"""
Logic for the compilation step of comptime.
"""

import contextlib
import os
import sys
import textwrap
import typing
from pathlib import Path

import black
import black.mode
from redbaron import RedBaron, Node, DecoratorNode

from .core import ENV_KEY
from .types import DynamicTuple, Registration, ResultsDictType

# Can contain custom black options.
#     Kept as default for now.
BlackMode = black.mode.Mode()


def extract_module_details(file_path: str, absolute: bool = None) -> tuple[str, str, str | None]:
    """
    Get the required info to run the script.

    This info is:
    - code (as string)
    - file/module name
    - possibly package name (if relative imports are used)
    """
    contents = Path(file_path).read_text()
    directory, file_name = os.path.split(file_path)
    module_name, _ = os.path.splitext(file_name)

    if absolute or not os.path.exists(os.path.join(directory, "__init__.py")):
        package_name = None
        full_module_name = module_name

        sys.path.insert(0, directory)
    else:
        # Determine the package name based on the directory structure
        package_name = os.path.basename(directory)
        full_module_name = f"{package_name}.{module_name}"

    return contents, full_module_name, package_name


@contextlib.contextmanager
def comptime_env() -> typing.Generator[None, None, None]:
    """
    Context manager to set the comptime environment variable to 1 for the scope of the with statement.

    Used by comptime.skip to determine which functions not to execute.

    Example:
        with comptime_env():
            exec("...") # some code that uses comptime.skip
    """
    os.environ[ENV_KEY] = "1"
    yield
    os.environ[ENV_KEY] = "0"


def precompute(contents: str, full_module_name: str, package_name: str = None) -> ResultsDictType:
    """
    Run the input code to get the output values for each comptime function.
    """
    registrations: dict[str, Registration] = {}
    scope = {"__name__": full_module_name, "__package__": package_name, "COMPTIME_REGISTRATIONS": registrations}

    with comptime_env():
        exec(contents, scope)  # nosec: B102
        exec(  # nosec: B102
            textwrap.dedent(
                """
            from comptime import comptime

            COMPTIME_REGISTRATIONS.clear()
            COMPTIME_REGISTRATIONS.update(comptime.get_registrations())
            """
            ),
            scope,
        )

    results: ResultsDictType = {}

    def run_combinations(args: DynamicTuple[typing.Any], current_combination: list[typing.Any] = []) -> None:
        # current_combination is mutable on purpose!
        if not args:
            results[(registration.name, tuple(current_combination))] = registration.func(*current_combination)
            return

        first_arg = args[0]
        remaining_args = args[1:]

        # If the first argument is a tuple, iterate through it, otherwise use it as a list with a single element
        first_combinations = first_arg if isinstance(first_arg, tuple) else [first_arg]

        for comb in first_combinations:
            run_combinations(remaining_args, [*current_combination, comb])

    def process_args(args: DynamicTuple[typing.Any]) -> None:
        # If all the elements in args are not tuples, call some_function for each of them individually
        if all(not isinstance(arg, tuple) for arg in args):
            # basic case of @comptime('option1', 'option2')
            for arg in args:
                results[(name, arg)] = registration.func(arg)
        else:
            # advanced case of @comptime(('arg1_option1', 'arg1_option2'), ('arg2_option1', 'arg2_option2'))
            run_combinations(args)

    for name, registration in registrations.items():
        if args := registration.args:
            process_args(args)
        else:
            result = registration.func()
            results[name] = result

    return results


class TransformComptimeRedBaron:
    """
    RedBaron-based code manipulator.
    """

    def __init__(self, code, replacements):
        self.red = RedBaron(code)
        self.replacements = replacements

    def has_comptime_decorator(self, func_node: Node) -> bool:
        return any("comptime" in decorator.dumps() for decorator in func_node.decorators)

    def is_comptime_import(self, node) -> bool:
        if node.type == "import" and any(
            alias.startswith("comptime.") or alias == "comptime" for alias in node.names()
        ):
            return True
        elif node.type == "from_import" and node.value[0].value == "comptime":
            return True
        return False

    def remove_comptime_decorators(self, node: Node):
        # Remove the @comptime decorator(s) if present
        decos: list[DecoratorNode] = node.decorators

        for decorator in decos:
            if str(decorator.name) == "comptime":
                decos.remove(decorator)

    def remove_node(self, node):
        index = node.index_on_parent
        self.red.node_list.remove(node)
        # Remove preceding newline if it exists
        if index > 0 and self.red.node_list[index - 1].type == "endl":
            self.red.node_list.remove(self.red.node_list[index - 1])
        # Remove succeeding newline if it exists
        elif index < len(self.red.node_list) and self.red.node_list[index].type == "endl":
            self.red.node_list.remove(self.red.node_list[index])

    def add_typing_import(self):
        red = self.red
        # Check if "import typing" is already present
        import_typing_exists = any(
            isinstance(node, RedBaron) and node.dumps() == "import typing" for node in red.find_all("ImportNode")
        )

        # If not present, add it at the start of the imports
        if not import_typing_exists:
            if docstring := red.find("StringNode", recursive=False):
                position = docstring.index_on_parent + 1
            else:
                position = 0

            if imports := red.find_all("ImportNode", recursive=False):
                position = imports[0].index_on_parent

            red.insert(position, "import typing")

    def walk_nodelist(self):
        nodes_to_remove = []
        for node in self.red.node_list:
            if self.is_comptime_import(node):
                nodes_to_remove.append(node)
            elif node.type in ["def", "async_def"]:
                self.remove_comptime_decorators(node)

        for node in nodes_to_remove:
            self.remove_node(node)

    def transform_functions(self):
        for func_node in self.red.find_all("DefNode"):
            if not self.has_comptime_decorator(func_node):
                continue
            function_name = func_node.name
            if function_name in self.replacements:
                # Replace the function content as per your logic
                # You can make use of self.replacements[function_name]
                pass
            # Extend with other transformations...


def transform_code(code, replacements):
    transformer = TransformComptimeRedBaron(code, replacements)

    transformer.add_typing_import()
    transformer.walk_nodelist()
    transformer.transform_functions()

    return transformer.red.dumps()


def do_compilation(file: str | Path, has_absolute_imports: bool = None, with_black: bool = True) -> str:
    """
    Execute @comptime code and replace the functions with its output.
    """
    file = str(file)

    module_details = extract_module_details(file, has_absolute_imports)
    results = precompute(*module_details)
    code = module_details[0]
    new_code = transform_code(code, results)
    if with_black:
        new_code = black.format_str(new_code, mode=BlackMode)
    return new_code


def write(file: str | Path, has_absolute_imports: bool = None, output: str = None, with_black: bool = True) -> None:
    """
    Compile `file` and write the outputs to `output`, or myfile.py -> myfile_compiled.py.
    """
    new_code = do_compilation(file, has_absolute_imports=has_absolute_imports, with_black=with_black)
    if output is None:
        output = str(file).replace(".py", "_compiled.py")
    with Path(output).open("w") as f:
        print(new_code, file=f)

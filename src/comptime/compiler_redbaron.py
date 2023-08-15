"""
Logic for the compilation step of comptime.
"""

import contextlib
import os
import sys
import textwrap
import typing
from pathlib import Path
from xml.dom.minicompat import NodeList

import black
import black.mode
from redbaron import RedBaron, Node, DecoratorNode, StringNode

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

    def get_docstring(self, function_def: Node) -> Node | None:
        """
        Get the docstring (object) of a function node.
        """
        if function_def.value:
            # Check if the first statement is a string (which would be the docstring)
            first_stmt = function_def.value[0]
            if isinstance(first_stmt, StringNode):
                return first_stmt
        return None

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

    def _add_fallback_case(self, arg_names: list[str], cases: RedBaron) -> None:
        args_fstring_elements = []

        for arg_name in arg_names:
            # Append formatted string elements
            args_fstring_elements.append(RedBaron(f"'{arg_name}='"))
            args_fstring_elements.append(RedBaron(f"FormattedValue(Name('{arg_name}'))"))
            args_fstring_elements.append(RedBaron("' '"))

        # Removing the trailing space
        del args_fstring_elements[-1]

        # Construct the error message
        error_message = f"JoinedStr(['Uncompiled variant ', {' + '.join([elem.dumps() for elem in args_fstring_elements])}])"

        # Construct the fallback match case
        fallback_case = RedBaron(f"""match_case(pattern=MatchAs(name=None), body=[
            Raise(exc=Call(func=Name("ValueError"), args=[{error_message}]))
        ])""")

        cases.append(fallback_case)

    def _build_match_cases(self, function_name: str, arg_names: list[str]):
        literals_map = {arg_name: set() for arg_name in arg_names}
        cases = []

        for key, value in self.replacements.items():
            if isinstance(key, tuple) and key[0] == function_name:
                if isinstance(key[1], tuple):
                    for idx, literal_value in enumerate(key[1]):
                        literals_map[arg_names[idx]].add(literal_value)
                else:
                    literals_map[arg_names[0]].add(key[1])

                # Building the patterns
                patterns = (
                    [f"MatchValue(value=Constant(value={literal}))" for literal in key[1]]
                    if isinstance(key[1], tuple)
                    else [f"MatchValue(value=Constant(value={key[1]}))"]
                )

                pattern_string = (
                    f"Tuple(elts={patterns}, ctx=Load())" if len(patterns) > 1 else patterns[0]
                )

                # Create nodes using RedBaron
                pattern_node = RedBaron(pattern_string)[0]
                return_stmt_node = RedBaron(f"Return(value=Constant(value={value}))")[0]

                match_case_node = RedBaron("case _:\n    pass")[0]  # This is a simple way to get a match_case node
                match_case_node.pattern = pattern_node  # Assuming pattern is already a redbaron node or a proper string
                match_case_node.body = NodeList([return_stmt_node])

                cases.append(match_case_node)

        # Add the default match case
        self._add_fallback_case(arg_names, cases)
        return cases, literals_map

    def _generate_comptime_match_cases_and_annotations(self, arg_names: list[str], function_name: str, node: Node):
        cases, literals = self._build_match_cases(function_name, arg_names)
        self._build_argument_annotations(node, arg_names, literals)

    def transform_functions(self):
        for func_node in self.red.find_all("DefNode"):
            if not self.has_comptime_decorator(func_node):
                continue

            if docstring_node := self.get_docstring(func_node):
                # Remove the docstring node from the function body to preserve it
                docstring_node_index = func_node.value.index(docstring_node)
                del func_node.value[docstring_node_index]

            function_name = func_node.name
            arg_names = [arg.target.value for arg in func_node.arguments]

            # If function name matches some criteria:
            # The actual criteria aren't provided, so this is just a placeholder
            if any(isinstance(key, tuple) and key[0] == function_name for key in self.replacements):
                # Logic for self._generate_comptime_match_cases_and_annotations goes here
                self._generate_comptime_match_cases_and_annotations(arg_names, function_name, func_node)
            else:
                # Replace the body with a return statement from the replacements dict
                # Note: This assumes that replacements is a dictionary where the key is a function name and the value is what you wish to return
                return_value = self.replacements.get(function_name, None) # todo: return None should be possible!
                if return_value is not None:
                    return_stmt = RedBaron(f'return {return_value}')[0]
                    del func_node.value[:]  # clear old body
                    func_node.value.insert(0, return_stmt)

            # Add back the docstring if it was present
            if docstring_node:
                func_node.value.insert(0, docstring_node)


def transform_code(code, replacements):
    transformer = TransformComptimeRedBaron(code, replacements)

    transformer.transform_functions()
    transformer.add_typing_import()
    transformer.walk_nodelist()

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

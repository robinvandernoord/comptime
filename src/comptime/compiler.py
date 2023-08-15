"""
Logic for the compilation step of comptime.
"""

import ast
import contextlib
import os
import sys
import textwrap
import typing
from ast import NodeTransformer, fix_missing_locations
from ast_comments import parse, unparse
from pathlib import Path

import black
import black.mode

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


Node: typing.TypeAlias = ast.AST

Strategy = typing.Literal["match", "dict"]
# DEFAULT_STRATEGY = "match"
DEFAULT_STRATEGY = "dict"


class TransformComptime(NodeTransformer):
    """
    AST manipulator.
    """

    replacements: ResultsDictType

    def __init__(self, replacements: ResultsDictType, strategy: Strategy = DEFAULT_STRATEGY) -> None:
        """
        Store the possible replacements for easier access.
        """
        self.replacements = replacements
        self.strategy = strategy

    def check_comptime_decorator(self, node: ast.FunctionDef) -> bool:
        """
        Check if a function has @comptime.

        If it does, remove it.
        Returns whether it did.
        """
        has_comptime_decorator = any(
            (isinstance(deco, ast.Call) and getattr(deco.func, "id", "") == "comptime")
            or (isinstance(deco, ast.Name) and deco.id == "comptime")
            for deco in node.decorator_list
        )

        # Remove the @comptime decorator(s) if present
        node.decorator_list = [
            deco
            for deco in node.decorator_list
            if not (
                # Check for @comptime
                (isinstance(deco, ast.Name) and deco.id == "comptime")
                or
                # Check for @comptime.*
                (isinstance(deco, ast.Attribute) and getattr(deco.value, "id", "") == "comptime")
                or
                # Check for @comptime() or @comptime.*()
                (
                    isinstance(deco, ast.Call)
                    and (
                        getattr(deco.func, "id", "") == "comptime"
                        or (isinstance(deco.func, ast.Attribute) and getattr(deco.func.value, "id", "") == "comptime")
                    )
                )
            )
        ]
        return has_comptime_decorator

    def get_docstring(self, node: ast.FunctionDef) -> ast.Expr | None:
        """
        Get the docstring (object) of a function node.
        """
        first_expr = typing.cast(ast.Expr, node.body[0])  # it probably is and we check it afterwards:
        if isinstance(first_expr, ast.Expr) and isinstance(first_expr.value, ast.Str):
            return first_expr
        return None

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        """
        Check each function and replace its contents if it has the @comptime decorator.
        """
        # Check if the function has the @comptime decorator
        has_comptime_decorator = self.check_comptime_decorator(node)

        # If the function does not have the @comptime decorator, do not modify it
        if not has_comptime_decorator:
            return node

        # Preserve the docstring if it exists
        docstring_node = self.get_docstring(node)

        function_name = node.name
        arg_names = [arg.arg for arg in node.args.args]

        if any(isinstance(key, tuple) and key[0] == function_name for key in self.replacements):
            # todo: maybe fallback to original code if nothing found, unless specified in args by user?

            if self.strategy == "match":
                self._generate_comptime_match_cases_and_annotations(arg_names, function_name, node)
            elif self.strategy == "dict":
                self._generate_comptime_lookup_return(arg_names, function_name, node)
            else:
                raise ValueError(f"Invalid strategy '{self.strategy}'.")
        else:
            # If the function does not have arguments, simply replace its body with the return statement
            node.body = [ast.Return(value=ast.Constant(self.replacements[function_name]))]

        # Add back the docstring if it was present
        if docstring_node:
            node.body.insert(0, docstring_node)
        return node

    def _generate_comptime_match_cases_and_annotations(
        self, arg_names: list[str], function_name: str, node: ast.FunctionDef
    ) -> None:
        cases, literals = self._build_match_cases(function_name, arg_names)
        self._build_argument_annotations(node, arg_names, literals)

        # Replacing the body with the match block
        match_subjects = [ast.Name(arg_name, ast.Load()) for arg_name in arg_names]
        node.body = [
            ast.Match(
                subject=ast.Tuple(elts=match_subjects, ctx=ast.Load())
                if len(match_subjects) > 1
                else match_subjects[0],
                cases=cases,
            )
        ]

    def _generate_comptime_lookup_return(
        self, arg_names: list[str], function_name: str, node: ast.FunctionDef
    ) -> None:
        lookup_dict, literals = self._build_lookup_dict(function_name, arg_names)
        self._build_argument_annotations(node, arg_names, literals)

        # Convert lookup_dict to an ast.Dict object
        dict_keys = [ast.Tuple(elts=[ast.Constant(value=k) for k in key], ctx=ast.Load()) if isinstance(key,
                                                                                                        tuple) else ast.Constant(
            value=key) for key in lookup_dict.keys()]
        dict_values = [ast.Constant(value=v) for v in lookup_dict.values()]
        ast_lookup_dict = ast.Dict(keys=dict_keys, values=dict_values)

        # Using dictionary lookup to replace the body
        keys = [ast.Name(arg_name, ast.Load()) for arg_name in arg_names]
        lookup_key = ast.Tuple(elts=keys, ctx=ast.Load()) if len(keys) > 1 else keys[0]

        lookup_expression = ast.Subscript(
            value=ast_lookup_dict,
            slice=ast.Index(value=lookup_key),
            ctx=ast.Load(),
        )

        node.body = [
            ast.Return(value=lookup_expression)
        ]

    def _build_argument_annotations(
        self, node: ast.FunctionDef, arg_names: list[str], literals_map: dict[str, set[typing.Any]]
    ) -> None:
        for idx, arg_name in enumerate(arg_names):
            literals = [ast.Constant(value=literal) for literal in literals_map[arg_name]]
            if set(literals_map[arg_name]) == {True, False}:
                node.args.args[idx].annotation = ast.Name("bool", ast.Load())
            else:
                node.args.args[idx].annotation = ast.Subscript(
                    value=ast.Name("typing.Literal", ast.Load()),
                    slice=ast.Index(value=ast.Tuple(elts=literals, ctx=ast.Load())),
                    ctx=ast.Load(),
                )

    def _build_match_cases(
        self, function_name: str, arg_names: list[str]
    ) -> tuple[list[ast.match_case], dict[str, set[typing.Any]]]:
        literals_map: dict[str, set[typing.Any]] = {arg_name: set() for arg_name in arg_names}
        cases = []
        for key, value in self.replacements.items():
            if isinstance(key, tuple) and key[0] == function_name:
                if isinstance(key[1], tuple):
                    for idx, literal_value in enumerate(key[1]):
                        literals_map[arg_names[idx]].add(literal_value)
                else:
                    literals_map[arg_names[0]].add(key[1])

                # Adding the match cases
                patterns = (
                    [ast.MatchValue(value=ast.Constant(value=literal)) for literal in key[1]]
                    if isinstance(key[1], tuple)
                    else [ast.MatchValue(value=ast.Constant(value=key[1]))]
                )

                pattern: ast.MatchValue | ast.Tuple = (
                    ast.Tuple(elts=patterns, ctx=ast.Load()) if len(patterns) > 1 else patterns[0]
                )

                cases.append(ast.match_case(pattern=pattern, body=[ast.Return(value=ast.Constant(value))]))

        # Adding the default match case
        self._add_fallback_case(arg_names, cases)
        return cases, literals_map

    def _add_fallback_case(self, arg_names: list[str], cases: list[ast.match_case]) -> None:
        args_fstring_elements: list[ast.Str | ast.FormattedValue] = []
        for arg_name in arg_names:
            args_fstring_elements.extend(
                (
                    ast.Str(f"{arg_name}="),
                    ast.FormattedValue(
                        value=ast.Name(arg_name, ast.Load()),
                        conversion=-1,
                        format_spec=None,
                    ),
                    ast.Str(" "),
                )
            )
        # Removing the trailing space
        args_fstring_elements = args_fstring_elements[:-1]
        error_message = ast.JoinedStr(values=[ast.Str("Uncompiled variant "), *args_fstring_elements])
        cases.append(
            ast.match_case(
                pattern=ast.MatchAs(name=None),
                body=[
                    ast.Raise(exc=ast.Call(func=ast.Name("ValueError", ast.Load()), args=[error_message], keywords=[]))
                ],
            )
        )

    def _build_lookup_dict(
        self, function_name: str, arg_names: list[str]
    ) -> dict[str, set[typing.Any]]:
        literals_map: dict[str, set[typing.Any]] = {arg_name: set() for arg_name in arg_names}
        lookup_dict = {}

        for key, value in self.replacements.items():
            if isinstance(key, tuple) and key[0] == function_name:
                literals = key[1] if isinstance(key[1], tuple) else (key[1],)
                for idx, literal_value in enumerate(literals):
                    literals_map[arg_names[idx]].add(literal_value)

                # Populating the lookup dictionary
                lookup_key = tuple(literals) if len(literals) > 1 else literals[0]
                lookup_dict[lookup_key] = value

        return lookup_dict, literals_map

    def visit_Import(self, node: ast.Import) -> ast.Import | None:
        """
        Remove the import statement if it imports comptime.
        """
        if any(alias.name == "comptime" for alias in node.names):
            return None
        return node

    def visit_ImportFrom(self, node: ast.ImportFrom) -> ast.ImportFrom | None:
        """
        Remove the from import statement if it imports comptime.
        """
        if node.module == "comptime":
            return None
        return node


def transform_code(code: str, replacements: ResultsDictType, strategy: Strategy = DEFAULT_STRATEGY) -> str:
    """
    Given the orginal code and output of comptime functions, inline the results.
    """
    tree = parse(code)
    transformer = TransformComptime(replacements, strategy=strategy)
    new_tree = fix_missing_locations(transformer.visit(tree))

    # Adding the typing import if not already present
    for stmt in new_tree.body:
        if isinstance(stmt, ast.Import) and any(alias.name == "typing" for alias in stmt.names):
            break
    else:
        new_tree.body.insert(0, ast.Import(names=[ast.alias(name="typing", asname=None)]))

    return unparse(new_tree)


def do_compilation(file: str | Path, has_absolute_imports: bool = None, with_black: bool = True,
                   strategy: Strategy = DEFAULT_STRATEGY) -> str:
    """
    Execute @comptime code and replace the functions with its output.
    """
    file = str(file)

    module_details = extract_module_details(file, has_absolute_imports)
    results = precompute(*module_details)
    code = module_details[0]
    new_code = transform_code(code, results, strategy=strategy)
    if with_black:
        new_code = black.format_str(new_code, mode=BlackMode)
    return new_code


def write(file: str | Path, has_absolute_imports: bool = None, output: str | Path = None, with_black: bool = True,
          strategy: Strategy = DEFAULT_STRATEGY) -> None:
    """
    Compile `file` and write the outputs to `output`, or myfile.py -> myfile_compiled.py.
    """
    new_code = do_compilation(file, has_absolute_imports=has_absolute_imports, with_black=with_black, strategy=strategy)
    if output is None:
        output = str(file).replace(".py", "_compiled.py")
    with Path(output).open("w") as f:
        print(new_code, file=f)

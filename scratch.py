from pathlib import Path
import sys
import textwrap
import os
import ast
from ast import parse, NodeTransformer, fix_missing_locations


def extract_module_details(file_path: str, absolute: bool = None):
    contents = Path(file_path).read_text()
    directory, file_name = os.path.split(file_path)
    module_name, _ = os.path.splitext(file_name)

    if absolute or not os.path.exists(
        os.path.join(directory, '__init__.py')
    ):
        package_name = None
        full_module_name = module_name

        sys.path.insert(0, directory)
    else:
        # Determine the package name based on the directory structure
        package_name = os.path.basename(directory)
        full_module_name = f'{package_name}.{module_name}'

    return contents, full_module_name, package_name


def precompute(contents: str, full_module_name: str, package_name: str = None):
    registrations = {}
    scope = {
        '__name__': full_module_name,
        '__package__': package_name,
        "COMPTIME_REGISTRATIONS": registrations
    }
    exec(contents, scope)
    exec(textwrap.dedent("""
    from comptime import comptime

    COMPTIME_REGISTRATIONS.clear() 
    COMPTIME_REGISTRATIONS.update(comptime.get_registrations()) 
    """), scope)

    results = {}

    def run_combinations(args, current_combination=[]):
        if not args:
            results[(registration.name, tuple(current_combination))] = registration.func(*current_combination)
            return

        first_arg = args[0]
        remaining_args = args[1:]

        # If the first argument is a tuple, iterate through it, otherwise use it as a list with a single element
        first_combinations = first_arg if isinstance(first_arg, tuple) else [first_arg]

        for comb in first_combinations:
            run_combinations(remaining_args, current_combination + [comb])

    def process_args(args):
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


class TransformComptime(NodeTransformer):
    def __init__(self, replacements):
        self.replacements = replacements

    def visit_FunctionDef(self, node):
        # Check if the function has the @comptime decorator
        has_comptime_decorator = any(
            (isinstance(deco, ast.Call) and getattr(deco.func, 'id', '') == 'comptime') or
            (isinstance(deco, ast.Name) and deco.id == 'comptime')
            for deco in node.decorator_list
        )

        # Remove the @comptime decorator if present
        node.decorator_list = [
            deco for deco in node.decorator_list if not (
                (isinstance(deco, ast.Call) and getattr(deco.func, 'id', '') == 'comptime') or
                (isinstance(deco, ast.Name) and deco.id == 'comptime')
            )
        ]

        # If the function does not have the @comptime decorator, do not modify it
        if not has_comptime_decorator:
            return node

        # Preserve the docstring if it exists
        docstring_node = None
        if isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Str):
            docstring_node = node.body[0]

        function_name = node.name
        arg_names = [arg.arg for arg in node.args.args]

        if any(isinstance(key, tuple) and key[0] == function_name for key in self.replacements.keys()):
            literals = []
            cases = []
            for key, value in self.replacements.items():
                if isinstance(key, tuple) and key[0] == function_name:
                    literals.append(ast.Constant(value=key[1]))
                    cases.append(ast.match_case(
                        pattern=ast.MatchValue(value=ast.Constant(value=key[1])),
                        body=[ast.Return(value=ast.Constant(value))]
                    ))

            # Update the first argument's annotation in the function signature
            node.args.args[0].annotation = ast.Subscript(
                value=ast.Name('typing', ast.Load()),
                slice=ast.Index(value=ast.Tuple(elts=literals, ctx=ast.Load())),
                ctx=ast.Load()
            )

            # Adding the default match case
            args_string = ', '.join(arg_names) if len(arg_names) > 1 else arg_names[0]
            error_message = ast.JoinedStr(
                values=[
                    ast.Str(f"Uncompiled variant {args_string}")
                ]
            )

            cases.append(ast.match_case(
                pattern=ast.MatchAs(name=None),
                body=[ast.Raise(exc=ast.Call(
                    func=ast.Name('ValueError', ast.Load()),
                    args=[error_message],
                    keywords=[]
                ))]
            ))

            # Replacing the body with the match block
            new_body = [ast.Match(
                subject=ast.Name(arg_names[0], ast.Load()),
                cases=cases
            )]

            # Add back the docstring if it was present
            if docstring_node:
                new_body.insert(0, docstring_node)

            node.body = new_body
        else:
            # If the function does not have arguments, simply replace its body with the return statement
            node.body = [ast.Return(value=ast.Constant(self.replacements[function_name]))]

            # Add back the docstring if it was present
            if docstring_node:
                node.body.insert(0, docstring_node)

        return node

    # def visit_FunctionDef(self, node):
    #     # Check if the function has the @comptime decorator
    #     has_comptime_decorator = any(
    #         (isinstance(deco, ast.Call) and getattr(deco.func, 'id', '') == 'comptime') or
    #         (isinstance(deco, ast.Name) and deco.id == 'comptime')
    #         for deco in node.decorator_list
    #     )
    #
    #     # Remove the @comptime decorator if present
    #     node.decorator_list = [
    #         deco for deco in node.decorator_list if not (
    #             (isinstance(deco, ast.Call) and getattr(deco.func, 'id', '') == 'comptime') or
    #             (isinstance(deco, ast.Name) and deco.id == 'comptime')
    #         )
    #     ]
    #
    #     # If the function does not have the @comptime decorator, do not modify it
    #     if not has_comptime_decorator:
    #         return node
    #
    #     function_name = node.name
    #     arg_names = [arg.arg for arg in node.args.args]
    #
    #     if any(isinstance(key, tuple) and key[0] == function_name for key in self.replacements.keys()):
    #         literals = []
    #         cases = []
    #         for key, value in self.replacements.items():
    #             if isinstance(key, tuple) and key[0] == function_name:
    #                 literals.append(ast.Constant(value=key[1]))
    #                 cases.append(ast.match_case(
    #                     pattern=ast.MatchValue(value=ast.Constant(value=key[1])),
    #                     body=[ast.Return(value=ast.Constant(value))]
    #                 ))
    #
    #         # Update the first argument's annotation in the function signature
    #         node.args.args[0].annotation = ast.Subscript(
    #             value=ast.Name('typing', ast.Load()),
    #             slice=ast.Index(value=ast.Tuple(elts=literals, ctx=ast.Load())),
    #             ctx=ast.Load()
    #         )
    #
    #         # Adding the default match case
    #         cases.append(ast.match_case(
    #             pattern=ast.MatchAs(name=None),
    #             body=[ast.Raise(exc=ast.Call(
    #                 func=ast.Name('ValueError', ast.Load()),
    #                 args=[ast.Str('Uncompiled variant {endpoint}')],
    #                 keywords=[]
    #             ))]
    #         ))
    #
    #         # Replacing the body with the match block
    #         node.body = [ast.Match(
    #             subject=ast.Name(arg_names[0], ast.Load()),
    #             cases=cases
    #         )]
    #     else:
    #         # If the function does not have arguments, simply replace its body with the return statement
    #         node.body = [ast.Return(value=ast.Constant(self.replacements[function_name]))]
    #
    #     return node

    # def visit_FunctionDef(self, node):
    #     # Check if the function has the @comptime decorator
    #     has_comptime_decorator = any(
    #         (isinstance(deco, ast.Call) and getattr(deco.func, 'id', '') == 'comptime') or
    #         (isinstance(deco, ast.Name) and deco.id == 'comptime')
    #         for deco in node.decorator_list
    #     )
    #
    #     # Remove the @comptime decorator if present
    #     node.decorator_list = [
    #         deco for deco in node.decorator_list if not (
    #             (isinstance(deco, ast.Call) and getattr(deco.func, 'id', '') == 'comptime') or
    #             (isinstance(deco, ast.Name) and deco.id == 'comptime')
    #         )
    #     ]
    #
    #     # If the function does not have the @comptime decorator, do not modify it
    #     if not has_comptime_decorator:
    #         return node
    #
    #     function_name = node.name
    #     arg_names = [arg.arg for arg in node.args.args]
    #
    #     if any(isinstance(key, tuple) and key[0] == function_name for key in self.replacements.keys()):
    #         cases = []
    #         literals = []
    #         for key, value in self.replacements.items():
    #             if isinstance(key, tuple) and key[0] == function_name:
    #                 literals.append(ast.Str(s=key[1]))
    #                 cases.append(ast.match_case(
    #                     pattern=ast.MatchValue(value=ast.Str(key[1])),
    #                     body=[ast.Return(value=ast.Constant(value))]
    #                 ))
    #
    #         cases.append(ast.match_case(
    #             pattern=ast.MatchAs(name=None),
    #             body=[ast.Raise(exc=ast.Call(
    #                 func=ast.Name('ValueError', ast.Load()),
    #                 args=[ast.Str('Uncompiled variant {endpoint}')],
    #                 keywords=[]
    #             ))]
    #         ))
    #
    #         node.body = [
    #             ast.AnnAssign(
    #                 target=ast.Name(arg_names[0], ast.Store()),
    #                 annotation=ast.Subscript(
    #                     value=ast.Name('typing', ast.Load()),
    #                     slice=ast.Index(value=ast.Tuple(elts=literals, ctx=ast.Load())),
    #                     ctx=ast.Load()
    #                 ),
    #                 value=None,
    #                 simple=1
    #             ),
    #             ast.Match(
    #                 subject=ast.Name(arg_names[0], ast.Load()),
    #                 cases=cases
    #             )
    #         ]
    #     else:
    #         node.body = [ast.Return(value=ast.Constant(self.replacements[function_name]))]
    #
    #     return node

    # def visit_FunctionDef(self, node):
    #     for deco in node.decorator_list:
    #         if isinstance(deco, ast.Call) and getattr(deco.func, 'id', '') == 'comptime':
    #             function_name = node.name
    #             arg_names = [arg.arg for arg in node.args.args]
    #
    #             if any(isinstance(key, tuple) and key[0] == function_name for key in self.replacements.keys()):
    #                 cases = []
    #                 literals = []
    #                 for key, value in self.replacements.items():
    #                     if isinstance(key, tuple) and key[0] == function_name:
    #                         literals.append(ast.Str(s=key[1]))
    #                         cases.append(ast.match_case(
    #                             pattern=ast.MatchValue(value=ast.Str(key[1])),
    #                             body=[ast.Return(value=ast.Constant(value))]
    #                         ))
    #
    #                 cases.append(ast.match_case(
    #                     pattern=ast.MatchAs(name=None),
    #                     body=[ast.Raise(exc=ast.Call(
    #                         func=ast.Name('ValueError', ast.Load()),
    #                         args=[ast.Str('Uncompiled variant {endpoint}')],
    #                         keywords=[]
    #                     ))]
    #                 ))
    #
    #                 node.body = [
    #                     ast.AnnAssign(
    #                         target=ast.Name(arg_names[0], ast.Store()),
    #                         annotation=ast.Subscript(
    #                             value=ast.Name('typing', ast.Load()),
    #                             slice=ast.Index(value=ast.Tuple(elts=literals, ctx=ast.Load())),
    #                             ctx=ast.Load()
    #                         ),
    #                         value=None,
    #                         simple=1
    #                     ),
    #                     ast.Match(
    #                         subject=ast.Name(arg_names[0], ast.Load()),
    #                         cases=cases
    #                     )
    #                 ]
    #             else:
    #                 node.body = [ast.Return(value=ast.Constant(self.replacements[function_name]))]
    #
    #     return node

    def visit_Import(self, node):
        # Remove the import statement if it imports comptime
        if any(alias.name == 'comptime' for alias in node.names):
            return None
        return node

    def visit_ImportFrom(self, node):
        # Remove the from import statement if it imports comptime
        if node.module == 'comptime':
            return None
        return node


def transform_code(code, replacements):
    tree = parse(code)
    transformer = TransformComptime(replacements)
    new_tree = fix_missing_locations(transformer.visit(tree))

    # Adding the typing import if not already present
    for stmt in new_tree.body:
        if isinstance(stmt, ast.Import) and any(alias.name == 'typing' for alias in stmt.names):
            break
    else:
        new_tree.body.insert(0, ast.Import(names=[ast.alias(name='typing', asname=None)]))

    return ast.unparse(new_tree)


def main(file_path, has_absolute_imports=None):
    module_details = extract_module_details(file_path, has_absolute_imports)
    results = precompute(*module_details)
    code = module_details[0]

    print(results)
    new_code = transform_code(code, results)
    print(new_code)


if __name__ == '__main__':
    base = Path(__file__).parent / "examples"

    main(str(base / "main.py"))
    main(str(base / "absolute.py"), has_absolute_imports=True)

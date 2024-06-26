from posthog.hogql import ast


def sparkline(node: ast.Expr, args: list[ast.Expr]) -> ast.Expr:
    return ast.Tuple(
        exprs=[
            ast.Constant(value="__hogql_chart_type"),
            ast.Constant(value="sparkline"),
            ast.Constant(value="results"),
            args[0],
        ]
    )

import ast
import operator

SCHEMA = {
    "type": "function",
    "function": {
        "name": "calculate",
        "description": "Evaluate a mathematical expression and return the numeric result.",
        "parameters": {
            "type": "object",
            "properties": {
                "expr": {
                    "type": "string",
                    "description": "A math expression, e.g. '45 * 3' or '(10 + 5) / 2'",
                }
            },
            "required": ["expr"],
        },
    },
}

_OPS = {
    ast.Add:      operator.add,
    ast.Sub:      operator.sub,
    ast.Mult:     operator.mul,
    ast.Div:      operator.truediv,
    ast.Pow:      operator.pow,
    ast.Mod:      operator.mod,
    ast.FloorDiv: operator.floordiv,
    ast.USub:     operator.neg,
    ast.UAdd:     operator.pos,
}


def _eval(node):
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f"Unsupported constant: {node.value!r}")
    if isinstance(node, ast.BinOp):
        op = _OPS.get(type(node.op))
        if op is None:
            raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
        return op(_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp):
        op = _OPS.get(type(node.op))
        if op is None:
            raise ValueError(f"Unsupported unary operator: {type(node.op).__name__}")
        return op(_eval(node.operand))
    raise ValueError(f"Unsupported expression node: {type(node).__name__}")


def calculate(expr: str) -> str:
    try:
        tree = ast.parse(expr.strip(), mode="eval")
        result = _eval(tree.body)
        if isinstance(result, float) and result.is_integer():
            return str(int(result))
        return str(round(result, 10))
    except Exception as e:
        return f"Error: {e}"

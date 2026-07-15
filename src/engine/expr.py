def evaluate_expr(expr, scope):
    if expr is None:
        return None
    result = evaluate_term(expr.op, scope)
    for op, term in zip(expr.op0, expr.op1):
        val = evaluate_term(term, scope)
        result = result + val if op == '+' else result - val
    return result


def evaluate_term(term, scope):
    result = evaluate_factor(term.op, scope)
    for op, factor in zip(term.op0, term.op1):
        val = evaluate_factor(factor, scope)
        if op == '*':
            result = result * val
        else:
            if val == 0:
                raise RuntimeError("Division by zero in expression")
            result = result / val
    return result


def evaluate_factor(factor, scope):
    if isinstance(factor, int):
        return factor
    if isinstance(factor, str):
        if factor not in scope:
            raise RuntimeError(f"Undefined variable: '{factor}'")
        return scope[factor]
    return evaluate_expr(factor, scope)
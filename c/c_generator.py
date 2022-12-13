from typing import List, cast
from checker import (
    CheckedAssign,
    CheckedAssignOperations,
    CheckedBinary,
    CheckedBinaryOperations,
    CheckedBool,
    CheckedBreak,
    CheckedCall,
    CheckedChar,
    CheckedExpr,
    CheckedExprStatement,
    CheckedExprTypes,
    CheckedFloat,
    CheckedFunc,
    CheckedId,
    CheckedIf,
    CheckedIndexing,
    CheckedInt,
    CheckedLet,
    CheckedReturn,
    CheckedStatement,
    CheckedStatementTypes,
    CheckedString,
    CheckedType,
    CheckedTypeTypes,
    CheckedWhile,
    GlobalTable,
    LocalTable,
)


def safeify_name(name: str) -> str:
    return name.replace("æ", "ae").replace("ø", "oe").replace("å", "aa")


def generate_c_code(
    top_level_statements: List[CheckedStatement], global_table: GlobalTable
) -> str:
    return generate_top_level_statements(top_level_statements, global_table)


def generate_top_level_statements(
    top_level_statements: List[CheckedStatement], global_table: GlobalTable
) -> str:
    acc = '#include "runtime.h"\n'
    for statement in top_level_statements:
        if statement.statement_type() == CheckedStatementTypes.Let:
            acc += generate_top_level_let(cast(CheckedLet, statement), global_table)
        elif statement.statement_type() == CheckedStatementTypes.Func:
            acc += generate_top_level_func(cast(CheckedFunc, statement), global_table)
    return acc


def generate_top_level_let(let: CheckedLet, global_table: GlobalTable) -> str:
    return f"const {generate_type(let.value_type, global_table)} {let.subject} = {generate_top_level_expr(let.value, global_table)};\n"


def generate_top_level_expr(node: CheckedExpr, global_table: GlobalTable) -> str:
    if node.expr_type() == CheckedExprTypes.Int:
        int_node = cast(CheckedInt, node)
        return str(int_node.value)
    else:
        raise NotImplementedError()


def generate_top_level_func(func: CheckedFunc, global_table: GlobalTable) -> str:
    acc = "\n"
    if func.subject == "begynd":
        acc += f"int main"
    else:
        subject = safeify_name(func.subject)
        acc += f"{generate_type(func.return_type, global_table)} {subject}"
    acc += f"("
    if len(func.params) > 0:
        acc += f"{generate_type(func.params[0].value_type, global_table)} {func.params[0].subject}"
        for param in func.params[1:]:
            acc += f", {generate_type(param.value_type, global_table)} {param.subject}"
    acc += ")\n{\n"
    acc += generate_statements(func.body, global_table.func_local_tables[func.subject])
    acc += "}\n"
    return acc


def generate_statements(
    statements: List[CheckedStatement], local_table: LocalTable
) -> str:
    acc = ""
    for statement in statements:
        if statement.statement_type() == CheckedStatementTypes.Expr:
            acc += f"{generate_expr_statement(cast(CheckedExprStatement, statement), local_table)}"
        elif statement.statement_type() == CheckedStatementTypes.Let:
            acc += f"{generate_let(cast(CheckedLet, statement), local_table)}"
        elif statement.statement_type() == CheckedStatementTypes.If:
            acc += f"{generate_if(cast(CheckedIf, statement), local_table)}"
        elif statement.statement_type() == CheckedStatementTypes.While:
            acc += f"{generate_while(cast(CheckedWhile, statement), local_table)}"
        elif statement.statement_type() == CheckedStatementTypes.Break:
            acc += f"{generate_break(cast(CheckedBreak, statement), local_table)}"
        elif statement.statement_type() == CheckedStatementTypes.Func:
            acc += f"{generate_func(cast(CheckedFunc, statement), local_table)}"
        elif statement.statement_type() == CheckedStatementTypes.Return:
            acc += f"{generate_return(cast(CheckedReturn, statement), local_table)}"
        else:
            raise NotImplementedError()
    return acc


def generate_expr_statement(
    statement: CheckedExprStatement, local_table: LocalTable
) -> str:
    return f"{generate_expr(statement.value, local_table)};\n"


def generate_let(statement: CheckedLet, local_table: LocalTable) -> str:
    return f"{generate_type(statement.value_type, local_table)} {safeify_name(statement.subject)} = {generate_expr(statement.value, local_table)};\n"


def generate_if(statement: CheckedIf, local_table: LocalTable) -> str:
    acc = "if ("
    acc += generate_expr(statement.condition, local_table)
    acc += ") {\n"
    acc += generate_statements(statement.truthy, local_table)
    acc += "}"
    if statement.falsy:
        acc += " else {\n"
        acc += generate_statements(statement.falsy, local_table)
        acc += "}"
    acc += "\n"
    return acc


def generate_while(statement: CheckedWhile, local_table: LocalTable) -> str:
    acc = "while ("
    acc += generate_expr(statement.condition, local_table)
    acc += ") {\n"
    acc += generate_statements(statement.body, local_table)
    acc += "}\n"
    return acc


def generate_break(statement: CheckedBreak, local_table: LocalTable) -> str:
    raise NotImplementedError()


def generate_func(statement: CheckedFunc, local_table: LocalTable) -> str:
    raise NotImplementedError()


def generate_return(statement: CheckedReturn, local_table: LocalTable) -> str:
    if statement.value:
        return f"return {generate_expr(statement.value, local_table)};\n"
    else:
        return "return;\n"


def generate_type(node: CheckedType, local_table) -> str:
    if node.type_type() == CheckedTypeTypes.Int:
        return "long"
    elif node.type_type() == CheckedTypeTypes.Float:
        return "double"
    elif node.type_type() == CheckedTypeTypes.Char:
        return "char"
    elif node.type_type() == CheckedTypeTypes.String:
        return "String*"
    elif node.type_type() == CheckedTypeTypes.Bool:
        return "bool"
    elif node.type_type() == CheckedTypeTypes.Array:
        return "Array*"
    elif node.type_type() == CheckedTypeTypes.Object:
        raise NotImplementedError()
    elif node.type_type() == CheckedTypeTypes.Func:
        raise NotImplementedError()
    else:
        raise Exception()


def generate_expr(node: CheckedExpr, local_table: LocalTable) -> str:
    if node.expr_type() == CheckedExprTypes.Id:
        return safeify_name(cast(CheckedId, node).value)
    elif node.expr_type() == CheckedExprTypes.Int:
        return str(cast(CheckedInt, node).value)
    elif node.expr_type() == CheckedExprTypes.Float:
        return str(cast(CheckedFloat, node).value)
    elif node.expr_type() == CheckedExprTypes.Char:
        return cast(CheckedChar, node).value
    elif node.expr_type() == CheckedExprTypes.String:
        return f"string_from({cast(CheckedString, node).value})"
    elif node.expr_type() == CheckedExprTypes.Bool:
        return "true" if cast(CheckedBool, node).value else "false"
    elif node.expr_type() == CheckedExprTypes.Array:
        return f"array_new()"
    elif node.expr_type() == CheckedExprTypes.Object:
        raise NotImplementedError()
    elif node.expr_type() == CheckedExprTypes.Accessing:
        raise NotImplementedError()
    elif node.expr_type() == CheckedExprTypes.Indexing:
        return generate_indexing(cast(CheckedIndexing, node), local_table)
    elif node.expr_type() == CheckedExprTypes.Call:
        return generate_call(cast(CheckedCall, node), local_table)
    elif node.expr_type() == CheckedExprTypes.Unary:
        raise NotImplementedError()
    elif node.expr_type() == CheckedExprTypes.Binary:
        return generate_binary(cast(CheckedBinary, node), local_table)
    elif node.expr_type() == CheckedExprTypes.Assign:
        return generate_assign(cast(CheckedAssign, node), local_table)
    else:
        raise NotImplementedError()


def generate_call(node: CheckedCall, local_table: LocalTable) -> str:
    subject = generate_expr(node.subject, local_table)
    args = ", ".join([generate_expr(arg, local_table) for arg in node.args])
    return f"{subject}({args})"


def generate_indexing(node: CheckedIndexing, local_table: LocalTable) -> str:
    if node.subject.expr_value_type().type_type() == CheckedTypeTypes.Array:
        return f"array_at({generate_expr(node.subject, local_table)}, {generate_expr(node.value, local_table)})"
    elif node.subject.expr_value_type().type_type() == CheckedTypeTypes.String:
        return f"string_at({generate_expr(node.subject, local_table)}, {generate_expr(node.value, local_table)})"
    else:
        raise Exception("type is not indexable")


def generate_binary(node: CheckedBinary, local_table: LocalTable) -> str:
    left = generate_expr(node.left, local_table)
    right = generate_expr(node.right, local_table)
    left_type = node.left.expr_value_type()
    right_type = node.right.expr_value_type()
    if left_type.type_type() == CheckedTypeTypes.Int:
        if right_type.type_type() == CheckedTypeTypes.Int:
            if node.operation == CheckedBinaryOperations.Add:
                return f"({left} + {right})"
            elif node.operation == CheckedBinaryOperations.Subtract:
                return f"({left} - {right})"
            elif node.operation == CheckedBinaryOperations.Multiply:
                return f"({left} * {right})"
            elif node.operation == CheckedBinaryOperations.EQ:
                return f"({left} == {right})"
            elif node.operation == CheckedBinaryOperations.NE:
                return f"({left} != {right})"
            elif node.operation == CheckedBinaryOperations.LT:
                return f"({left} < {right})"
            elif node.operation == CheckedBinaryOperations.LTE:
                return f"({left} <= {right})"
            elif node.operation == CheckedBinaryOperations.GT:
                return f"({left} > {right})"
            elif node.operation == CheckedBinaryOperations.GTE:
                return f"({left} >= {right})"
            else:
                raise NotImplementedError()
        else:
            raise NotImplementedError()
    elif left_type.type_type() == CheckedTypeTypes.Char:
        if right_type.type_type() == CheckedTypeTypes.Char:
            if node.operation == CheckedBinaryOperations.Add:
                return f"({left} + {right})"
            elif node.operation == CheckedBinaryOperations.Subtract:
                return f"({left} - {right})"
            elif node.operation == CheckedBinaryOperations.Multiply:
                return f"({left} * {right})"
            elif node.operation == CheckedBinaryOperations.EQ:
                return f"({left} == {right})"
            elif node.operation == CheckedBinaryOperations.NE:
                return f"({left} != {right})"
            elif node.operation == CheckedBinaryOperations.LT:
                return f"({left} < {right})"
            elif node.operation == CheckedBinaryOperations.LTE:
                return f"({left} <= {right})"
            elif node.operation == CheckedBinaryOperations.GT:
                return f"({left} > {right})"
            elif node.operation == CheckedBinaryOperations.GTE:
                return f"({left} >= {right})"
            else:
                raise NotImplementedError()
        else:
            raise NotImplementedError()
    elif left_type.type_type() == CheckedTypeTypes.Bool:
        if right_type.type_type() == CheckedTypeTypes.Bool:
            if node.operation == CheckedBinaryOperations.EQ:
                return f"({left} == {right})"
            elif node.operation == CheckedBinaryOperations.NE:
                return f"({left} != {right})"
            elif node.operation == CheckedBinaryOperations.LT:
                return f"({left} < {right})"
            elif node.operation == CheckedBinaryOperations.LTE:
                return f"({left} <= {right})"
            elif node.operation == CheckedBinaryOperations.GT:
                return f"({left} > {right})"
            elif node.operation == CheckedBinaryOperations.GTE:
                return f"({left} >= {right})"
            elif node.operation == CheckedBinaryOperations.And:
                return f"({left} && {right})"
            elif node.operation == CheckedBinaryOperations.Or:
                return f"({left} || {right})"
            else:
                raise NotImplementedError()
        else:
            raise NotImplementedError()
    else:
        raise NotImplementedError()


def generate_assign(node: CheckedAssign, local_table: LocalTable) -> str:
    subject = generate_expr(node.subject, local_table)
    value = generate_expr(node.value, local_table)
    if node.operation == CheckedAssignOperations.Assign:
        return f"{subject} = {value}"
    elif node.operation == CheckedAssignOperations.Increment:
        return f"{subject} += {value}"
    elif node.operation == CheckedAssignOperations.Decrement:
        return f"{subject} -= {value}"
    else:
        raise NotImplementedError()

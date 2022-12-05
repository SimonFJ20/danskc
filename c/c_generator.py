from typing import List, cast
from checker import (
    CheckedBreak,
    CheckedExpr,
    CheckedExprStatement,
    CheckedExprTypes,
    CheckedFloat,
    CheckedFunc,
    CheckedId,
    CheckedIf,
    CheckedInt,
    CheckedLet,
    CheckedReturn,
    CheckedStatement,
    CheckedStatementTypes,
    CheckedType,
    CheckedTypeTypes,
    CheckedWhile,
    GlobalTable,
    LocalTable,
)


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
    return f"const {generate_type(let.value_type)} {let.subject} = {generate_top_level_expr(let.value, global_table)};\n"


def generate_top_level_expr(node: CheckedExpr, global_table: GlobalTable) -> str:
    if node.expr_type() == CheckedExprTypes.Int:
        int_node = cast(CheckedInt, node)
        return str(int_node.value)
    else:
        raise NotImplementedError()


def generate_top_level_func(func: CheckedFunc, global_table: GlobalTable) -> str:
    acc = ""
    if func.subject == "begynd":
        acc += f"int main"
    else:
        acc += f"{generate_type(func.return_type)} {func.subject}"
    acc += f"("
    if len(func.params) > 0:
        acc += f"{generate_type(func.params[0].value_type)} {func.params[0].subject}"
        for param in func.params[1:]:
            acc += f", {generate_type(param.value_type)} {param.subject}"
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
    raise NotImplementedError()


def generate_let(statement: CheckedLet, local_table: LocalTable) -> str:
    raise NotImplementedError()


def generate_if(statement: CheckedIf, local_table: LocalTable) -> str:
    raise NotImplementedError()


def generate_while(statement: CheckedWhile, local_table: LocalTable) -> str:
    raise NotImplementedError()


def generate_break(statement: CheckedBreak, local_table: LocalTable) -> str:
    raise NotImplementedError()


def generate_func(statement: CheckedFunc, local_table: LocalTable) -> str:
    raise NotImplementedError()


def generate_return(statement: CheckedReturn, local_table: LocalTable) -> str:
    if statement.value:
        return f"return {generate_expr(statement.value, local_table)};\n"
    else:
        return "return;\n"


def generate_type(node: CheckedType) -> str:
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
        return cast(CheckedId, node).value
    elif node.expr_type() == CheckedExprTypes.Int:
        return str(cast(CheckedInt, node).value)
    elif node.expr_type() == CheckedExprTypes.Float:
        return str(cast(CheckedFloat, node).value)
    elif node.expr_type() == CheckedExprTypes.Char:
        raise NotImplementedError()
    elif node.expr_type() == CheckedExprTypes.String:
        raise NotImplementedError()
    elif node.expr_type() == CheckedExprTypes.Bool:
        raise NotImplementedError()
    elif node.expr_type() == CheckedExprTypes.Array:
        raise NotImplementedError()
    elif node.expr_type() == CheckedExprTypes.Object:
        raise NotImplementedError()
    elif node.expr_type() == CheckedExprTypes.Accessing:
        raise NotImplementedError()
    elif node.expr_type() == CheckedExprTypes.Indexing:
        raise NotImplementedError()
    elif node.expr_type() == CheckedExprTypes.Call:
        raise NotImplementedError()
    elif node.expr_type() == CheckedExprTypes.Unary:
        raise NotImplementedError()
    elif node.expr_type() == CheckedExprTypes.Binary:
        raise NotImplementedError()
    elif node.expr_type() == CheckedExprTypes.Assign:
        raise NotImplementedError()
    else:
        raise NotImplementedError()

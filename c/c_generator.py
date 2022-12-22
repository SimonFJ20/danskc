from random import randint
from typing import List, cast
from checker import (
    CheckedArray,
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
    CheckedUnary,
    CheckedUnaryOperations,
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
        acc += f"{generate_type(func.params[0].value_type, global_table)} {safeify_name(func.params[0].subject)}"
        for param in func.params[1:]:
            acc += f", {generate_type(param.value_type, global_table)} {safeify_name(param.subject)}"
    acc += ")\n{\n"
    acc += generate_statements(func.body, global_table.func_local_tables[func.subject])
    acc += "}\n"
    return acc


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


def generate_statements(
    statements: List[CheckedStatement], local_table: LocalTable
) -> str:
    return StatementGenerator(local_table).generate_statements(statements)


class StatementGenerator:
    def __init__(self, local_table: LocalTable) -> None:
        self.local_table = local_table
        self.declarations: List[str] = []

    def generate_statements(self, statements: List[CheckedStatement]) -> str:
        acc = ""
        for statement in statements:
            if statement.statement_type() == CheckedStatementTypes.Expr:
                acc += f"{self.generate_expr_statement(cast(CheckedExprStatement, statement))}"
            elif statement.statement_type() == CheckedStatementTypes.Let:
                acc += f"{self.generate_let(cast(CheckedLet, statement))}"
            elif statement.statement_type() == CheckedStatementTypes.If:
                acc += f"{self.generate_if(cast(CheckedIf, statement))}"
            elif statement.statement_type() == CheckedStatementTypes.While:
                acc += f"{self.generate_while(cast(CheckedWhile, statement))}"
            elif statement.statement_type() == CheckedStatementTypes.Break:
                acc += f"{self.generate_break(cast(CheckedBreak, statement))}"
            elif statement.statement_type() == CheckedStatementTypes.Func:
                acc += f"{self.generate_func(cast(CheckedFunc, statement))}"
            elif statement.statement_type() == CheckedStatementTypes.Return:
                acc += f"{self.generate_return(cast(CheckedReturn, statement))}"
            else:
                raise NotImplementedError()
        declarations = "".join(self.declarations)
        return f"{declarations}{acc}"

    def generate_expr_statement(self, statement: CheckedExprStatement) -> str:
        return f"{self.generate_expr(statement.value)};\n"

    def generate_let(self, statement: CheckedLet) -> str:
        value_type = generate_type(statement.value_type, self.local_table)
        subject = safeify_name(statement.subject)
        value = self.generate_expr(statement.value)
        return f"{value_type} {subject} = {value};\n"

    def generate_if(self, statement: CheckedIf) -> str:
        acc = "if ("
        acc += self.generate_expr(statement.condition)
        acc += ") {\n"
        acc += generate_statements(statement.truthy, self.local_table)
        acc += "}"
        if statement.falsy:
            acc += " else {\n"
            acc += generate_statements(statement.falsy, self.local_table)
            acc += "}"
        acc += "\n"
        return acc

    def generate_while(self, statement: CheckedWhile) -> str:
        acc = "while ("
        acc += self.generate_expr(statement.condition)
        acc += ") {\n"
        acc += generate_statements(statement.body, self.local_table)
        acc += "}\n"
        return acc

    def generate_break(self, statement: CheckedBreak) -> str:
        raise NotImplementedError()

    def generate_func(self, statement: CheckedFunc) -> str:
        raise NotImplementedError()

    def generate_return(self, statement: CheckedReturn) -> str:
        if statement.value:
            return f"return {self.generate_expr(statement.value)};\n"
        else:
            return "return;\n"

    def generate_expr(self, node: CheckedExpr) -> str:
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
            return self.generate_array(cast(CheckedArray, node))
        elif node.expr_type() == CheckedExprTypes.Object:
            raise NotImplementedError()
        elif node.expr_type() == CheckedExprTypes.Accessing:
            raise NotImplementedError()
        elif node.expr_type() == CheckedExprTypes.Indexing:
            return self.generate_indexing(cast(CheckedIndexing, node))
        elif node.expr_type() == CheckedExprTypes.Call:
            return self.generate_call(cast(CheckedCall, node))
        elif node.expr_type() == CheckedExprTypes.Unary:
            return self.generate_unary(cast(CheckedUnary, node))
        elif node.expr_type() == CheckedExprTypes.Binary:
            return self.generate_binary(cast(CheckedBinary, node))
        elif node.expr_type() == CheckedExprTypes.Assign:
            return self.generate_assign(cast(CheckedAssign, node))
        else:
            raise Exception()

    def generate_array(self, node: CheckedArray) -> str:
        if len(node.values) != 0:
            temp_declaration_name = f"temp_array_{randint(0, 10000)}"
            self.declarations.append(f"Array* {temp_declaration_name} = NULL;\n")
            acc = f"({temp_declaration_name} = array_new()"
            for value in node.values:
                acc += f", array_push({temp_declaration_name}, {self.generate_expr(value)})"
            acc += ")"
            return acc
        else:
            return f"array_new()"

    def generate_call(self, node: CheckedCall) -> str:
        subject = self.generate_expr(node.subject)
        args = ", ".join([self.generate_expr(arg) for arg in node.args])
        return f"{subject}({args})"

    def generate_indexing(self, node: CheckedIndexing) -> str:
        if node.subject.expr_value_type().type_type() == CheckedTypeTypes.Array:
            desired_type = generate_type(node.expr_value_type(), self.local_table)
            subject = self.generate_expr(node.subject)
            value = self.generate_expr(node.value)
            return f"({desired_type})array_at({subject}, {value})"
        elif node.subject.expr_value_type().type_type() == CheckedTypeTypes.String:
            return f"(char)string_at({self.generate_expr(node.subject)}, {self.generate_expr(node.value)})"
        else:
            raise Exception()

    def generate_unary(self, node: CheckedUnary) -> str:
        value = self.generate_expr(node.subject)
        if node.operation == CheckedUnaryOperations.Not:
            return f"(!{value})"
        elif node.operation == CheckedUnaryOperations.Negate:
            return f"(-{value})"
        else:
            raise NotImplementedError()

    def generate_binary(self, node: CheckedBinary) -> str:
        left = self.generate_expr(node.left)
        right = self.generate_expr(node.right)
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

    def generate_assign(self, node: CheckedAssign) -> str:
        value = self.generate_expr(node.value)
        if node.subject.expr_type() == CheckedExprTypes.Indexing:
            return self.generate_indexing_assign(node, value)
        else:
            return self.generate_primitive_assign(node, value)

    def generate_indexing_assign(self, node: CheckedAssign, value: str) -> str:
        subject_subject = self.generate_expr(
            cast(CheckedIndexing, node.subject).subject
        )
        subject_value = self.generate_expr(cast(CheckedIndexing, node.subject).value)
        if (
            cast(CheckedIndexing, node.subject).subject.expr_value_type().type_type()
            == CheckedTypeTypes.Array
        ):
            if node.operation == CheckedAssignOperations.Assign:
                return f"array_set({subject_subject}, {subject_value}, {value})"
            elif node.operation == CheckedAssignOperations.Increment:
                return f"array_set({subject_subject}, {subject_value}, array_at({subject_subject}, {subject_value}) + {value})"
            elif node.operation == CheckedAssignOperations.Decrement:
                return f"array_set({subject_subject}, {subject_value}, array_at({subject_subject}, {subject_value}) - {value})"
            else:
                raise NotImplementedError()
        else:
            raise Exception(f" {node.subject.expr_value_type()}")

    def generate_primitive_assign(self, node: CheckedAssign, value: str) -> str:
        subject = self.generate_expr(node.subject)
        if node.operation == CheckedAssignOperations.Assign:
            return f"{subject} = {value}"
        elif node.operation == CheckedAssignOperations.Increment:
            return f"{subject} += {value}"
        elif node.operation == CheckedAssignOperations.Decrement:
            return f"{subject} -= {value}"
        else:
            raise NotImplementedError()

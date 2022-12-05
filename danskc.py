from __future__ import annotations
from c.c_generator import generate_c_code
from checker import check_top_level_statements
from parser_ import Parser, parsed_statements_to_string
from tokenizer import tokenize
from argparse import ArgumentParser


def main() -> None:
    argparser = ArgumentParser("danskc")
    argparser.add_argument("file")
    argparser.add_argument("--outfile", required=True)
    args = argparser.parse_args()
    with open(args.file) as file:
        text = file.read()
        print("\nTOKENIZING...\n")
        tokens = tokenize(text)
        print("\n=== TOKEN ===\n")
        for token in tokens:
            print(token)
        print("\nPARSING...\n")
        parser = Parser(tokens)
        parsed_ast = parser.parse_statements()
        print("\n=== PARSED AST ===\n")
        print(parsed_statements_to_string(parsed_ast))
        print("\nCHECKING...\n")
        (checked_ast, global_table) = check_top_level_statements(parsed_ast)
        print("\n=== CHECKED AST ===\n")
        print("no printing :(")
        print("\n=== GENERATING C CODE ===\n")
        c_code = generate_c_code(checked_ast, global_table)
        print("\n=== GENERATED C CODE ===\n")
        print(c_code)
        with open(args.outfile, "w") as outfile:
            outfile.write(c_code)


if __name__ == "__main__":
    main()

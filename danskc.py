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
    argparser.add_argument("--debug", action="store_true")
    args = argparser.parse_args()
    with open(args.file) as file:
        text = file.read()
        if args.debug:
            print("\nTOKENIZING...\n")
        tokens = tokenize(text)
        if args.debug:
            print("\n=== TOKEN ===\n")
        if args.debug:
            for token in tokens:
                print(token)
        if args.debug:
            print("\nPARSING...\n")
        parser = Parser(tokens)
        parsed_ast = parser.parse_statements()
        if args.debug:
            print("\n=== PARSED AST ===\n")
            print(parsed_statements_to_string(parsed_ast))
            print("\nCHECKING...\n")
        (checked_ast, global_table) = check_top_level_statements(parsed_ast)
        if args.debug:
            print("\n=== CHECKED AST ===\n")
            print("no printing :(")
            print("\n=== GENERATING C CODE ===\n")
        c_code = generate_c_code(checked_ast, global_table)
        if args.debug:
            print("\n=== GENERATED C CODE ===\n")
            print(c_code)
        with open(args.outfile, "w") as outfile:
            outfile.write(c_code)


if __name__ == "__main__":
    main()

from __future__ import annotations
import os
from c.c_generator import generate_c_code
from checker import check_top_level_statements
from parser_ import Parser, parsed_statements_to_string
from tokenizer import tokenize
from argparse import ArgumentParser


def main() -> None:
    argparser = ArgumentParser("danskc")
    argparser.add_argument("file")
    argparser.add_argument("-o", "--outfile", required=True)
    argparser.add_argument("--tempfile", required=False, default="temp.c")
    argparser.add_argument("--gcc", action="store_true")
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
        if args.gcc:
            with open(args.tempfile, "w") as tempfile:
                tempfile.write(c_code)
            os.system(
                f"gcc {args.tempfile} c/runtime.c -std=c17 -Ic -Wall -Wextra -Wno-unused-variable -o {args.outfile}"
            )
            os.remove(args.tempfile)
        else:
            raise NotImplementedError(
                'GCC is currently the only backend, enable with "--gcc"'
            )


if __name__ == "__main__":
    main()

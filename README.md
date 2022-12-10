
# Programmeringssprog på dansk

## Test

```
python3 danskc.py tests/adder.dk --outfile c/test.c && gcc c/test.c -std=c17 -Wall -Wextra && ./a.out; echo $?

python3 danskc.py advent-of-code-2022/day1/main.dk --outfile c/temp.c && gcc c/temp.c c/runtime.c -std=c17 -Wall -Wextra -fsanitize=address && ./a.out; echo $?
```

## Resources

- [How Do You Make An Assembler? - StackOverflow](https://stackoverflow.com/questions/2478142/how-do-you-make-an-assembler)
- [Assemblers And Loaders - David Salomon](http://www.davidsalomon.name/assem.advertis/asl.pdf)
- [Simple but Powerful Pratt Parsing - Alex Kladov](https://matklad.github.io/2020/04/13/simple-but-powerful-pratt-parsing.html)

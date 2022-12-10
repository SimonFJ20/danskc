#include "runtime.h"

int main()
{
String* input = laes_fil(string_from("advent-of-code-2022/day1/input.txt"));
long i = 0;
long stoerste = 0;
Array* buffer = tom_tegnliste();
while ((i < tekst_laengde(input))) {
char c = string_at(input, i);
if (((c >= '0') || (c <= '9'))) {
tegnliste_tilfoej(buffer, c);
} else {
String* tal_tekst = tegnliste_til_tekst(buffer);
}
skriv_tegn(string_at(input, i));
i = (i + 1);
}
return 0;
}

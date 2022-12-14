#include "runtime.h"

int main()
{
String* input = laes_fil(string_from("advent-of-code-2022/day1/input.txt"));
long stoerste = 0;
long akkumulator = 0;
Array* buffer = tom_tegnliste();
long i = 0;
bool sidste_var_tom = false;
while ((i < tekst_laengde(input))) {
char c = string_at(input, i);
if (((c == '\n') && sidste_var_tom)) {
if ((akkumulator > stoerste)) {
stoerste = akkumulator;
}
akkumulator = 0;
} else {
if ((c == '\n')) {
String* tal_tekst = tegnliste_til_tekst(buffer);
buffer = tom_tegnliste();
long tal = tekst_til_heltal(tal_tekst);
akkumulator += tal;
sidste_var_tom = true;
} else {
if (((c >= '0') && (c <= '9'))) {
tegnliste_tilfoej(buffer, c);
sidste_var_tom = false;
} else {
fejl(string_from("burde ikke kunne ske"));
}
}
}
i += 1;
}
skriv(string_from("svaret er "));
skriv_heltal(stoerste);
skriv_linje(string_from(""));
return 0;
}

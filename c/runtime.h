#ifndef DANSKC_RUNTIME_H
#define DANSKC_RUNTIME_H

#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct String {
    size_t refs;
    void (*destroy)(struct String* string);
    size_t length, capacity;
    char* buffer;
} String;

String* string_new();
void string_destroy(String* string);
String* string_from(const char* literal);
char string_at(const String* string, long index);

typedef struct Array {
    size_t refs;
    void (*destroy)(struct Array* array);
    size_t length, capacity;
    size_t* buffer;
} Array;

Array* array_new();
void array_destroy(Array* array);
long array_push(Array* array, size_t value);
size_t array_at(Array* array, int64_t i);

long tekst_laengde(const String* string);
Array* tom_tegnliste();
void tegnliste_tilfoej(Array* array, char value);
String* tegnliste_til_tekst(Array* array);

long skriv_heltal(long value);
long skriv_decimal(double value);
long skriv_boolsk(bool value);
long skriv_tegn(char value);
long skriv(String* value);
long skriv_linje(String* value);
String* laes_fil(String* filename);

#endif

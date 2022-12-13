#include "runtime.h"
#include <stdio.h>

static const size_t string_block_size = 8;

String* string_new()
{
    String* string = (String*)malloc(sizeof(String));
    *string = (String) {
        .refs = 1,
        .destroy = string_destroy,
        .length = 0,
        .capacity = 0,
        .buffer = NULL,
    };
    return string;
}

void string_destroy(String* string)
{
    if (string->buffer)
        free(string->buffer);
}

String* string_from(const char* literal)
{
    size_t length = strlen(literal);
    size_t capacity = length + length % string_block_size + 1;
    String* string = malloc(sizeof(String));
    if (!string) {
        fprintf(stderr, "terminator: allocation failure\n");
        exit(1);
    }
    *string = (String) {
        .refs = 1,
        .destroy = string_destroy,
        .length = length,
        .capacity = capacity,
        .buffer = calloc(sizeof(char), capacity),
    };
    if (!string->buffer) {
        fprintf(stderr, "terminator: allocation failure\n");
        exit(1);
    }
    strcpy(string->buffer, literal);
    return string;
}

char string_at(const String* string, long index)
{
    return string->buffer[index];
}

const size_t array_block_size = 8;

Array* array_new()
{
    Array* array = malloc(sizeof(Array));
    if (!array) {
        fprintf(stderr, "terminator: allocation failure\n");
        exit(1);
    }
    *array = (Array) {
        .refs = 1,
        .destroy = array_destroy,
        .length = 0,
        .capacity = 0,
        .buffer = NULL,
    };
    return array;
};

void array_destroy(Array* array)
{
    if (array->buffer)
        free(array->buffer);
}

long array_push(Array* array, size_t value)
{
    if (array->length + 1 > array->capacity) {
        array->capacity += array_block_size;
        array->buffer = realloc(array->buffer, array->capacity * sizeof(size_t*));
        if (!array->buffer) {
            fprintf(stderr, "terminator: allocation failure\n");
            exit(1);
        }
    }
    array->buffer[array->length] = value;
    array->length++;
    return 0;
}

size_t array_at(Array* array, int64_t i)
{
    if (i < 0) {
        return array_at(array, -i);
    } else if ((size_t)i >= array->length) {
        fprintf(stderr, "terminator: index out of bounds\n");
        exit(1);
    } else {
        return array->buffer[i];
    }
}

long skriv_heltal(long value)
{
    printf("%ld", value);
    return 0;
}

long skriv_decimal(double value)
{
    printf("%lf", value);
    return 0;
}

long skriv_boolsk(bool value)
{
    printf("%s", value ? "true" : "false");
    return 0;
}

long skriv_tegn(char value)
{
    printf("%c", value);
    return 0;
}

long skriv(String* value)
{
    printf("%s", value->buffer);
    return 0;
}

long skriv_linje(String* value)
{
    printf("%s\n", value->buffer);
    return 0;
}

String* laes_fil(String* filename)
{
    FILE* file = fopen(filename->buffer, "r");
    if (!file) {
        fprintf(stderr, "terminator: could not open file\n");
        exit(1);
    }
    char text_buffer[65536] = { 0 };
    fread(text_buffer, 1, 65535, file);
    if (!feof(file)) {
        fprintf(stderr, "terminator: error reading file, or file is too large\n");
        exit(1);
    }
    fclose(file);
    text_buffer[65525] = '\0';
    return string_from(text_buffer);
}

long fejl(const String* message)
{
    fprintf(stderr, "fejl: %s\n", message->buffer);
    return 0;
}

long tekst_laengde(const String* string) { return string->length; }

long laengde_af_tegnliste(const Array* array) { return array->length; }

Array* tom_tegnliste() { return array_new(); }

void tegnliste_tilfoej(Array* array, char value)
{
    array_push(array, value);
}

String* tegnliste_til_tekst(Array* array)
{
    if (array->length > 8192) {
        fprintf(stderr, "terminator: avoided buffer overflow\n");
        exit(1);
    }
    char buffer[8193] = { 0 };
    for (size_t i = 0; i < array->length; i++)
        buffer[i] = array_at(array, i);
    buffer[8192] = '\0';
    return string_from(buffer);
}

long tekst_til_heltal(String* value)
{
    return atol(value->buffer);
}

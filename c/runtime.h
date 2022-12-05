#ifndef DANSKC_RUNTIME_H
#define DANSKC_RUNTIME_H

#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    size_t refs;
} RefCount;

static inline void ref(RefCount* ref_count)
{
    ref_count->refs++;
}

static inline void unref(RefCount* ref_count)
{
    ref_count->refs--;
    if (ref_count->refs <= 0 && ref_count)
        free(ref_count);
}

#define REF(value) ref((RefCount*)value)
#define UNREF(value) unref((RefCount*)value)

static const size_t string_block_size = 8;

typedef struct String {
    size_t refs;
    size_t length, capacity;
    char* buffer;
} String;

static inline String* string_new()
{
    String* string = (String*)malloc(sizeof(String));
    *string = (String) {
        .refs = 1,
        .length = 0,
        .capacity = 0,
        .buffer = NULL,
    };
    return string;
}

static inline String* string_from(const char* literal)
{
    size_t length = strlen(literal);
    size_t capacity = length + length % string_block_size;
    String* string = (String*)malloc(sizeof(String));
    *string = (String) {
        .refs = 1,
        .length = length,
        .capacity = capacity,
        .buffer = (char*)calloc(sizeof(char), length),
    };
    strcpy(string->buffer, literal);
    return string;
}

static const size_t array_block_size = 8;

typedef struct Array {
    size_t refs;
    size_t length, capacity;
    size_t* buffer;
} Array;

static inline Array* array_new()
{
    Array* array = (Array*)malloc(sizeof(Array));
    *array = (Array) {
        .refs = 1,
        .length = 0,
        .buffer = NULL,
    };
    return array;
};

static inline long array_push(Array* array, size_t value)
{
    array->length++;
    if (array->length > array->capacity) {
        array->capacity += array_block_size;
        array->buffer = (size_t*)realloc(array->buffer, array->capacity);
    }
    array->buffer[array->length - 1] = value;
    UNREF(array);
    return 0;
}

static inline size_t array_at(Array* array, int64_t i)
{
    if (i < 0) {
        UNREF(array);
        return array_at(array, -i);
    } else if ((size_t)i >= array->length) {
        fprintf(stderr, "terminator: index out of bounds\n");
        exit(1);
    } else {
        UNREF(array);
        return array->buffer[i];
    }
}

static inline long print_int(long value)
{
    printf("%ld", value);
    return 0;
}

static inline long print_float(double value)
{
    printf("%lf", value);
    return 0;
}

static inline long print_bool(bool value)
{
    printf("%s", value ? "true" : "false");
    return 0;
}

static inline long print(String* value)
{
    printf("%s", value->buffer);
    UNREF(value);
    return 0;
}

static inline long println(String* value)
{
    printf("%s\n", value->buffer);
    UNREF(value);
    return 0;
}

#endif

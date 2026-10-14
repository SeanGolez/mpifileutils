#include "common.h"

int check_str(const char* label, const char* got, const char* expected)
{
    if (strcmp(got, expected) == 0) {
        printf("PASS %s\n", label);
        return 0;
    }
    printf("FAIL %s\n  expected %s\n  got      %s\n", label, expected, got);
    return 1;
}

int check_int(const char* label, const int got, const int expected)
{
    if (got == expected) {
        printf("PASS %s\n", label);
        return 0;
    }
    printf("FAIL %s\n  expected %d\n  got      %d\n", label, expected, got);
    return 1;
}

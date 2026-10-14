#ifndef COMMON_H
#define COMMON_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#include "mfu.h"

int check_str(const char* label, const char* got, const char* expected);

int check_int(const char* label, const int got, const int expected);

#endif /* COMMON_H */

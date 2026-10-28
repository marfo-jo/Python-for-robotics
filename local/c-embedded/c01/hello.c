/*
 * C1 exercise 1: hello.c
 *
 * Copy this file into YOUR folder first (never edit the course copy):
 *   my-solutions/c-embedded/c01/hello.c
 * Then, in the Ubuntu VM:
 *   gcc -Wall -Wextra -std=c11 hello.c -o hello && ./hello
 * and when it looks right:
 *   bash <path-to-repo>/local/c-embedded/check.sh hello.c
 *
 * Goal: the output must match hello.expected.txt exactly (2 lines).
 */
#include <stdio.h>

int main(void)
{
    /* TODO 1: print exactly this line, ending with a newline (\n):
     *   Hello from the VM!
     */

    /* TODO 2: print the C standard the compiler is using, like this:
     *   C standard: 201112
     * Use the predefined macro __STDC_VERSION__ (it is a long, so the
     * printf format specifier is %ld). With -std=c11 it is 201112.
     * Try compiling with -std=c99 afterwards and watch the number change.
     */

    return 0; /* 0 tells the shell "success". Check it with: echo $? */
}

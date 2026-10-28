/*
 * C2 exercise 1: sizes.c (desktop half of the VM-vs-Uno comparison)
 *
 * Copy to my-solutions/c-embedded/c02/sizes.c and work there.
 * Check:  bash <path-to-repo>/local/c-embedded/check.sh sizes.c
 *
 * sizeof gives a size_t. The printf specifier for size_t is %zu.
 * The output must match sizes.expected.txt exactly (12 lines).
 */
#include <stdio.h>
#include <stdint.h>   /* uint8_t, int16_t, uint32_t, ... */
#include <limits.h>   /* INT_MAX, LONG_MAX, ...           */

int main(void)
{
    printf("sizeof(char) = %zu\n", sizeof(char));

    /* TODO 1: one line each, same format, in this order:
     *   short, int, long, long long, float, double
     */

    /* TODO 2: one line each, same format, for the fixed-width types:
     *   uint8_t, int16_t, uint32_t
     */

    /* TODO 3: print the largest int and the largest long:
     *   INT_MAX = <value>     (INT_MAX is an int: use %d)
     *   LONG_MAX = <value>    (LONG_MAX is a long: use %ld)
     */

    return 0;
}

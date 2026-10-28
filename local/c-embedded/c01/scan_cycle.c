/*
 * C1 exercise 2: scan_cycle.c
 *
 * An Arduino sketch has no main(). The Arduino core supplies one that calls
 * setup() once and then loop() forever, like a PLC scan cycle. In this
 * desktop program YOU write that main(), but you stop after 5 scans so the
 * program ends and check.sh can compare the output.
 *
 * Copy to my-solutions/c-embedded/c01/scan_cycle.c and work there.
 * Check:  bash <path-to-repo>/local/c-embedded/check.sh scan_cycle.c
 */
#include <stdio.h>

/* A global counter: it keeps its value between calls to loop(). */
unsigned int scan_count = 0;

void setup(void)
{
    printf("setup(): runs once\n");
}

void loop(void)
{
    scan_count++;
    printf("loop(): scan %u\n", scan_count);
}

int main(void)
{
    /* TODO 1: call setup() exactly once. */

    /* TODO 2: call loop() 5 times. A C for loop looks like this:
     *     for (int i = 0; i < 5; i++) {
     *         ... body runs with i = 0, 1, 2, 3, 4 ...
     *     }
     */

    /* TODO 3: print this final line, using scan_count and %u:
     *   main(): stopped after 5 scans (a real Arduino never stops)
     */

    return 0;
}

/*
 * C2 exercise 2: overflow.c (wraparound, the millis() trick, and printf)
 *
 * Copy to my-solutions/c-embedded/c02/overflow.c and work there.
 * BEFORE you run each part, write your prediction in a comment next to it.
 * Check:  bash <path-to-repo>/local/c-embedded/check.sh overflow.c
 * The output must match overflow.expected.txt exactly (9 lines).
 */
#include <stdio.h>
#include <stdint.h>
#include <inttypes.h>   /* PRIu32 and friends */

int main(void)
{
    /* Part 1 (done for you): an unsigned 8-bit value wraps from 255 to 0.
     * The (unsigned) cast makes the argument match %u exactly. */
    uint8_t a = 255;
    a = a + 1;
    printf("uint8_t: 255 + 1 = %u\n", (unsigned)a);

    /* TODO Part 2: uint8_t b = 0; subtract 1; print
     *   uint8_t: 0 - 1 = <value>
     */

    /* TODO Part 3: uint16_t c = 65535; add 1; print
     *   uint16_t: 65535 + 1 = <value>
     */

    /* TODO Part 4: int16_t t = INT16_MAX; t = t + 1; print with %d
     *   int16_t: 32767 + 1 stored back = <value>
     * (Read the C2 page: why is this "implementation-defined" here, but
     *  undefined behavior if you write  int t = 32767; t++;  on the Uno?)
     */

    /* TODO Part 5: the millis() rollover trick.
     *   uint32_t start = 4294967290u;   (6 ms before the counter wraps)
     *   uint32_t now   = 14u;           (14 ms after it wrapped)
     * Compute elapsed = now - start as a uint32_t and print it with PRIu32:
     *   elapsed across the wrap = <value> ms
     * PRIu32 is a string macro, so the format looks like:
     *   "elapsed across the wrap = %" PRIu32 " ms\n"
     */

    /* TODO Part 6: print how many days a uint32_t millisecond counter lasts:
     *   uint32_t ms counter wraps after <value> days
     * Use UINT32_MAX / 86400000.0 and the format %.1f
     */

    /* TODO Part 7: long ticks = 100000L; print it with %ld:
     *   long ticks = 100000
     */

    /* TODO Part 8: hex. Print these two lines using %X (uppercase hex):
     *   0xFF = 255
     *   INT16_MAX = 32767 = 0x7FFF
     * (%X expects an unsigned int: pass 0xFFu, and cast INT16_MAX with (unsigned).)
     */

    return 0;
}

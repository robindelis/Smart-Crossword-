#ifndef MUX_DRIVER_H
#define MUX_DRIVER_H

#include <stdint.h>
#include <stdbool.h>

/**
 * Initialize GPIO pins for CD74HC4067 16-channel multiplexer.
 */
void mux_init(void);

/**
 * Select active RF channel (0 to 15) by driving S0..S3 address lines.
 * Applies settling delay to stabilize the analog switch connection.
 * 
 * @param channel Index 0 to 15.
 */
void mux_select_channel(uint8_t channel);

/**
 * Enable multiplexer output (pulls EN low).
 */
void mux_enable(void);

/**
 * Disable multiplexer output (pulls EN high, isolating all coils).
 */
void mux_disable(void);

/**
 * Get the currently selected channel.
 */
uint8_t mux_get_current_channel(void);

#endif /* MUX_DRIVER_H */

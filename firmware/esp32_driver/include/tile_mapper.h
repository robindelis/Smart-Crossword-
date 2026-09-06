#ifndef TILE_MAPPER_H
#define TILE_MAPPER_H

#include <stdint.h>
#include <stdbool.h>
#include "config.h"

#define MAX_REGISTERED_TILES 128

typedef struct {
    uint8_t uid[MAX_UID_LEN];
    uint8_t uid_len;
    char letter;
    uint8_t points;
    bool active;
} TileMapping;

/**
 * Initialize tile mapping table with standard English Scrabble point rules
 * and default bench test tag IDs.
 */
void tile_mapper_init(void);

/**
 * Look up letter and point score by NFC UID.
 * 
 * @return true if UID was found in mapping table, false if unknown tag.
 */
bool tile_mapper_lookup(const uint8_t *uid, uint8_t uid_len, char *out_letter, uint8_t *out_points);

/**
 * Register or update an NFC UID mapping.
 */
bool tile_mapper_register(const uint8_t *uid, uint8_t uid_len, char letter, uint8_t points);

/**
 * Print all registered tiles to standard output.
 */
void tile_mapper_print_table(void);

#endif /* TILE_MAPPER_H */

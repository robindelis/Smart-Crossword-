#include "tile_mapper.h"
#include <stdio.h>
#include <string.h>
#include <ctype.h>

static TileMapping s_tile_table[MAX_REGISTERED_TILES];
static size_t s_tile_count = 0;

static const uint8_t s_english_scores[26] = {
    /* A  B  C  D  E  F  G  H  I  J  K  L  M */
       1, 3, 3, 2, 1, 4, 2, 4, 1, 8, 5, 1, 3,
    /* N  O  P  Q  R  S  T  U  V  W  X  Y  Z */
       1, 1, 3,10, 1, 1, 1, 1, 4, 4, 8, 4, 10
};

static uint8_t get_default_letter_score(char letter) {
    letter = toupper((unsigned char)letter);
    if (letter >= 'A' && letter <= 'Z') {
        return s_english_scores[letter - 'A'];
    }
    return 0; /* Blank or invalid */
}

void tile_mapper_init(void) {
    memset(s_tile_table, 0, sizeof(s_tile_table));
    s_tile_count = 0;

    /* Pre-register 16 default 7-byte test UIDs for letters P-L-A-Y-W-O-R-D-S-C-B-E-N-C-H-T */
    const char test_letters[16] = {
        'P', 'L', 'A', 'Y',
        'W', 'O', 'R', 'D',
        'S', 'C', 'B', 'E',
        'N', 'T', 'I', 'M'
    };

    for (int i = 0; i < 16; i++) {
        uint8_t dummy_uid[MAX_UID_LEN] = {0x04, 0xA1, 0xB2, 0xC3, 0xD4, 0xE5, (uint8_t)(0x10 + i)};
        tile_mapper_register(dummy_uid, 7, test_letters[i], get_default_letter_score(test_letters[i]));
    }
}

bool tile_mapper_lookup(const uint8_t *uid, uint8_t uid_len, char *out_letter, uint8_t *out_points) {
    if (!uid || uid_len == 0) return false;

    for (size_t i = 0; i < s_tile_count; i++) {
        if (s_tile_table[i].active && s_tile_table[i].uid_len == uid_len) {
            if (memcmp(s_tile_table[i].uid, uid, uid_len) == 0) {
                if (out_letter) *out_letter = s_tile_table[i].letter;
                if (out_points) *out_points = s_tile_table[i].points;
                return true;
            }
        }
    }
    return false;
}

bool tile_mapper_register(const uint8_t *uid, uint8_t uid_len, char letter, uint8_t points) {
    if (!uid || uid_len == 0 || uid_len > MAX_UID_LEN) return false;

    letter = toupper((unsigned char)letter);
    if (points == 0 && letter >= 'A' && letter <= 'Z') {
        points = get_default_letter_score(letter);
    }

    /* Check if already registered */
    for (size_t i = 0; i < s_tile_count; i++) {
        if (s_tile_table[i].active && s_tile_table[i].uid_len == uid_len) {
            if (memcmp(s_tile_table[i].uid, uid, uid_len) == 0) {
                s_tile_table[i].letter = letter;
                s_tile_table[i].points = points;
                return true;
            }
        }
    }

    /* Add new slot */
    if (s_tile_count < MAX_REGISTERED_TILES) {
        memcpy(s_tile_table[s_tile_count].uid, uid, uid_len);
        s_tile_table[s_tile_count].uid_len = uid_len;
        s_tile_table[s_tile_count].letter = letter;
        s_tile_table[s_tile_count].points = points;
        s_tile_table[s_tile_count].active = true;
        s_tile_count++;
        return true;
    }

    return false;
}

void tile_mapper_print_table(void) {
    printf("\n=== Registered NFC Tile Mappings (%zu tiles) ===\n", s_tile_count);
    printf("| Index | UID                    | Letter | Points |\n");
    printf("| :---- | :--------------------- | :----- | :----- |\n");
    for (size_t i = 0; i < s_tile_count; i++) {
        if (s_tile_table[i].active) {
            printf("| %-5zu | ", i + 1);
            for (int u = 0; u < s_tile_table[i].uid_len; u++) {
                printf("%02X", s_tile_table[i].uid[u]);
            }
            printf("       | '%c'    | %-6u |\n", s_tile_table[i].letter, s_tile_table[i].points);
        }
    }
    printf("================================================\n\n");
}

#include "grid_scanner.h"
#include "mux_driver.h"
#include "pn532_driver.h"
#include "tile_mapper.h"
#include "crossword_engine.h"
#include <stdio.h>
#include <string.h>
#include <time.h>

#ifdef ESP_PLATFORM
#include "esp_timer.h"
static int64_t get_time_us(void) {
    return esp_timer_get_time();
}
#else
static int64_t get_time_us(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (int64_t)ts.tv_sec * 1000000LL + (ts.tv_nsec / 1000LL);
}
#endif

void grid_scanner_init(GridScanner *scanner) {
    if (!scanner) return;
    memset(scanner, 0, sizeof(GridScanner));
    scanner->min_scan_duration_us = 0xFFFFFFFF;
}

int grid_scanner_sweep(GridScanner *scanner) {
    if (!scanner) return 0;

    int64_t t_start = get_time_us();
    int occupied_count = 0;

    mux_enable();

    for (uint8_t ch = 0; ch < GRID_TOTAL_CELLS; ch++) {
        uint8_t row = ch / GRID_COLS;
        uint8_t col = ch % GRID_COLS;
        GridCellState *cell = &scanner->cells[row][col];

        /* Select analog multiplexer channel */
        mux_select_channel(ch);

        /* Poll active antenna coil for NFC target */
        PN532_Target target;
        bool found = pn532_read_passive_target(NFC_POLL_TIMEOUT_MS, &target);

        if (found) {
            char letter = '?';
            uint8_t pts = 0;
            tile_mapper_lookup(target.uid, target.uid_len, &letter, &pts);

            if (!cell->occupied || cell->letter != letter) {
                cell->occupied = true;
                cell->letter = letter;
                cell->points = pts;
                cell->uid_len = target.uid_len;
                memcpy(cell->uid, target.uid, target.uid_len);
                cell->stable_count = 1;
                printf("[EVENT] Tile PLACED at (%d,%d): Letter '%c' (%u pts)\n", row, col, letter, pts);
            } else {
                cell->stable_count++;
            }
            occupied_count++;
        } else {
            if (cell->occupied) {
                printf("[EVENT] Tile REMOVED from (%d,%d): Was '%c'\n", row, col, cell->letter);
                cell->occupied = false;
                cell->letter = ' ';
                cell->points = 0;
                cell->uid_len = 0;
                memset(cell->uid, 0, MAX_UID_LEN);
                cell->stable_count = 0;
            }
        }
    }

    mux_disable();

    int64_t t_end = get_time_us();
    uint32_t duration_us = (uint32_t)(t_end - t_start);

    scanner->last_scan_duration_us = duration_us;
    if (duration_us < scanner->min_scan_duration_us) scanner->min_scan_duration_us = duration_us;
    if (duration_us > scanner->max_scan_duration_us) scanner->max_scan_duration_us = duration_us;

    scanner->total_scans++;
    if (scanner->total_scans == 1) {
        scanner->avg_scan_duration_us = duration_us;
    } else {
        scanner->avg_scan_duration_us = (scanner->avg_scan_duration_us * 7 + duration_us) / 8;
    }

    return occupied_count;
}

void grid_scanner_print_board(const GridScanner *scanner) {
    if (!scanner) return;

    printf("\n  +---+---+---+---+\n");
    for (int r = 0; r < GRID_ROWS; r++) {
        printf("%d |", r);
        for (int c = 0; c < GRID_COLS; c++) {
            if (scanner->cells[r][c].occupied) {
                printf(" %c |", scanner->cells[r][c].letter);
            } else {
                printf(" . |");
            }
        }
        printf("\n  +---+---+---+---+\n");
    }
    printf("    0   1   2   3\n\n");
}

void grid_scanner_print_stats(const GridScanner *scanner) {
    if (!scanner) return;

    printf("=== NFC Sweep Benchmark Statistics ===\n");
    printf("Total Full Sweeps (16 coils): %u\n", scanner->total_scans);
    printf("Last Sweep Latency:           %.2f ms (%u µs)\n", 
           scanner->last_scan_duration_us / 1000.0f, scanner->last_scan_duration_us);
    printf("Average Sweep Latency:        %.2f ms (%u µs)\n", 
           scanner->avg_scan_duration_us / 1000.0f, scanner->avg_scan_duration_us);
    if (scanner->min_scan_duration_us != 0xFFFFFFFF) {
        printf("Min / Max Sweep Latency:      %.2f ms / %.2f ms\n",
               scanner->min_scan_duration_us / 1000.0f, scanner->max_scan_duration_us / 1000.0f);
    }
    printf("Per-Channel Average Time:     %.2f ms\n", 
           (scanner->avg_scan_duration_us / 16.0f) / 1000.0f);
    printf("Target Latency Ceiling:       40.00 ms (PASS: %s)\n",
           (scanner->last_scan_duration_us <= 40000) ? "YES" : "NO");
    printf("======================================\n\n");
}

void grid_scanner_evaluate_move(const GridScanner *scanner) {
    if (!scanner) return;

    printf("=== Scrabble Referee Evaluation ===\n");
    int word_count = 0;

    /* Check horizontal rows */
    for (int r = 0; r < GRID_ROWS; r++) {
        char buffer[GRID_COLS + 1];
        int len = 0;
        int score = 0;
        for (int c = 0; c < GRID_COLS; c++) {
            if (scanner->cells[r][c].occupied) {
                buffer[len++] = scanner->cells[r][c].letter;
                score += scanner->cells[r][c].points;
            } else {
                if (len >= 2) {
                    buffer[len] = '\0';
                    bool valid = dictionary_contains(buffer);
                    printf("-> Horizontal [%d,%d..%d]: \"%s\" (%d pts) - %s\n",
                           r, c - len, c - 1, buffer, score, valid ? "VALID WORD" : "INVALID WORD");
                    word_count++;
                }
                len = 0;
                score = 0;
            }
        }
        if (len >= 2) {
            buffer[len] = '\0';
            bool valid = dictionary_contains(buffer);
            printf("-> Horizontal [%d,%d..%d]: \"%s\" (%d pts) - %s\n",
                   r, GRID_COLS - len, GRID_COLS - 1, buffer, score, valid ? "VALID WORD" : "INVALID WORD");
            word_count++;
        }
    }

    /* Check vertical columns */
    for (int c = 0; c < GRID_COLS; c++) {
        char buffer[GRID_ROWS + 1];
        int len = 0;
        int score = 0;
        for (int r = 0; r < GRID_ROWS; r++) {
            if (scanner->cells[r][c].occupied) {
                buffer[len++] = scanner->cells[r][c].letter;
                score += scanner->cells[r][c].points;
            } else {
                if (len >= 2) {
                    buffer[len] = '\0';
                    bool valid = dictionary_contains(buffer);
                    printf("-> Vertical [%d..%d,%d]: \"%s\" (%d pts) - %s\n",
                           r - len, r - 1, c, buffer, score, valid ? "VALID WORD" : "INVALID WORD");
                    word_count++;
                }
                len = 0;
                score = 0;
            }
        }
        if (len >= 2) {
            buffer[len] = '\0';
            bool valid = dictionary_contains(buffer);
            printf("-> Vertical [%d..%d,%d]: \"%s\" (%d pts) - %s\n",
                   GRID_ROWS - len, GRID_ROWS - 1, c, buffer, score, valid ? "VALID WORD" : "INVALID WORD");
            word_count++;
        }
    }

    if (word_count == 0) {
        printf("-> No contiguous words (>= 2 letters) detected on the grid.\n");
    }
    printf("===================================\n\n");
}

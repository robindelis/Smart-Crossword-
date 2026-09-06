#ifndef GRID_SCANNER_H
#define GRID_SCANNER_H

#include <stdint.h>
#include <stdbool.h>
#include "config.h"

typedef struct {
    bool occupied;
    char letter;
    uint8_t points;
    uint8_t uid[MAX_UID_LEN];
    uint8_t uid_len;
    uint8_t stable_count;
} GridCellState;

typedef struct {
    GridCellState cells[GRID_ROWS][GRID_COLS];
    uint32_t last_scan_duration_us;
    uint32_t avg_scan_duration_us;
    uint32_t total_scans;
    uint32_t min_scan_duration_us;
    uint32_t max_scan_duration_us;
} GridScanner;

/**
 * Initialize grid scanner state.
 */
void grid_scanner_init(GridScanner *scanner);

/**
 * Perform one complete sweep across all 16 channels.
 * 
 * @param scanner Pointer to scanner instance.
 * @return Number of detected tiles.
 */
int grid_scanner_sweep(GridScanner *scanner);

/**
 * Print the current 4x4 visual board state to console.
 */
void grid_scanner_print_board(const GridScanner *scanner);

/**
 * Print scan latency statistics.
 */
void grid_scanner_print_stats(const GridScanner *scanner);

/**
 * Evaluate the current 4x4 board state against the crossword game referee.
 */
void grid_scanner_evaluate_move(const GridScanner *scanner);

#endif /* GRID_SCANNER_H */

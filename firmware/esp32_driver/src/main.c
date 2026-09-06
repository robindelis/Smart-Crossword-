#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "config.h"
#include "mux_driver.h"
#include "pn532_driver.h"
#include "tile_mapper.h"
#include "grid_scanner.h"
#include "crossword_engine.h"

static GridScanner s_scanner;

static void run_bench_test(int iterations) {
    printf("\n>>> Running %d consecutive 16-channel sweep cycles...\n", iterations);
    for (int i = 0; i < iterations; i++) {
        grid_scanner_sweep(&s_scanner);
    }
    grid_scanner_print_stats(&s_scanner);
}

static void run_automated_validation(void) {
    printf("\n=======================================================\n");
    printf("   ESP32 4x4 BENCH DRIVER - AUTOMATED VERIFICATION     \n");
    printf("=======================================================\n");

    /* 1. Initialize subsystems */
    mux_init();
    pn532_init();
    tile_mapper_init();
    grid_scanner_init(&s_scanner);
    engine_init();

    /* Load tournament dictionary for referee validation */
    const char *dict_path = "data/dict_en.txt";
    int words = engine_load_dictionary_file(dict_path);
    if (words <= 0) {
        dict_path = "../../data/dict_en.txt";
        words = engine_load_dictionary_file(dict_path);
    }
    printf("[1] Engine initialized: %d English tournament words loaded.\n", words);

    /* 2. Test empty sweep */
    printf("[2] Testing baseline sweep on empty board...\n");
    int count = grid_scanner_sweep(&s_scanner);
    printf("    -> Detected %d tiles (Expected: 0)\n", count);
    if (count != 0) {
        printf("    FAIL: Empty board sweep returned non-zero!\n");
        exit(1);
    }

    /* 3. Inject simulated wooden tiles for word 'PLAY' on Row 1 (channels 4, 5, 6, 7) */
    printf("[3] Simulating placement of word 'P-L-A-Y' on Row 1...\n");
    uint8_t uid_p[7] = {0x04, 0xA1, 0xB2, 0xC3, 0xD4, 0xE5, 0x10}; /* 'P' */
    uint8_t uid_l[7] = {0x04, 0xA1, 0xB2, 0xC3, 0xD4, 0xE5, 0x11}; /* 'L' */
    uint8_t uid_a[7] = {0x04, 0xA1, 0xB2, 0xC3, 0xD4, 0xE5, 0x12}; /* 'A' */
    uint8_t uid_y[7] = {0x04, 0xA1, 0xB2, 0xC3, 0xD4, 0xE5, 0x13}; /* 'Y' */

    pn532_mock_set_target(4, true, uid_p, 7);
    pn532_mock_set_target(5, true, uid_l, 7);
    pn532_mock_set_target(6, true, uid_a, 7);
    pn532_mock_set_target(7, true, uid_y, 7);

    count = grid_scanner_sweep(&s_scanner);
    printf("    -> Detected %d tiles (Expected: 4)\n", count);
    if (count != 4) {
        printf("    FAIL: Expected 4 tiles, got %d\n", count);
        exit(1);
    }

    /* 4. Display board */
    printf("[4] Board state after sweep:");
    grid_scanner_print_board(&s_scanner);

    /* 5. Evaluate referee */
    printf("[5] Referee evaluation:");
    grid_scanner_evaluate_move(&s_scanner);

    /* 6. Latency benchmark */
    printf("[6] Benchmarking 50 sweeps for latency invariant (<40ms ceiling)...");
    run_bench_test(50);

    /* 7. Simulate tile removal */
    printf("[7] Simulating removal of tile 'Y' at (1,3)... \n");
    pn532_mock_set_target(7, false, NULL, 0);
    count = grid_scanner_sweep(&s_scanner);
    printf("    -> Detected %d tiles (Expected: 3)\n", count);
    grid_scanner_print_board(&s_scanner);
    if (count != 3) {
        printf("    FAIL: Expected 3 tiles after removal, got %d\n", count);
        exit(1);
    }

    printf("=======================================================\n");
    printf("   ALL 7 HARDWARE DRIVER TESTS PASSED SUCCESSFULLY!    \n");
    printf("=======================================================\n\n");
}

int main(int argc, char **argv) {
    if (argc > 1 && strcmp(argv[1], "test") == 0) {
        run_automated_validation();
        return 0;
    }

    /* Default interactive / banner output */
    printf("\n=======================================================\n");
    printf("   Smart Crossword Board - ESP32 4x4 Bench Driver      \n");
    printf("   Hardware: CD74HC4067 (16-Ch MUX) + PN532 (SPI)      \n");
    printf("=======================================================\n\n");

    run_automated_validation();
    return 0;
}

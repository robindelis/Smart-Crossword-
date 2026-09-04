#include <stdio.h>
#include <string.h>
#include <assert.h>
#include "../firmware/engine/crossword_engine.h"

static void clear_board(char board[BOARD_SIZE][BOARD_SIZE]) {
    memset(board, 0, sizeof(char) * BOARD_SIZE * BOARD_SIZE);
}

static void test_first_move_center_required(void) {
    char board[BOARD_SIZE][BOARD_SIZE];
    clear_board(board);

    /* Move at row 0, col 0 (does not cover 7,7) */
    TilePlacement p1[3] = {
        {0, 0, 'C', false, 0},
        {0, 1, 'A', false, 0},
        {0, 2, 'T', false, 0}
    };
    MoveResult res;
    MoveErrorCode err = engine_validate_move(board, p1, 3, &res);
    assert(err == ERR_FIRST_MOVE_NOT_CENTER);
    printf("PASS: test_first_move_center_required\n");
}

static void test_first_move_valid(void) {
    char board[BOARD_SIZE][BOARD_SIZE];
    clear_board(board);

    /* Move "HELLO" across center (7,7) to (7,11) */
    TilePlacement p[5] = {
        {7, 7,  'H', false, 0},
        {7, 8,  'E', false, 0},
        {7, 9,  'L', false, 0},
        {7, 10, 'L', false, 0},
        {7, 11, 'O', false, 0}
    };
    MoveResult res;
    MoveErrorCode err = engine_validate_move(board, p, 5, &res);
    assert(err == MOVE_OK);
    assert(res.words_count == 1);
    assert(strcmp(res.words[0], "HELLO") == 0);
    
    /* Center (7,7) is Double Word Score (DWS)
       H(4) + E(1) + L(1) + L(1) + O(1*2 for DLS at 7,11) = 9
       Word mult: DWS on (7,7) = * 2
       Total score = 18
    */
    assert(res.total_score == 18);
    printf("PASS: test_first_move_valid (score: %d)\n", res.total_score);
}

static void test_collinear_check(void) {
    char board[BOARD_SIZE][BOARD_SIZE];
    clear_board(board);

    /* Placed in an L-shape: (7,7), (7,8), (8,8) */
    TilePlacement p[3] = {
        {7, 7, 'C', false, 0},
        {7, 8, 'A', false, 0},
        {8, 8, 'T', false, 0}
    };
    MoveResult res;
    MoveErrorCode err = engine_validate_move(board, p, 3, &res);
    assert(err == ERR_NOT_IN_LINE);
    printf("PASS: test_collinear_check\n");
}

static void test_gap_in_word(void) {
    char board[BOARD_SIZE][BOARD_SIZE];
    clear_board(board);

    /* Placed at (7,7) and (7,9), leaving (7,8) empty */
    TilePlacement p[2] = {
        {7, 7, 'G', false, 0},
        {7, 9, 'O', false, 0}
    };
    MoveResult res;
    MoveErrorCode err = engine_validate_move(board, p, 2, &res);
    assert(err == ERR_GAP_IN_WORD);
    printf("PASS: test_gap_in_word\n");
}

static void test_disconnected_move(void) {
    char board[BOARD_SIZE][BOARD_SIZE];
    clear_board(board);

    /* Turn 1: "HI" at (7,7)-(7,8) */
    TilePlacement t1[2] = {
        {7, 7, 'H', false, 0},
        {7, 8, 'I', false, 0}
    };
    engine_apply_move(board, t1, 2);

    /* Turn 2: "DOG" way up at (0,0)-(0,2) */
    TilePlacement t2[3] = {
        {0, 0, 'D', false, 0},
        {0, 1, 'O', false, 0},
        {0, 2, 'G', false, 0}
    };
    MoveResult res;
    MoveErrorCode err = engine_validate_move(board, t2, 3, &res);
    assert(err == ERR_DISCONNECTED);
    printf("PASS: test_disconnected_move\n");
}

static void test_interlocking_and_crossword(void) {
    char board[BOARD_SIZE][BOARD_SIZE];
    clear_board(board);

    /* Turn 1: "HELLO" at (7,7)-(7,11) */
    TilePlacement t1[5] = {
        {7, 7,  'H', false, 0},
        {7, 8,  'E', false, 0},
        {7, 9,  'L', false, 0},
        {7, 10, 'L', false, 0},
        {7, 11, 'O', false, 0}
    };
    engine_apply_move(board, t1, 5);

    /* Turn 2: "HONEY" placed vertically, intersecting 'H' at (7,7).
       New tiles placed at (8,7), (9,7), (10,7), (11,7): O, N, E, Y.
    */
    TilePlacement t2[4] = {
        {8,  7, 'O', false, 0},
        {9,  7, 'N', false, 0},
        {10, 7, 'E', false, 0},
        {11, 7, 'Y', false, 0}
    };
    MoveResult res;
    MoveErrorCode err = engine_validate_move(board, t2, 4, &res);
    assert(err == MOVE_OK);
    assert(res.words_count == 1);
    assert(strcmp(res.words[0], "HONEY") == 0);

    /* Score calculation for HONEY:
       H at (7,7): already on board -> base 4
       O at (8,7): row 8, col 7 -> 1 pt
       N at (9,7): row 9, col 7 -> 1 pt
       E at (10,7): row 10, col 7 -> 1 pt
       Y at (11,7): row 11, col 7 -> DLS (Double Letter Score) -> 4 * 2 = 8 pts
       Word sum: H(4) + O(1) + N(1) + E(1) + Y(8) = 15 pts
       Total score = 15 pts
    */
    assert(res.total_score == 15);
    printf("PASS: test_interlocking_and_crossword (score: %d)\n", res.total_score);
}

static void test_bingo_bonus(void) {
    char board[BOARD_SIZE][BOARD_SIZE];
    clear_board(board);

    /* First move using all 7 tiles: "GRANDMA" covering center star (7,7) */
    TilePlacement t[7] = {
        {7, 4,  'G', false, 0},
        {7, 5,  'R', false, 0},
        {7, 6,  'A', false, 0},
        {7, 7,  'N', false, 0},
        {7, 8,  'D', false, 0},
        {7, 9,  'M', false, 0},
        {7, 10, 'A', false, 0}
    };

    MoveResult res;
    MoveErrorCode err = engine_validate_move(board, t, 7, &res);
    assert(err == MOVE_OK);
    assert(res.is_bingo == true);
    /* 50 points bingo bonus included */
    assert(res.total_score >= 50);
    printf("PASS: test_bingo_bonus (total score with +50 bingo: %d)\n", res.total_score);
}

static void test_real_dictionary_load(void) {
    int count = engine_load_dictionary_file("../../data/dictionary.txt");
    assert(count > 170000);
    printf("PASS: test_real_dictionary_load (Loaded %d words)\n", count);

    /* Test real word lookups */
    assert(dictionary_contains("SCRABBLE") == true);
    assert(dictionary_contains("SYZYGY") == true);
    assert(dictionary_contains("QUIZZICAL") == true);
    assert(dictionary_contains("NOTAREALWORDXYZ") == false);
    printf("PASS: test_real_dictionary_queries\n");
    engine_free_dictionary();
}

int main(void) {
    printf("=== Starting Crossword Engine Tests ===\n");
    engine_init();
    test_first_move_center_required();
    test_first_move_valid();
    test_collinear_check();
    test_gap_in_word();
    test_disconnected_move();
    test_interlocking_and_crossword();
    test_bingo_bonus();
    test_real_dictionary_load();
    printf("=== ALL ENGINE TESTS PASSED! ===\n");
    return 0;
}

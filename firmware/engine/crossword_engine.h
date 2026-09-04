#ifndef CROSSWORD_ENGINE_H
#define CROSSWORD_ENGINE_H

#include <stdint.h>
#include <stdbool.h>

#define BOARD_SIZE 15
#define MAX_TILES_PER_MOVE 7
#define MAX_WORDS_PER_MOVE 8
#define MAX_WORD_LEN 16

/* Square bonus multiplier types */
typedef enum {
    BONUS_NONE = 0,
    BONUS_DLS  = 1, /* Double Letter Score */
    BONUS_TLS  = 2, /* Triple Letter Score */
    BONUS_DWS  = 3, /* Double Word Score */
    BONUS_TWS  = 4  /* Triple Word Score */
} BonusType;

/* Move validation error codes */
typedef enum {
    MOVE_OK                   = 0,
    ERR_NO_TILES              = 1,
    ERR_TOO_MANY_TILES        = 2,
    ERR_OUT_OF_BOUNDS         = 3,
    ERR_SQUARE_OCCUPIED       = 4,
    ERR_NOT_IN_LINE           = 5,
    ERR_GAP_IN_WORD           = 6,
    ERR_FIRST_MOVE_NOT_CENTER = 7,
    ERR_DISCONNECTED          = 8,
    ERR_SINGLE_LETTER_WORD    = 9,
    ERR_INVALID_WORD          = 10
} MoveErrorCode;

/* Representation of one placed tile */
typedef struct {
    uint8_t row;          /* 0 to 14 */
    uint8_t col;          /* 0 to 14 */
    char letter;          /* 'A' to 'Z' */
    bool is_blank;        /* true if tile is a blank tile */
    char assigned_letter; /* letter assigned if blank */
} TilePlacement;

/* Detailed breakdown of score for a move */
typedef struct {
    MoveErrorCode status;
    char error_message[64];
    int total_score;
    int words_count;
    char words[MAX_WORDS_PER_MOVE][MAX_WORD_LEN];
    int word_scores[MAX_WORDS_PER_MOVE];
    bool is_bingo; /* +50 points bonus if 7 tiles played */
} MoveResult;

/* API Functions */
void engine_init(void);
BonusType engine_get_bonus(int row, int col);
int engine_get_letter_value(char letter);
bool dictionary_contains(const char* word);
int engine_load_dictionary_file(const char* filepath);
void engine_free_dictionary(void);

/* Validate a move against current board, calculate score without modifying board */
MoveErrorCode engine_validate_move(
    const char board[BOARD_SIZE][BOARD_SIZE],
    const TilePlacement* placements,
    int count,
    MoveResult* out_result
);

/* Apply valid placements onto board */
void engine_apply_move(
    char board[BOARD_SIZE][BOARD_SIZE],
    const TilePlacement* placements,
    int count
);

/* Check if board is completely empty (first turn) */
bool engine_is_board_empty(const char board[BOARD_SIZE][BOARD_SIZE]);

#endif /* CROSSWORD_ENGINE_H */

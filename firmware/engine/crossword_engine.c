#include "crossword_engine.h"

/* Standard Scrabble letter scores (A-Z) */
static const int LETTER_VALUES[26] = {
    1, 3, 3, 2, 1, 4, 2, 4, 1, 8, 5, 1, 3, 1, 1, 3, 10, 1, 1, 1, 1, 4, 4, 8, 4, 10
};

/* Official Scrabble bonus square matrix (15x15)
   0: None, 1: DLS, 2: TLS, 3: DWS, 4: TWS */
static const uint8_t BONUS_GRID[BOARD_SIZE][BOARD_SIZE] = {
    {4, 0, 0, 1, 0, 0, 0, 4, 0, 0, 0, 1, 0, 0, 4},
    {0, 3, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 3, 0},
    {0, 0, 3, 0, 0, 0, 1, 0, 1, 0, 0, 0, 3, 0, 0},
    {1, 0, 0, 3, 0, 0, 0, 1, 0, 0, 0, 3, 0, 0, 1},
    {0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0},
    {0, 2, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 2, 0},
    {0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0},
    {4, 0, 0, 1, 0, 0, 0, 3, 0, 0, 0, 1, 0, 0, 4}, /* (7,7) center is DWS */
    {0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0},
    {0, 2, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 2, 0},
    {0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0},
    {1, 0, 0, 3, 0, 0, 0, 1, 0, 0, 0, 3, 0, 0, 1},
    {0, 0, 3, 0, 0, 0, 1, 0, 1, 0, 0, 0, 3, 0, 0},
    {0, 3, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 3, 0},
    {4, 0, 0, 1, 0, 0, 0, 4, 0, 0, 0, 1, 0, 0, 4}
};

/* Core built-in baseline dictionary for standalone / embedded verification */
static const char* BUILTIN_WORDS[] = {
    "AA", "AB", "AD", "AE", "AG", "AH", "AI", "AL", "AM", "AN", "AR", "AS", "AT", "AW", "AX", "AY",
    "BA", "BE", "BI", "BO", "BY", "CAT", "CLOUD", "DO", "DOG", "ED", "EF", "EH", "EL", "EM", "EN",
    "ER", "ES", "ET", "EX", "FA", "FE", "GO", "HA", "HE", "HELLO", "HI", "HM", "HO", "HONEY", "ID",
    "IF", "IN", "IS", "IT", "JO", "KA", "KI", "LA", "LI", "LO", "MA", "ME", "MI", "MM", "MO", "MU",
    "MY", "NA", "NE", "NO", "NU", "OD", "OE", "OF", "OH", "OI", "OK", "OM", "ON", "OP", "OR", "OS",
    "OW", "OX", "OY", "PA", "PE", "PEACH", "PI", "PLAY", "PO", "QI", "RE", "SH", "SI", "SO", "TA",
    "TI", "TO", "UH", "UM", "UN", "UP", "US", "UT", "WE", "WO", "XI", "XU", "YA", "YE", "YO", "ZA",
    "BREEZE", "GARDEN", "HOME", "LOVE", "QUIET", "QUARTZ", "SMART", "BOARD", "GAME", "WORD", "WORDS",
    "FAMILY", "GRANDMA", "GRANDPA", "TOUCH", "TILES", "RACK", "SCORE", "DOUBLE", "TRIPLE", "LETTER"
};
static const int BUILTIN_WORDS_COUNT = sizeof(BUILTIN_WORDS) / sizeof(BUILTIN_WORDS[0]);

/* External dictionary callback support */
typedef bool (*CustomDictFn)(const char* word);
static CustomDictFn g_custom_dict_fn = 0;

void engine_set_custom_dictionary(CustomDictFn fn) {
    g_custom_dict_fn = fn;
}

void engine_init(void) {
    /* Ready for initialization */
}

BonusType engine_get_bonus(int row, int col) {
    if (row < 0 || row >= BOARD_SIZE || col < 0 || col >= BOARD_SIZE) {
        return BONUS_NONE;
    }
    return (BonusType)BONUS_GRID[row][col];
}

int engine_get_letter_value(char letter) {
    if (letter >= 'a' && letter <= 'z') letter -= 32;
    if (letter >= 'A' && letter <= 'Z') {
        return LETTER_VALUES[letter - 'A'];
    }
    return 0;
}

static int str_compare(const char* s1, const char* s2) {
    while (*s1 && (*s1 == *s2)) {
        s1++;
        s2++;
    }
    return *(const unsigned char*)s1 - *(const unsigned char*)s2;
}

#ifndef __wasm__
#include <stdio.h>
#include <stdlib.h>
static char** g_file_words = 0;
static int g_file_words_count = 0;
static char* g_dict_buffer = 0;

int engine_load_dictionary_file(const char* filepath) {
    FILE* f = fopen(filepath, "rb");
    if (!f) return -1;
    fseek(f, 0, SEEK_END);
    long sz = ftell(f);
    fseek(f, 0, SEEK_SET);
    if (sz <= 0) { fclose(f); return -1; }

    engine_free_dictionary();

    g_dict_buffer = (char*)malloc(sz + 2);
    if (!g_dict_buffer) { fclose(f); return -1; }
    size_t read_bytes = fread(g_dict_buffer, 1, sz, f);
    fclose(f);
    g_dict_buffer[read_bytes] = '\0';

    int count = 0;
    for (size_t i = 0; i < read_bytes; i++) {
        if (g_dict_buffer[i] == '\n') count++;
    }
    count += 2;

    g_file_words = (char**)malloc(count * sizeof(char*));
    if (!g_file_words) return -1;

    int idx = 0;
    char* p = g_dict_buffer;
    while (*p) {
        while (*p == '\r' || *p == '\n' || *p == ' ') p++;
        if (!*p) break;
        g_file_words[idx++] = p;
        while (*p && *p != '\r' && *p != '\n') {
            if (*p >= 'a' && *p <= 'z') *p -= 32;
            p++;
        }
        if (*p) {
            *p = '\0';
            p++;
        }
    }
    g_file_words_count = idx;
    return g_file_words_count;
}

void engine_free_dictionary(void) {
    if (g_dict_buffer) {
        free(g_dict_buffer);
        g_dict_buffer = 0;
    }
    if (g_file_words) {
        free(g_file_words);
        g_file_words = 0;
    }
    g_file_words_count = 0;
}
#else
int engine_load_dictionary_file(const char* filepath) {
    (void)filepath;
    return -1;
}
void engine_free_dictionary(void) {}
#endif

bool dictionary_contains(const char* word) {
    if (g_custom_dict_fn) {
        return g_custom_dict_fn(word);
    }
#ifndef __wasm__
    if (g_file_words && g_file_words_count > 0) {
        int low = 0;
        int high = g_file_words_count - 1;
        while (low <= high) {
            int mid = low + (high - low) / 2;
            int cmp = str_compare(word, g_file_words[mid]);
            if (cmp == 0) return true;
            if (cmp < 0) high = mid - 1;
            else low = mid + 1;
        }
        return false;
    }
#endif
    /* Simple linear search over baseline built-in list */
    for (int i = 0; i < BUILTIN_WORDS_COUNT; i++) {
        if (str_compare(BUILTIN_WORDS[i], word) == 0) {
            return true;
        }
    }
    return false;
}

bool engine_is_board_empty(const char board[BOARD_SIZE][BOARD_SIZE]) {
    for (int r = 0; r < BOARD_SIZE; r++) {
        for (int c = 0; c < BOARD_SIZE; c++) {
            if (board[r][c] != '\0' && board[r][c] != ' ') {
                return false;
            }
        }
    }
    return true;
}

static void copy_string(char* dest, const char* src, int max_len) {
    int i = 0;
    while (src[i] != '\0' && i < max_len - 1) {
        dest[i] = src[i];
        i++;
    }
    dest[i] = '\0';
}

MoveErrorCode engine_validate_move(
    const char board[BOARD_SIZE][BOARD_SIZE],
    const TilePlacement* placements,
    int count,
    MoveResult* out_result
) {
    if (!out_result) return ERR_NO_TILES;
    
    out_result->total_score = 0;
    out_result->words_count = 0;
    out_result->is_bingo = (count == MAX_TILES_PER_MOVE);
    out_result->error_message[0] = '\0';

    if (count <= 0) {
        out_result->status = ERR_NO_TILES;
        copy_string(out_result->error_message, "No tiles placed", 64);
        return ERR_NO_TILES;
    }
    if (count > MAX_TILES_PER_MOVE) {
        out_result->status = ERR_TOO_MANY_TILES;
        copy_string(out_result->error_message, "Too many tiles placed", 64);
        return ERR_TOO_MANY_TILES;
    }

    bool board_empty = engine_is_board_empty(board);

    /* 1. Bounds and occupancy check */
    bool covers_center = false;
    for (int i = 0; i < count; i++) {
        int r = placements[i].row;
        int c = placements[i].col;
        if (r < 0 || r >= BOARD_SIZE || c < 0 || c >= BOARD_SIZE) {
            out_result->status = ERR_OUT_OF_BOUNDS;
            copy_string(out_result->error_message, "Tile placed out of bounds", 64);
            return ERR_OUT_OF_BOUNDS;
        }
        if (board[r][c] != '\0' && board[r][c] != ' ') {
            out_result->status = ERR_SQUARE_OCCUPIED;
            copy_string(out_result->error_message, "Square already occupied", 64);
            return ERR_SQUARE_OCCUPIED;
        }
        if (r == 7 && c == 7) {
            covers_center = true;
        }
    }

    if (board_empty && !covers_center) {
        out_result->status = ERR_FIRST_MOVE_NOT_CENTER;
        copy_string(out_result->error_message, "First move must cover center star (H8)", 64);
        return ERR_FIRST_MOVE_NOT_CENTER;
    }

    /* 2. Collinear check */
    bool same_row = true;
    bool same_col = true;
    int fixed_row = placements[0].row;
    int fixed_col = placements[0].col;

    for (int i = 1; i < count; i++) {
        if (placements[i].row != fixed_row) same_row = false;
        if (placements[i].col != fixed_col) same_col = false;
    }

    if (!same_row && !same_col) {
        out_result->status = ERR_NOT_IN_LINE;
        copy_string(out_result->error_message, "Tiles must be in a single row or column", 64);
        return ERR_NOT_IN_LINE;
    }

    /* Create working grid including newly placed tiles */
    char temp_board[BOARD_SIZE][BOARD_SIZE];
    bool is_new[BOARD_SIZE][BOARD_SIZE];
    for (int r = 0; r < BOARD_SIZE; r++) {
        for (int c = 0; c < BOARD_SIZE; c++) {
            temp_board[r][c] = board[r][c];
            is_new[r][c] = false;
        }
    }

    int min_r = 15, max_r = -1, min_c = 15, max_c = -1;
    for (int i = 0; i < count; i++) {
        int r = placements[i].row;
        int c = placements[i].col;
        char let = placements[i].is_blank ? placements[i].assigned_letter : placements[i].letter;
        if (let >= 'a' && let <= 'z') let -= 32;
        temp_board[r][c] = let;
        is_new[r][c] = true;

        if (r < min_r) min_r = r;
        if (r > max_r) max_r = r;
        if (c < min_c) min_c = c;
        if (c > max_c) max_c = c;
    }

    /* 3. Continuity check (no empty gaps between bounds) */
    if (same_row) {
        for (int c = min_c; c <= max_c; c++) {
            if (temp_board[fixed_row][c] == '\0' || temp_board[fixed_row][c] == ' ') {
                out_result->status = ERR_GAP_IN_WORD;
                copy_string(out_result->error_message, "Empty gap in word", 64);
                return ERR_GAP_IN_WORD;
            }
        }
    } else {
        for (int r = min_r; r <= max_r; r++) {
            if (temp_board[r][fixed_col] == '\0' || temp_board[r][fixed_col] == ' ') {
                out_result->status = ERR_GAP_IN_WORD;
                copy_string(out_result->error_message, "Empty gap in word", 64);
                return ERR_GAP_IN_WORD;
            }
        }
    }

    /* 4. Connectivity check (must connect to existing board if not empty) */
    if (!board_empty) {
        bool connected = false;
        for (int i = 0; i < count; i++) {
            int r = placements[i].row;
            int c = placements[i].col;
            if (r > 0 && board[r-1][c] != '\0' && board[r-1][c] != ' ') connected = true;
            if (r < BOARD_SIZE-1 && board[r+1][c] != '\0' && board[r+1][c] != ' ') connected = true;
            if (c > 0 && board[r][c-1] != '\0' && board[r][c-1] != ' ') connected = true;
            if (c < BOARD_SIZE-1 && board[r][c+1] != '\0' && board[r][c+1] != ' ') connected = true;
            if (connected) break;
        }
        if (!connected) {
            out_result->status = ERR_DISCONNECTED;
            copy_string(out_result->error_message, "Tiles must connect to existing words", 64);
            return ERR_DISCONNECTED;
        }
    }

    /* 5. Extract words and calculate score */
    int total_score = 0;

    /* A. Main Word along placement line */
    bool is_horizontal = same_row;
    if (count == 1) {
        /* Single tile: check if it extends horizontal or vertical */
        bool has_h = (fixed_col > 0 && temp_board[fixed_row][fixed_col-1]) ||
                     (fixed_col < BOARD_SIZE-1 && temp_board[fixed_row][fixed_col+1]);
        bool has_v = (fixed_row > 0 && temp_board[fixed_row-1][fixed_col]) ||
                     (fixed_row < BOARD_SIZE-1 && temp_board[fixed_row+1][fixed_col]);
        is_horizontal = has_h || (!has_h && !has_v);
    }

    if (is_horizontal) {
        /* Find horizontal word bounds */
        int start_c = min_c;
        while (start_c > 0 && temp_board[fixed_row][start_c-1] != '\0' && temp_board[fixed_row][start_c-1] != ' ') {
            start_c--;
        }
        int end_c = max_c;
        while (end_c < BOARD_SIZE-1 && temp_board[fixed_row][end_c+1] != '\0' && temp_board[fixed_row][end_c+1] != ' ') {
            end_c++;
        }

        if (end_c > start_c) {
            char word[MAX_WORD_LEN];
            int len = 0;
            int word_pts = 0;
            int word_mult = 1;

            for (int c = start_c; c <= end_c && len < MAX_WORD_LEN - 1; c++) {
                char ch = temp_board[fixed_row][c];
                word[len++] = ch;
                int base_val = engine_get_letter_value(ch);

                if (is_new[fixed_row][c]) {
                    BonusType b = engine_get_bonus(fixed_row, c);
                    if (b == BONUS_DLS) base_val *= 2;
                    else if (b == BONUS_TLS) base_val *= 3;
                    else if (b == BONUS_DWS) word_mult *= 2;
                    else if (b == BONUS_TWS) word_mult *= 3;
                }
                word_pts += base_val;
            }
            word[len] = '\0';

            if (!dictionary_contains(word)) {
                out_result->status = ERR_INVALID_WORD;
                copy_string(out_result->error_message, "Not in dictionary: ", 24);
                copy_string(out_result->error_message + 19, word, 40);
                return ERR_INVALID_WORD;
            }

            int score = word_pts * word_mult;
            total_score += score;
            copy_string(out_result->words[out_result->words_count], word, MAX_WORD_LEN);
            out_result->word_scores[out_result->words_count] = score;
            out_result->words_count++;
        }
    } else {
        /* Vertical main word */
        int start_r = min_r;
        while (start_r > 0 && temp_board[start_r-1][fixed_col] != '\0' && temp_board[start_r-1][fixed_col] != ' ') {
            start_r--;
        }
        int end_r = max_r;
        while (end_r < BOARD_SIZE-1 && temp_board[end_r+1][fixed_col] != '\0' && temp_board[end_r+1][fixed_col] != ' ') {
            end_r++;
        }

        if (end_r > start_r) {
            char word[MAX_WORD_LEN];
            int len = 0;
            int word_pts = 0;
            int word_mult = 1;

            for (int r = start_r; r <= end_r && len < MAX_WORD_LEN - 1; r++) {
                char ch = temp_board[r][fixed_col];
                word[len++] = ch;
                int base_val = engine_get_letter_value(ch);

                if (is_new[r][fixed_col]) {
                    BonusType b = engine_get_bonus(r, fixed_col);
                    if (b == BONUS_DLS) base_val *= 2;
                    else if (b == BONUS_TLS) base_val *= 3;
                    else if (b == BONUS_DWS) word_mult *= 2;
                    else if (b == BONUS_TWS) word_mult *= 3;
                }
                word_pts += base_val;
            }
            word[len] = '\0';

            if (!dictionary_contains(word)) {
                out_result->status = ERR_INVALID_WORD;
                copy_string(out_result->error_message, "Not in dictionary: ", 24);
                copy_string(out_result->error_message + 19, word, 40);
                return ERR_INVALID_WORD;
            }

            int score = word_pts * word_mult;
            total_score += score;
            copy_string(out_result->words[out_result->words_count], word, MAX_WORD_LEN);
            out_result->word_scores[out_result->words_count] = score;
            out_result->words_count++;
        }
    }

    /* B. Cross-words perpendicular to each placed tile */
    for (int i = 0; i < count; i++) {
        int r = placements[i].row;
        int c = placements[i].col;

        if (is_horizontal) {
            /* Check vertical cross-word for this tile */
            int start_r = r;
            while (start_r > 0 && temp_board[start_r-1][c] != '\0' && temp_board[start_r-1][c] != ' ') {
                start_r--;
            }
            int end_r = r;
            while (end_r < BOARD_SIZE-1 && temp_board[end_r+1][c] != '\0' && temp_board[end_r+1][c] != ' ') {
                end_r++;
            }

            if (end_r > start_r) {
                char word[MAX_WORD_LEN];
                int len = 0;
                int word_pts = 0;
                int word_mult = 1;

                for (int curr_r = start_r; curr_r <= end_r && len < MAX_WORD_LEN - 1; curr_r++) {
                    char ch = temp_board[curr_r][c];
                    word[len++] = ch;
                    int base_val = engine_get_letter_value(ch);

                    if (curr_r == r) {
                        /* Newly placed tile gets bonus applied to cross-word too */
                        BonusType b = engine_get_bonus(curr_r, c);
                        if (b == BONUS_DLS) base_val *= 2;
                        else if (b == BONUS_TLS) base_val *= 3;
                        else if (b == BONUS_DWS) word_mult *= 2;
                        else if (b == BONUS_TWS) word_mult *= 3;
                    }
                    word_pts += base_val;
                }
                word[len] = '\0';

                if (!dictionary_contains(word)) {
                    out_result->status = ERR_INVALID_WORD;
                    copy_string(out_result->error_message, "Cross-word invalid: ", 24);
                    copy_string(out_result->error_message + 20, word, 40);
                    return ERR_INVALID_WORD;
                }

                int score = word_pts * word_mult;
                total_score += score;
                copy_string(out_result->words[out_result->words_count], word, MAX_WORD_LEN);
                out_result->word_scores[out_result->words_count] = score;
                out_result->words_count++;
            }
        } else {
            /* Vertical main: check horizontal cross-word */
            int start_c = c;
            while (start_c > 0 && temp_board[r][start_c-1] != '\0' && temp_board[r][start_c-1] != ' ') {
                start_c--;
            }
            int end_c = c;
            while (end_c < BOARD_SIZE-1 && temp_board[r][end_c+1] != '\0' && temp_board[r][end_c+1] != ' ') {
                end_c++;
            }

            if (end_c > start_c) {
                char word[MAX_WORD_LEN];
                int len = 0;
                int word_pts = 0;
                int word_mult = 1;

                for (int curr_c = start_c; curr_c <= end_c && len < MAX_WORD_LEN - 1; curr_c++) {
                    char ch = temp_board[r][curr_c];
                    word[len++] = ch;
                    int base_val = engine_get_letter_value(ch);

                    if (curr_c == c) {
                        BonusType b = engine_get_bonus(r, curr_c);
                        if (b == BONUS_DLS) base_val *= 2;
                        else if (b == BONUS_TLS) base_val *= 3;
                        else if (b == BONUS_DWS) word_mult *= 2;
                        else if (b == BONUS_TWS) word_mult *= 3;
                    }
                    word_pts += base_val;
                }
                word[len] = '\0';

                if (!dictionary_contains(word)) {
                    out_result->status = ERR_INVALID_WORD;
                    copy_string(out_result->error_message, "Cross-word invalid: ", 24);
                    copy_string(out_result->error_message + 20, word, 40);
                    return ERR_INVALID_WORD;
                }

                int score = word_pts * word_mult;
                total_score += score;
                copy_string(out_result->words[out_result->words_count], word, MAX_WORD_LEN);
                out_result->word_scores[out_result->words_count] = score;
                out_result->words_count++;
            }
        }
    }

    if (out_result->words_count == 0) {
        out_result->status = ERR_SINGLE_LETTER_WORD;
        copy_string(out_result->error_message, "Word must be at least 2 letters", 64);
        return ERR_SINGLE_LETTER_WORD;
    }

    /* Bingo bonus */
    if (out_result->is_bingo) {
        total_score += 50;
    }

    out_result->total_score = total_score;
    out_result->status = MOVE_OK;
    return MOVE_OK;
}

void engine_apply_move(
    char board[BOARD_SIZE][BOARD_SIZE],
    const TilePlacement* placements,
    int count
) {
    for (int i = 0; i < count; i++) {
        int r = placements[i].row;
        int c = placements[i].col;
        char let = placements[i].is_blank ? placements[i].assigned_letter : placements[i].letter;
        if (let >= 'a' && let <= 'z') let -= 32;
        board[r][c] = let;
    }
}

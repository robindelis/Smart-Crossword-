package com.example.crosswordcompanion.model

enum class SquareType(val label: String, val badgeColor: Long) {
    NORMAL("", 0xFFF5EFE6),
    DOUBLE_LETTER("2L", 0xFF81D4FA),
    TRIPLE_LETTER("3L", 0xFF0288D1),
    DOUBLE_WORD("2W", 0xFFFFCDD2),
    TRIPLE_WORD("3W", 0xFFD32F2F),
    CENTER("★", 0xFFFFD54F)
}

data class Tile(
    val letter: Char,
    val points: Int,
    val isBlank: Boolean = false
)

data class BoardCell(
    val row: Int,
    val col: Int,
    val squareType: SquareType,
    val tile: Tile? = null,
    val isCommitted: Boolean = false
)

class Board4x4 {
    companion object {
        const val SIZE = 4

        /**
         * Creates a fresh 4x4 prototype board layout containing sample bonus squares:
         * (0,0): 2W, (0,3): 3L
         * (1,1): Center Star (★ / 2L), (1,3): 2L
         * (2,1): 2L
         * (3,0): 3L, (3,3): 3W
         */
        fun createDefaultLayout(): List<BoardCell> {
            val cells = mutableListOf<BoardCell>()
            for (r in 0 until SIZE) {
                for (c in 0 until SIZE) {
                    val type = when {
                        r == 0 && c == 0 -> SquareType.DOUBLE_WORD
                        r == 0 && c == 3 -> SquareType.TRIPLE_LETTER
                        r == 1 && c == 1 -> SquareType.CENTER
                        r == 1 && c == 3 -> SquareType.DOUBLE_LETTER
                        r == 2 && c == 1 -> SquareType.DOUBLE_LETTER
                        r == 3 && c == 0 -> SquareType.TRIPLE_LETTER
                        r == 3 && c == 3 -> SquareType.TRIPLE_WORD
                        else -> SquareType.NORMAL
                    }
                    cells.add(BoardCell(r, c, type))
                }
            }
            return cells
        }
    }
}

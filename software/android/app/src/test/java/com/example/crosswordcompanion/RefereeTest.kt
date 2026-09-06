package com.example.crosswordcompanion

import com.example.crosswordcompanion.game.EnglishReferee
import com.example.crosswordcompanion.model.Board4x4
import com.example.crosswordcompanion.model.BoardCell
import com.example.crosswordcompanion.model.SquareType
import com.example.crosswordcompanion.model.Tile
import com.example.crosswordcompanion.model.UniqueUsernameGenerator
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class RefereeTest {

    private val referee = EnglishReferee()

    @Test
    fun testFirstMoveMustCoverCenterStar() {
        val board = Board4x4.createDefaultLayout()

        // Place "GO" at row 0, col 0 and 1 (does not cover (1,1) center star)
        val uncommitted = listOf(
            BoardCell(0, 0, SquareType.DOUBLE_WORD, Tile('G', 2)),
            BoardCell(0, 1, SquareType.NORMAL, Tile('O', 1))
        )
        val updatedBoard = board.map { cell ->
            uncommitted.find { it.row == cell.row && it.col == cell.col } ?: cell
        }

        val result = referee.evaluateMove(updatedBoard, uncommitted, isFirstMove = true)
        assertFalse("First move without covering center star must be rejected", result.isValid)
        assertTrue("Error message must mention center star", result.message.contains("center star"))
    }

    @Test
    fun testValidFirstMoveCoveringCenterStarWithBonuses() {
        val board = Board4x4.createDefaultLayout()

        // Place "PLAY" at row 1, cols 0..3:
        // (1,0)=NORMAL: 'P'(3) -> 3 pts
        // (1,1)=CENTER (2L): 'L'(1)*2 -> 2 pts
        // (1,2)=NORMAL: 'A'(1) -> 1 pt
        // (1,3)=DOUBLE_LETTER (2L): 'Y'(4)*2 -> 8 pts
        // Expected score: 3 + 2 + 1 + 8 = 14 pts
        val uncommitted = listOf(
            BoardCell(1, 0, SquareType.NORMAL, Tile('P', 3)),
            BoardCell(1, 1, SquareType.CENTER, Tile('L', 1)),
            BoardCell(1, 2, SquareType.NORMAL, Tile('A', 1)),
            BoardCell(1, 3, SquareType.DOUBLE_LETTER, Tile('Y', 4))
        )
        val updatedBoard = board.map { cell ->
            uncommitted.find { it.row == cell.row && it.col == cell.col } ?: cell
        }

        val result = referee.evaluateMove(updatedBoard, uncommitted, isFirstMove = true)
        assertTrue("Move 'PLAY' must be valid", result.isValid)
        assertEquals("Words formed must contain PLAY", listOf("PLAY"), result.words)
        assertEquals("Score with 2L on L and Y must be 14", 14, result.score)
    }

    @Test
    fun testDoubleWordMultiplier() {
        val board = Board4x4.createDefaultLayout()

        // Place "AT" at row 0, cols 0..1:
        // (0,0)=DOUBLE_WORD (2W): 'A'(1)
        // (0,1)=NORMAL: 'T'(1)
        // Word letter sum = 1 + 1 = 2
        // Word multiplier = 2x
        // Expected score = 2 * 2 = 4 pts
        val uncommitted = listOf(
            BoardCell(0, 0, SquareType.DOUBLE_WORD, Tile('A', 1)),
            BoardCell(0, 1, SquareType.NORMAL, Tile('T', 1))
        )
        val updatedBoard = board.map { cell ->
            uncommitted.find { it.row == cell.row && it.col == cell.col } ?: cell
        }

        // Simulate subsequent turn (isFirstMove = false)
        val result = referee.evaluateMove(updatedBoard, uncommitted, isFirstMove = false)
        assertTrue("Move 'AT' on 2W must be valid", result.isValid)
        assertEquals(4, result.score)
    }

    @Test
    fun testTripleWordMultiplier() {
        val board = Board4x4.createDefaultLayout()

        // Place "WIN" at row 3, cols 1..3:
        // (3,1)=NORMAL: 'W'(4)
        // (3,2)=NORMAL: 'I'(1)
        // (3,3)=TRIPLE_WORD (3W): 'N'(1)
        // Word letter sum = 4 + 1 + 1 = 6
        // Word multiplier = 3x
        // Expected score = 6 * 3 = 18 pts
        val uncommitted = listOf(
            BoardCell(3, 1, SquareType.NORMAL, Tile('W', 4)),
            BoardCell(3, 2, SquareType.NORMAL, Tile('I', 1)),
            BoardCell(3, 3, SquareType.TRIPLE_WORD, Tile('N', 1))
        )
        val updatedBoard = board.map { cell ->
            uncommitted.find { it.row == cell.row && it.col == cell.col } ?: cell
        }

        val result = referee.evaluateMove(updatedBoard, uncommitted, isFirstMove = false)
        assertTrue("Move 'WIN' on 3W must be valid", result.isValid)
        assertEquals(18, result.score)
    }

    @Test
    fun testInvalidWordRejection() {
        val board = Board4x4.createDefaultLayout()

        // Place non-existent word "XYZ" covering center star (1,1)
        val uncommitted = listOf(
            BoardCell(1, 0, SquareType.NORMAL, Tile('X', 8)),
            BoardCell(1, 1, SquareType.CENTER, Tile('Y', 4)),
            BoardCell(1, 2, SquareType.NORMAL, Tile('Z', 10))
        )
        val updatedBoard = board.map { cell ->
            uncommitted.find { it.row == cell.row && it.col == cell.col } ?: cell
        }

        val result = referee.evaluateMove(updatedBoard, uncommitted, isFirstMove = true)
        assertFalse("Nonsense word 'XYZ' must be rejected", result.isValid)
        assertTrue("Message must indicate word is not valid", result.message.contains("not a valid English word"))
    }

    @Test
    fun testInternalGapRejection() {
        val board = Board4x4.createDefaultLayout()

        // Place tiles at (1,0) and (1,2) leaving (1,1) empty
        val uncommitted = listOf(
            BoardCell(1, 0, SquareType.NORMAL, Tile('A', 1)),
            BoardCell(1, 2, SquareType.NORMAL, Tile('T', 1))
        )
        val updatedBoard = board.map { cell ->
            uncommitted.find { it.row == cell.row && it.col == cell.col } ?: cell
        }

        val result = referee.evaluateMove(updatedBoard, uncommitted, isFirstMove = false)
        assertFalse("Tiles with gap must be rejected", result.isValid)
        assertTrue("Message must indicate gap", result.message.contains("gaps"))
    }

    @Test
    fun testUniqueUsernameGeneratorAndValidator() {
        val handle1 = UniqueUsernameGenerator.generate("Sarah")
        assertTrue("Generated handle must start with sarah#", handle1.startsWith("sarah#"))
        assertTrue("Generated handle must be valid", UniqueUsernameGenerator.isValidHandle(handle1))

        val boardHandle = UniqueUsernameGenerator.generate("Board", isBoard = true)
        assertTrue("Board handle must start with board_scb", boardHandle.startsWith("board_scb"))
        assertTrue("Board handle must be valid", UniqueUsernameGenerator.isValidHandle(boardHandle))

        assertTrue("scb-8492 format must be valid", UniqueUsernameGenerator.isValidHandle("scb-8492"))
        assertFalse("Empty handle is invalid", UniqueUsernameGenerator.isValidHandle(""))
        assertFalse("Single letter handle without suffix is invalid", UniqueUsernameGenerator.isValidHandle("a"))
    }

    @Test
    fun testUniqueUsernameBatchGeneration() {
        // Generate 100 handles and ensure all are valid and have standard length/format
        val handles = (1..100).map { UniqueUsernameGenerator.generate("Player$it") }
        assertEquals(100, handles.size)
        handles.forEach { handle ->
            assertTrue("Handle $handle must be valid", UniqueUsernameGenerator.isValidHandle(handle))
            assertTrue("Handle $handle must contain #", handle.contains("#"))
            val parts = handle.split("#")
            assertEquals(2, parts.size)
            assertEquals("Suffix must be 4 digits", 4, parts[1].length)
            assertTrue("Suffix must be numeric", parts[1].all { it.isDigit() })
        }
    }

    @Test
    fun testAllEnglishLetterScoringValues() {
        val expectedScores = mapOf(
            'A' to 1, 'B' to 3, 'C' to 3, 'D' to 2, 'E' to 1,
            'F' to 4, 'G' to 2, 'H' to 4, 'I' to 1, 'J' to 8,
            'K' to 5, 'L' to 1, 'M' to 3, 'N' to 1, 'O' to 1,
            'P' to 3, 'Q' to 10, 'R' to 1, 'S' to 1, 'T' to 1,
            'U' to 1, 'V' to 4, 'W' to 4, 'X' to 8, 'Y' to 4,
            'Z' to 10
        )
        expectedScores.forEach { (char, expected) ->
            assertEquals("Score for letter $char must be $expected", expected, EnglishReferee.LETTER_SCORES[char])
        }
    }

    @Test
    fun testVerticalWordPlacementAndScoring() {
        val board = Board4x4.createDefaultLayout()

        // Place vertical word "TOP" at col 1, rows 0..2 covering center star at (1,1):
        // (0,1)=NORMAL: 'T'(1) -> 1 pt
        // (1,1)=CENTER (2L): 'O'(1)*2 -> 2 pts
        // (2,1)=NORMAL: 'P'(3) -> 3 pts
        // Total expected = 1 + 2 + 3 = 6 pts
        val uncommitted = listOf(
            BoardCell(0, 1, SquareType.NORMAL, Tile('T', 1)),
            BoardCell(1, 1, SquareType.CENTER, Tile('O', 1)),
            BoardCell(2, 1, SquareType.NORMAL, Tile('P', 3))
        )
        val updatedBoard = board.map { cell ->
            uncommitted.find { it.row == cell.row && it.col == cell.col } ?: cell
        }

        val result = referee.evaluateMove(updatedBoard, uncommitted, isFirstMove = true)
        assertTrue("Vertical move 'TOP' must be valid", result.isValid)
        assertEquals(listOf("TOP"), result.words)
        assertEquals(6, result.score)
    }

    @Test
    fun testFullTournamentDictionaryLoading() {
        val dictFile = java.io.File("src/main/assets/dict_en.txt")
        assertTrue("dict_en.txt must exist in assets", dictFile.exists())

        val ref = EnglishReferee()
        val count = ref.loadDictionary(dictFile)
        assertTrue("Loaded dictionary must contain >= 168,000 words (actual: $count)", count >= 168000)

        // Test classic tournament words from ENABLE1
        assertTrue("ZYGOTE must be valid", ref.isWordValid("ZYGOTE"))
        assertTrue("SCRABBLE must be valid", ref.isWordValid("SCRABBLE"))
        assertTrue("CROSSWORD must be valid", ref.isWordValid("CROSSWORD"))
        assertTrue("QUIZ must be valid", ref.isWordValid("QUIZ"))
        assertTrue("QI must be valid", ref.isWordValid("QI"))
        assertTrue("ZA must be valid", ref.isWordValid("ZA"))
        assertFalse("Nonsense word XYZABC must be invalid", ref.isWordValid("XYZABC"))
    }
}


package com.example.crosswordcompanion.model

import java.util.Random

data class UserProfile(
    val id: String,
    val displayName: String,
    val uniqueUsername: String,
    val email: String? = null,
    val isBoard: Boolean = false
)

object UniqueUsernameGenerator {
    private val RANDOM_CHARS = "0123456789".toCharArray()

    /**
     * Generates a unique, friendly identifier like "sarah#4821" or "board_scb8492".
     */
    fun generate(displayName: String, isBoard: Boolean = false): String {
        val sanitized = displayName.lowercase().replace(Regex("[^a-z0-9]"), "")
        val prefix = if (sanitized.isEmpty()) "player" else sanitized

        return if (isBoard) {
            val suffix = (1000..9999).random()
            "board_scb$suffix"
        } else {
            val suffix = (1000..9999).random()
            "$prefix#$suffix"
        }
    }

    /**
     * Validates if an input string is a valid unique handle:
     * - User format: name#1234 (letters/digits followed by # and 4 digits)
     * - Board format: board_scb1234 or SCB-1234
     */
    fun isValidHandle(handle: String): Boolean {
        val trimmed = handle.trim().lowercase()
        val userRegex = Regex("^[a-z0-9_]{2,}#[0-9]{4}$")
        val boardRegex = Regex("^(board_scb[0-9]{4}|scb-[0-9]{4})$")
        return userRegex.matches(trimmed) || boardRegex.matches(trimmed)
    }
}

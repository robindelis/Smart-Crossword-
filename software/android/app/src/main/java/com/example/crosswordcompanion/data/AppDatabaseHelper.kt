package com.example.crosswordcompanion.data

import android.content.ContentValues
import android.content.Context
import android.database.sqlite.SQLiteDatabase
import android.database.sqlite.SQLiteOpenHelper
import com.example.crosswordcompanion.model.UserProfile

data class FriendRecord(
    val id: String,
    val displayName: String,
    val uniqueUsername: String,
    val isBoard: Boolean,
    val status: String
)

data class GameRecord(
    val gameId: String,
    val opponentName: String,
    val opponentHandle: String,
    val playerScore: Int,
    val opponentScore: Int,
    val currentTurn: String,
    val lastUpdated: Long
)

class AppDatabaseHelper(context: Context) : SQLiteOpenHelper(context, DATABASE_NAME, null, DATABASE_VERSION) {

    companion object {
        const val DATABASE_NAME = "crossword_companion.db"
        const val DATABASE_VERSION = 1

        // Table Users
        const val TABLE_USERS = "users"
        const val COL_USER_ID = "id"
        const val COL_USER_NAME = "display_name"
        const val COL_USER_HANDLE = "unique_username"
        const val COL_USER_EMAIL = "email"
        const val COL_USER_LOGGED_IN = "is_logged_in"

        // Table Friends
        const val TABLE_FRIENDS = "friends"
        const val COL_FRIEND_ID = "id"
        const val COL_FRIEND_NAME = "display_name"
        const val COL_FRIEND_HANDLE = "unique_username"
        const val COL_FRIEND_IS_BOARD = "is_board"
        const val COL_FRIEND_STATUS = "status"

        // Table Games
        const val TABLE_GAMES = "games"
        const val COL_GAME_ID = "game_id"
        const val COL_GAME_OPPONENT = "opponent_name"
        const val COL_GAME_HANDLE = "opponent_handle"
        const val COL_GAME_PLAYER_SCORE = "player_score"
        const val COL_GAME_OPP_SCORE = "opponent_score"
        const val COL_GAME_TURN = "current_turn"
        const val COL_GAME_UPDATED = "last_updated"
    }

    override fun onCreate(db: SQLiteDatabase) {
        db.execSQL("""
            CREATE TABLE $TABLE_USERS (
                $COL_USER_ID TEXT PRIMARY KEY,
                $COL_USER_NAME TEXT NOT NULL,
                $COL_USER_HANDLE TEXT NOT NULL UNIQUE,
                $COL_USER_EMAIL TEXT,
                $COL_USER_LOGGED_IN INTEGER DEFAULT 0
            )
        """.trimIndent())

        db.execSQL("""
            CREATE TABLE $TABLE_FRIENDS (
                $COL_FRIEND_ID TEXT PRIMARY KEY,
                $COL_FRIEND_NAME TEXT NOT NULL,
                $COL_FRIEND_HANDLE TEXT NOT NULL UNIQUE,
                $COL_FRIEND_IS_BOARD INTEGER DEFAULT 0,
                $COL_FRIEND_STATUS TEXT DEFAULT 'offline'
            )
        """.trimIndent())

        db.execSQL("""
            CREATE TABLE $TABLE_GAMES (
                $COL_GAME_ID TEXT PRIMARY KEY,
                $COL_GAME_OPPONENT TEXT NOT NULL,
                $COL_GAME_HANDLE TEXT NOT NULL,
                $COL_GAME_PLAYER_SCORE INTEGER DEFAULT 0,
                $COL_GAME_OPP_SCORE INTEGER DEFAULT 0,
                $COL_GAME_TURN TEXT DEFAULT 'player',
                $COL_GAME_UPDATED INTEGER NOT NULL
            )
        """.trimIndent())

        // Seed initial friend: Grandma Betty's Physical Smart Board
        val cv = ContentValues().apply {
            put(COL_FRIEND_ID, "board_scb8492")
            put(COL_FRIEND_NAME, "Grandma Betty (Physical Board)")
            put(COL_FRIEND_HANDLE, "board_scb8492")
            put(COL_FRIEND_IS_BOARD, 1)
            put(COL_FRIEND_STATUS, "online")
        }
        db.insert(TABLE_FRIENDS, null, cv)
    }

    override fun onUpgrade(db: SQLiteDatabase, oldVersion: Int, newVersion: Int) {
        // Future migrations handle schema evolution without wiping user records
    }

    // User Operations
    fun saveUserProfile(profile: UserProfile, isLoggedIn: Boolean = true) {
        writableDatabase.use { db ->
            if (isLoggedIn) {
                // Ensure only one active user is marked as logged in
                val resetCv = ContentValues().apply { put(COL_USER_LOGGED_IN, 0) }
                db.update(TABLE_USERS, resetCv, null, null)
            }
            val cv = ContentValues().apply {
                put(COL_USER_ID, profile.id)
                put(COL_USER_NAME, profile.displayName)
                put(COL_USER_HANDLE, profile.uniqueUsername)
                put(COL_USER_EMAIL, profile.email)
                put(COL_USER_LOGGED_IN, if (isLoggedIn) 1 else 0)
            }
            db.insertWithOnConflict(TABLE_USERS, null, cv, SQLiteDatabase.CONFLICT_REPLACE)
        }
    }

    fun logoutAllUsers() {
        writableDatabase.use { db ->
            val cv = ContentValues().apply { put(COL_USER_LOGGED_IN, 0) }
            db.update(TABLE_USERS, cv, null, null)
        }
    }

    fun clearAllData() {
        writableDatabase.use { db ->
            db.delete(TABLE_USERS, null, null)
            db.delete(TABLE_GAMES, null, null)
            db.delete(TABLE_FRIENDS, null, null)
            // Re-seed initial board friend
            val cv = ContentValues().apply {
                put(COL_FRIEND_ID, "board_scb8492")
                put(COL_FRIEND_NAME, "Grandma Betty (Physical Board)")
                put(COL_FRIEND_HANDLE, "board_scb8492")
                put(COL_FRIEND_IS_BOARD, 1)
                put(COL_FRIEND_STATUS, "online")
            }
            db.insert(TABLE_FRIENDS, null, cv)
        }
    }

    fun getActiveUserProfile(): UserProfile? {
        readableDatabase.use { db ->
            val cursor = db.query(
                TABLE_USERS,
                null,
                "$COL_USER_LOGGED_IN = 1",
                null,
                null,
                null,
                null,
                "1"
            )
            cursor.use {
                if (it.moveToFirst()) {
                    val id = it.getString(it.getColumnIndexOrThrow(COL_USER_ID))
                    val name = it.getString(it.getColumnIndexOrThrow(COL_USER_NAME))
                    val handle = it.getString(it.getColumnIndexOrThrow(COL_USER_HANDLE))
                    val email = it.getString(it.getColumnIndexOrThrow(COL_USER_EMAIL))
                    return UserProfile(id, name, handle, email)
                }
            }
        }
        return null
    }

    // Friends Operations
    fun getAllFriends(): List<FriendRecord> {
        val list = mutableListOf<FriendRecord>()
        readableDatabase.use { db ->
            val cursor = db.query(TABLE_FRIENDS, null, null, null, null, null, "$COL_FRIEND_NAME ASC")
            cursor.use {
                while (it.moveToNext()) {
                    list.add(
                        FriendRecord(
                            id = it.getString(it.getColumnIndexOrThrow(COL_FRIEND_ID)),
                            displayName = it.getString(it.getColumnIndexOrThrow(COL_FRIEND_NAME)),
                            uniqueUsername = it.getString(it.getColumnIndexOrThrow(COL_FRIEND_HANDLE)),
                            isBoard = it.getInt(it.getColumnIndexOrThrow(COL_FRIEND_IS_BOARD)) == 1,
                            status = it.getString(it.getColumnIndexOrThrow(COL_FRIEND_STATUS))
                        )
                    )
                }
            }
        }
        return list
    }

    fun addFriend(displayName: String, uniqueUsername: String, isBoard: Boolean): Boolean {
        writableDatabase.use { db ->
            val cv = ContentValues().apply {
                put(COL_FRIEND_ID, uniqueUsername.lowercase())
                put(COL_FRIEND_NAME, displayName)
                put(COL_FRIEND_HANDLE, uniqueUsername.lowercase())
                put(COL_FRIEND_IS_BOARD, if (isBoard) 1 else 0)
                put(COL_FRIEND_STATUS, "online")
            }
            val res = db.insertWithOnConflict(TABLE_FRIENDS, null, cv, SQLiteDatabase.CONFLICT_IGNORE)
            return res != -1L
        }
    }
}

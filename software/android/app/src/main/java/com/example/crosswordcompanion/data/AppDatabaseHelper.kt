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

data class TileRecord(
    val uid: String,
    val letter: Char,
    val points: Int,
    val registeredAt: Long,
    val notes: String? = null
)

class AppDatabaseHelper(context: Context) : SQLiteOpenHelper(context, DATABASE_NAME, null, DATABASE_VERSION) {

    companion object {
        const val DATABASE_NAME = "crossword_companion.db"
        const val DATABASE_VERSION = 2

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

        // Table Tiles
        const val TABLE_TILES = "tiles"
        const val COL_TILE_UID = "uid"
        const val COL_TILE_LETTER = "letter"
        const val COL_TILE_POINTS = "points"
        const val COL_TILE_REGISTERED_AT = "registered_at"
        const val COL_TILE_NOTES = "notes"
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

        db.execSQL("""
            CREATE TABLE $TABLE_TILES (
                $COL_TILE_UID TEXT PRIMARY KEY,
                $COL_TILE_LETTER TEXT NOT NULL,
                $COL_TILE_POINTS INTEGER NOT NULL,
                $COL_TILE_REGISTERED_AT INTEGER NOT NULL,
                $COL_TILE_NOTES TEXT
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
        if (oldVersion < 2) {
            db.execSQL("""
                CREATE TABLE IF NOT EXISTS $TABLE_TILES (
                    $COL_TILE_UID TEXT PRIMARY KEY,
                    $COL_TILE_LETTER TEXT NOT NULL,
                    $COL_TILE_POINTS INTEGER NOT NULL,
                    $COL_TILE_REGISTERED_AT INTEGER NOT NULL,
                    $COL_TILE_NOTES TEXT
                )
            """.trimIndent())
        }
    }

    // User Operations
    fun saveUserProfile(profile: UserProfile, isLoggedIn: Boolean = true) {
        val db = writableDatabase
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

    fun logoutAllUsers() {
        val db = writableDatabase
        val cv = ContentValues().apply { put(COL_USER_LOGGED_IN, 0) }
        db.update(TABLE_USERS, cv, null, null)
    }

    fun clearAllData() {
        val db = writableDatabase
        db.delete(TABLE_USERS, null, null)
        db.delete(TABLE_GAMES, null, null)
        db.delete(TABLE_FRIENDS, null, null)
        db.delete(TABLE_TILES, null, null)
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

    fun getActiveUserProfile(): UserProfile? {
        val db = readableDatabase
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
        return null
    }

    // Friends Operations
    fun getAllFriends(): List<FriendRecord> {
        val list = mutableListOf<FriendRecord>()
        val db = readableDatabase
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
        return list
    }

    fun addFriend(displayName: String, uniqueUsername: String, isBoard: Boolean): Boolean {
        val db = writableDatabase
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

    // Tile Persistence Operations (Survives ESP32 reflash)
    fun saveTile(uid: String, letter: Char, points: Int, notes: String? = null): Boolean {
        return try {
            val db = writableDatabase
            val cv = ContentValues().apply {
                put(COL_TILE_UID, uid)
                put(COL_TILE_LETTER, letter.uppercaseChar().toString())
                put(COL_TILE_POINTS, points)
                put(COL_TILE_REGISTERED_AT, System.currentTimeMillis())
                put(COL_TILE_NOTES, notes)
            }
            val res = db.insertWithOnConflict(TABLE_TILES, null, cv, SQLiteDatabase.CONFLICT_REPLACE)
            res != -1L
        } catch (e: Exception) {
            false
        }
    }

    fun getAllTiles(): List<TileRecord> {
        val list = mutableListOf<TileRecord>()
        val db = readableDatabase
        val cursor = db.query(
            TABLE_TILES,
            null,
            null,
            null,
            null,
            null,
            "$COL_TILE_LETTER ASC, $COL_TILE_REGISTERED_AT DESC"
        )
        cursor.use {
            while (it.moveToNext()) {
                val uid = it.getString(it.getColumnIndexOrThrow(COL_TILE_UID))
                val letterStr = it.getString(it.getColumnIndexOrThrow(COL_TILE_LETTER))
                val points = it.getInt(it.getColumnIndexOrThrow(COL_TILE_POINTS))
                val regAt = it.getLong(it.getColumnIndexOrThrow(COL_TILE_REGISTERED_AT))
                val notes = it.getString(it.getColumnIndexOrThrow(COL_TILE_NOTES))
                val letterChar = if (letterStr.isNotEmpty()) letterStr[0] else '?'
                list.add(TileRecord(uid, letterChar, points, regAt, notes))
            }
        }
        return list
    }

    fun getTile(uid: String): TileRecord? {
        val db = readableDatabase
        val cursor = db.query(
            TABLE_TILES,
            null,
            "$COL_TILE_UID = ?",
            arrayOf(uid),
            null,
            null,
            null,
            "1"
        )
        cursor.use {
            if (it.moveToFirst()) {
                val letterStr = it.getString(it.getColumnIndexOrThrow(COL_TILE_LETTER))
                val points = it.getInt(it.getColumnIndexOrThrow(COL_TILE_POINTS))
                val regAt = it.getLong(it.getColumnIndexOrThrow(COL_TILE_REGISTERED_AT))
                val notes = it.getString(it.getColumnIndexOrThrow(COL_TILE_NOTES))
                val letterChar = if (letterStr.isNotEmpty()) letterStr[0] else '?'
                return TileRecord(uid, letterChar, points, regAt, notes)
            }
        }
        return null
    }

    fun deleteTile(uid: String): Boolean {
        return try {
            val db = writableDatabase
            val count = db.delete(TABLE_TILES, "$COL_TILE_UID = ?", arrayOf(uid))
            count > 0
        } catch (e: Exception) {
            false
        }
    }

    fun clearAllTiles(): Boolean {
        return try {
            val db = writableDatabase
            db.delete(TABLE_TILES, null, null)
            true
        } catch (e: Exception) {
            false
        }
    }

    fun getTileCount(): Int {
        val db = readableDatabase
        val cursor = db.rawQuery("SELECT COUNT(*) FROM $TABLE_TILES", null)
        cursor.use {
            if (it.moveToFirst()) {
                return it.getInt(0)
            }
        }
        return 0
    }
}

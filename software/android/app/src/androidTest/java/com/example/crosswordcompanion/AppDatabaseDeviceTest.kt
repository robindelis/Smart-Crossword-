package com.example.crosswordcompanion

import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import com.example.crosswordcompanion.data.AppDatabaseHelper
import com.example.crosswordcompanion.model.UserProfile
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class AppDatabaseDeviceTest {

    private lateinit var dbHelper: AppDatabaseHelper

    @Before
    fun setUp() {
        val appContext = InstrumentationRegistry.getInstrumentation().targetContext
        dbHelper = AppDatabaseHelper(appContext)
        dbHelper.clearAllData()
    }

    @Test
    fun testDatabaseInitializationAndInitialSeed() {
        val friends = dbHelper.getAllFriends()
        assertEquals("Initial database must have 1 seeded board friend", 1, friends.size)
        val initialFriend = friends[0]
        assertEquals("board_scb8492", initialFriend.id)
        assertTrue("Initial friend must be physical board", initialFriend.isBoard)
        assertEquals("online", initialFriend.status)

        val activeUser = dbHelper.getActiveUserProfile()
        assertNull("Initial state must have no active logged in user", activeUser)
    }

    @Test
    fun testUserSaveAndSessionExclusivity() {
        val user1 = UserProfile(
            id = "user_101",
            displayName = "Robin",
            uniqueUsername = "robin#1234",
            email = "robin@crossword.test"
        )
        dbHelper.saveUserProfile(user1, isLoggedIn = true)

        val active1 = dbHelper.getActiveUserProfile()
        assertNotNull("Active user must not be null after save", active1)
        assertEquals("user_101", active1?.id)
        assertEquals("Robin", active1?.displayName)
        assertEquals("robin#1234", active1?.uniqueUsername)

        // Save a second user as logged in
        val user2 = UserProfile(
            id = "user_102",
            displayName = "Sarah",
            uniqueUsername = "sarah#5678",
            email = "sarah@crossword.test"
        )
        dbHelper.saveUserProfile(user2, isLoggedIn = true)

        // Verify session exclusivity: user 2 is now active, user 1 logged out
        val active2 = dbHelper.getActiveUserProfile()
        assertNotNull("Active user must not be null", active2)
        assertEquals("user_102", active2?.id)
        assertEquals("Sarah", active2?.displayName)
        assertEquals("sarah#5678", active2?.uniqueUsername)
    }

    @Test
    fun testLogoutAllUsers() {
        val user = UserProfile(
            id = "user_logout_test",
            displayName = "Tester",
            uniqueUsername = "tester#9999",
            email = "tester@test.com"
        )
        dbHelper.saveUserProfile(user, isLoggedIn = true)
        assertNotNull(dbHelper.getActiveUserProfile())

        dbHelper.logoutAllUsers()
        assertNull("Active user must be null after logoutAllUsers", dbHelper.getActiveUserProfile())
    }

    @Test
    fun testAddAndRetrieveFriends() {
        val success = dbHelper.addFriend(
            displayName = "Grandpa Bob",
            uniqueUsername = "bob#4321",
            isBoard = false
        )
        assertTrue("Adding friend must succeed", success)

        val allFriends = dbHelper.getAllFriends()
        assertEquals("Must now have 2 friends", 2, allFriends.size)

        val bob = allFriends.find { it.uniqueUsername == "bob#4321" }
        assertNotNull("Grandpa Bob must exist in friends list", bob)
        assertEquals("Grandpa Bob", bob?.displayName)
        assertEquals(false, bob?.isBoard)
    }

    @Test
    fun testClearAllData() {
        dbHelper.saveUserProfile(
            UserProfile("u_temp", "Temp", "temp#0001", "temp@test.com"),
            isLoggedIn = true
        )
        dbHelper.addFriend("Extra Friend", "extra#1111", isBoard = false)

        dbHelper.clearAllData()

        assertNull("Users must be cleared", dbHelper.getActiveUserProfile())
        val friends = dbHelper.getAllFriends()
        assertEquals("Friends must be reset to initial seed (1 board)", 1, friends.size)
        assertEquals("board_scb8492", friends[0].id)
        assertEquals("Tiles must be cleared by clearAllData", 0, dbHelper.getTileCount())
    }

    @Test
    fun testSaveAndRetrieveTiles() {
        assertEquals("Initial tile count must be 0", 0, dbHelper.getTileCount())

        val saved = dbHelper.saveTile("04:A1:B2:C3:D4:E5:10", 'A', 1, "Tile 1")
        assertTrue("Saving tile must return true", saved)
        assertEquals(1, dbHelper.getTileCount())

        val retrieved = dbHelper.getTile("04:A1:B2:C3:D4:E5:10")
        assertNotNull("Retrieved tile must not be null", retrieved)
        assertEquals("04:A1:B2:C3:D4:E5:10", retrieved?.uid)
        assertEquals('A', retrieved?.letter)
        assertEquals(1, retrieved?.points)
        assertEquals("Tile 1", retrieved?.notes)
        assertTrue(retrieved!!.registeredAt > 0)
    }

    @Test
    fun testTileUpdateConflictReplace() {
        dbHelper.saveTile("04:A1:B2:C3:D4:E5:10", 'A', 1)
        // Update to 'Z' (10 points) with same UID
        dbHelper.saveTile("04:A1:B2:C3:D4:E5:10", 'Z', 10, "Updated to Z")

        assertEquals(1, dbHelper.getTileCount())
        val tile = dbHelper.getTile("04:A1:B2:C3:D4:E5:10")
        assertNotNull(tile)
        assertEquals('Z', tile?.letter)
        assertEquals(10, tile?.points)
        assertEquals("Updated to Z", tile?.notes)
    }

    @Test
    fun testDeleteTile() {
        dbHelper.saveTile("04:11:22:33:44:55:66", 'B', 3)
        dbHelper.saveTile("04:AA:BB:CC:DD:EE:FF", 'C', 3)
        assertEquals(2, dbHelper.getTileCount())

        val deleted = dbHelper.deleteTile("04:11:22:33:44:55:66")
        assertTrue("Deleting tile should succeed", deleted)
        assertEquals(1, dbHelper.getTileCount())
        assertNull(dbHelper.getTile("04:11:22:33:44:55:66"))
        assertNotNull(dbHelper.getTile("04:AA:BB:CC:DD:EE:FF"))
    }

    @Test
    fun testClearAllTiles() {
        dbHelper.saveTile("UID_1", 'A', 1)
        dbHelper.saveTile("UID_2", 'B', 3)
        dbHelper.saveTile("UID_3", 'C', 3)
        assertEquals(3, dbHelper.getTileCount())

        val cleared = dbHelper.clearAllTiles()
        assertTrue("clearAllTiles should return true", cleared)
        assertEquals(0, dbHelper.getTileCount())
        assertTrue(dbHelper.getAllTiles().isEmpty())
    }
}

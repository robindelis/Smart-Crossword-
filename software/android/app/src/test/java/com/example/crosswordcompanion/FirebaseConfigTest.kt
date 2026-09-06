package com.example.crosswordcompanion

import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.File

class FirebaseConfigTest {

    @Test
    fun testGoogleServicesJsonContainsValidOAuthClients() {
        val jsonFile = File("google-services.json")
        assertTrue("google-services.json must exist in app module", jsonFile.exists())

        val jsonContent = jsonFile.readText()

        // 1. Verify Project Information
        assertTrue("Must contain project_id smart-crossword-2177f", jsonContent.contains("\"project_id\": \"smart-crossword-2177f\""))
        assertTrue("Must contain project_number 810714924778", jsonContent.contains("\"project_number\": \"810714924778\""))

        // 2. Verify Package Name
        assertTrue("Must contain package_name com.example.crosswordcompanion", jsonContent.contains("\"package_name\": \"com.example.crosswordcompanion\""))

        // 3. Verify Android Client with SHA-1
        assertTrue("Must contain client_type 1 (Android)", jsonContent.contains("\"client_type\": 1"))
        assertTrue(
            "Must contain debug certificate_hash 935f39f96f9a7f6cb92c72aae06b1c7b56d14753",
            jsonContent.contains("\"certificate_hash\": \"935f39f96f9a7f6cb92c72aae06b1c7b56d14753\"")
        )

        // 4. Verify Web Client ID for Google Auth
        assertTrue("Must contain client_type 3 (Web client)", jsonContent.contains("\"client_type\": 3"))
        assertTrue(
            "Must contain Web client ID ending with .apps.googleusercontent.com",
            jsonContent.contains("810714924778-6jktq4hnuh4bi4q0inbt13ccfvuvb521.apps.googleusercontent.com")
        )
    }

    @Test
    fun testGeneratedGoogleServicesValuesXmlContainsDefaultWebClientId() {
        val generatedXmlFile = File("build/generated/res/processDebugGoogleServices/values/values.xml")
        if (generatedXmlFile.exists()) {
            val xmlText = generatedXmlFile.readText()
            assertTrue("Generated values.xml must define default_web_client_id", xmlText.contains("default_web_client_id"))
            assertTrue("Generated values.xml must contain the 810714924778 client prefix", xmlText.contains("810714924778-"))
            assertTrue("Generated values.xml must contain smart-crossword-2177f", xmlText.contains("smart-crossword-2177f"))
        }
    }
}

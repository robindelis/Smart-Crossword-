package com.example.crosswordcompanion.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.crosswordcompanion.data.AppDatabaseHelper
import com.example.crosswordcompanion.model.UniqueUsernameGenerator
import com.example.crosswordcompanion.model.UserProfile

@Composable
fun AuthScreen(
    onAuthenticated: (UserProfile) -> Unit,
    modifier: Modifier = Modifier
) {
    val context = LocalContext.current
    val dbHelper = remember { AppDatabaseHelper(context) }
    var inputName by remember { mutableStateOf("Sarah") }

    Column(
        modifier = modifier
            .fillMaxSize()
            .background(Color(0xFFF9F6F0))
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        // App Wooden Tile Icon Mockup
        Box(
            modifier = Modifier
                .size(72.dp)
                .shadow(6.dp, RoundedCornerShape(12.dp))
                .clip(RoundedCornerShape(12.dp))
                .background(Color(0xFFFFD54F)),
            contentAlignment = Alignment.Center
        ) {
            Text(
                text = "S",
                fontSize = 42.sp,
                fontWeight = FontWeight.Black,
                color = Color(0xFF3E2723)
            )
            Text(
                text = "1",
                fontSize = 14.sp,
                fontWeight = FontWeight.Bold,
                color = Color(0xFF5D4037),
                modifier = Modifier
                    .align(Alignment.BottomEnd)
                    .padding(end = 6.dp, bottom = 4.dp)
            )
        }

        Spacer(modifier = Modifier.height(16.dp))

        Text(
            text = "Smart Crossword",
            fontSize = 26.sp,
            fontWeight = FontWeight.Black,
            color = Color(0xFF2C1810)
        )
        Text(
            text = "Companion App for Family & Friends",
            fontSize = 14.sp,
            color = Color(0xFF6D4C41),
            textAlign = TextAlign.Center
        )

        Spacer(modifier = Modifier.height(32.dp))

        // Profile Setup Card
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = Color.White),
            shape = RoundedCornerShape(16.dp),
            elevation = CardDefaults.cardElevation(defaultElevation = 3.dp)
        ) {
            Column(modifier = Modifier.padding(20.dp)) {
                Text(
                    text = "Player Profile",
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color(0xFF3E2723)
                )
                Spacer(modifier = Modifier.height(8.dp))

                OutlinedTextField(
                    value = inputName,
                    onValueChange = { inputName = it },
                    label = { Text("Your Display Name") },
                    singleLine = true,
                    modifier = Modifier.fillMaxWidth()
                )

                Spacer(modifier = Modifier.height(16.dp))

                // 1-Tap Quick Start (Generates Unique Username)
                Button(
                    onClick = {
                        val name = if (inputName.trim().isEmpty()) "Player" else inputName.trim()
                        val handle = UniqueUsernameGenerator.generate(name)
                        val profile = UserProfile(
                            id = java.util.UUID.randomUUID().toString(),
                            displayName = name,
                            uniqueUsername = handle,
                            email = "$name@smartcrossword.local"
                        )
                        dbHelper.saveUserProfile(profile, isLoggedIn = true)
                        onAuthenticated(profile)
                    },
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(48.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF5D4037)),
                    shape = RoundedCornerShape(10.dp)
                ) {
                    Text(
                        text = "Instant 1-Tap Play",
                        fontWeight = FontWeight.Bold,
                        fontSize = 15.sp
                    )
                }

                Spacer(modifier = Modifier.height(12.dp))

                // Google Sign-In Button
                OutlinedButton(
                    onClick = {
                        // Hook ready for Firebase Google Sign-In credentials
                        val name = if (inputName.trim().isEmpty()) "Google User" else inputName.trim()
                        val handle = UniqueUsernameGenerator.generate(name)
                        val profile = UserProfile(
                            id = "google_" + java.util.UUID.randomUUID().toString().take(8),
                            displayName = name,
                            uniqueUsername = handle,
                            email = "$name@gmail.com"
                        )
                        dbHelper.saveUserProfile(profile, isLoggedIn = true)
                        onAuthenticated(profile)
                    },
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(48.dp),
                    shape = RoundedCornerShape(10.dp),
                    colors = ButtonDefaults.outlinedButtonColors(contentColor = Color(0xFF2C1810))
                ) {
                    Text(
                        text = "🌐 Connect with Google Account",
                        fontWeight = FontWeight.SemiBold,
                        fontSize = 14.sp
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(20.dp))

        Text(
            text = "Unique usernames (e.g. sarah#4821) allow physical board and phone players to pair instantly.",
            fontSize = 12.sp,
            color = Color(0xFF8D6E63),
            textAlign = TextAlign.Center,
            modifier = Modifier.padding(horizontal = 16.dp)
        )
    }
}

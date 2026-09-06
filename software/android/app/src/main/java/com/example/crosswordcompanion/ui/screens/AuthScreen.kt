package com.example.crosswordcompanion.ui.screens

import android.util.Log
import android.widget.Toast
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.Image
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
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.crosswordcompanion.R
import com.example.crosswordcompanion.data.AppDatabaseHelper
import com.example.crosswordcompanion.model.UniqueUsernameGenerator
import com.example.crosswordcompanion.model.UserProfile
import com.google.android.gms.auth.api.signin.GoogleSignIn
import com.google.android.gms.auth.api.signin.GoogleSignInOptions
import com.google.android.gms.common.api.ApiException
import com.google.firebase.auth.FirebaseAuth
import com.google.firebase.auth.GoogleAuthProvider

@Composable
fun AuthScreen(
    onAuthenticated: (UserProfile) -> Unit,
    modifier: Modifier = Modifier
) {
    val context = LocalContext.current
    val dbHelper = remember { AppDatabaseHelper(context) }
    var inputName by remember { mutableStateOf("Sarah") }
    var authError by remember { mutableStateOf<String?>(null) }
    var isLoading by remember { mutableStateOf(false) }

    // Check if Firebase Web Client ID is available from google-services.json
    val webClientIdResId = remember {
        context.resources.getIdentifier("default_web_client_id", "string", context.packageName)
    }
    val webClientId = remember(webClientIdResId) {
        if (webClientIdResId != 0) context.getString(webClientIdResId) else null
    }

    // Google Sign-In Activity Result Launcher
    val googleSignInLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.StartActivityForResult()
    ) { result ->
        isLoading = false
        val task = GoogleSignIn.getSignedInAccountFromIntent(result.data)
        try {
            val account = task.getResult(ApiException::class.java)
            val idToken = account?.idToken
            if (idToken != null) {
                isLoading = true
                val credential = GoogleAuthProvider.getCredential(idToken, null)
                FirebaseAuth.getInstance().signInWithCredential(credential)
                    .addOnSuccessListener { authResult ->
                        isLoading = false
                        val firebaseUser = authResult.user
                        val name = firebaseUser?.displayName ?: account.displayName ?: "Player"
                        val email = firebaseUser?.email ?: account.email ?: ""
                        val uid = firebaseUser?.uid ?: "google_${account.id}"
                        val handle = UniqueUsernameGenerator.generate(name)
                        val profile = UserProfile(
                            id = uid,
                            displayName = name,
                            uniqueUsername = handle,
                            email = email
                        )
                        dbHelper.saveUserProfile(profile, isLoggedIn = true)
                        onAuthenticated(profile)
                    }
                    .addOnFailureListener { e ->
                        isLoading = false
                        authError = "Firebase Auth error: ${e.localizedMessage}"
                        Log.e("AuthScreen", "Firebase Auth sign-in failed", e)
                    }
            } else {
                authError = "Google account did not return an ID token."
            }
        } catch (e: ApiException) {
            isLoading = false
            Log.e("AuthScreen", "Google Sign-In failed with status code ${e.statusCode}", e)
            authError = when (e.statusCode) {
                10 -> "Configuration error (code 10): Ensure SHA-1 is added to Firebase Console."
                12500 -> "Sign-in error (code 12500): Check Google Play Services or network."
                12501 -> "Sign-in cancelled by user."
                else -> "Sign-in error: ${e.localizedMessage ?: "code ${e.statusCode}"}"
            }
        }
    }

    Column(
        modifier = modifier
            .fillMaxSize()
            .background(Color(0xFFF9F6F0))
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        // App Wooden Tile Icon
        Image(
            painter = painterResource(id = R.drawable.app_icon),
            contentDescription = "Smart Crossword Tile Icon",
            modifier = Modifier
                .size(84.dp)
                .shadow(8.dp, RoundedCornerShape(16.dp))
                .clip(RoundedCornerShape(16.dp))
        )

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
                        authError = null
                        if (webClientId == null) {
                            authError = "Google Auth is waiting for updated google-services.json with Web Client ID. Please re-download it from Firebase Console after adding SHA-1."
                        } else {
                            try {
                                val gso = GoogleSignInOptions.Builder(GoogleSignInOptions.DEFAULT_SIGN_IN)
                                    .requestIdToken(webClientId)
                                    .requestEmail()
                                    .build()
                                val client = GoogleSignIn.getClient(context, gso)
                                isLoading = true
                                googleSignInLauncher.launch(client.signInIntent)
                            } catch (e: Exception) {
                                isLoading = false
                                authError = "Failed to launch Google Sign-In: ${e.localizedMessage}"
                            }
                        }
                    },
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(48.dp),
                    shape = RoundedCornerShape(10.dp),
                    colors = ButtonDefaults.outlinedButtonColors(contentColor = Color(0xFF2C1810)),
                    enabled = !isLoading
                ) {
                    if (isLoading) {
                        CircularProgressIndicator(
                            modifier = Modifier.size(20.dp),
                            strokeWidth = 2.dp,
                            color = Color(0xFF5D4037)
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text("Connecting to Google...", fontSize = 14.sp)
                    } else {
                        Text(
                            text = "🌐 Connect with Google Account",
                            fontWeight = FontWeight.SemiBold,
                            fontSize = 14.sp
                        )
                    }
                }

                if (authError != null) {
                    Spacer(modifier = Modifier.height(12.dp))
                    Card(
                        colors = CardDefaults.cardColors(containerColor = Color(0xFFFFEBEE)),
                        shape = RoundedCornerShape(8.dp),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text(
                            text = authError!!,
                            color = Color(0xFFC62828),
                            fontSize = 12.sp,
                            modifier = Modifier.padding(10.dp)
                        )
                    }
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

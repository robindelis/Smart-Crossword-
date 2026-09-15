package com.example.crosswordcompanion

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import android.Manifest
import android.content.pm.PackageManager
import android.os.Build
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.core.content.ContextCompat
import com.example.crosswordcompanion.bluetooth.BleManager
import com.example.crosswordcompanion.data.AppDatabaseHelper
import com.example.crosswordcompanion.model.UserProfile
import com.example.crosswordcompanion.theme.CrosswordCompanionTheme
import com.example.crosswordcompanion.ui.screens.AuthScreen
import com.example.crosswordcompanion.ui.screens.Board4x4Screen
import com.example.crosswordcompanion.ui.screens.FriendsScreen
import com.example.crosswordcompanion.ui.screens.HardwareDebugScreen

enum class AppTab(val title: String) {
    BOARD_4X4("4x4 Board"),
    FRIENDS("Friends & Boards"),
    DEBUG("Hardware Debug"),
    PROFILE("Profile")
}

class MainActivity : ComponentActivity() {
    @OptIn(ExperimentalMaterial3Api::class)
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        setContent {
            CrosswordCompanionTheme {
                val context = LocalContext.current
                val dbHelper = remember { AppDatabaseHelper(context) }
                val bleManager = remember { BleManager.getInstance(context) }
                var currentUser by remember { mutableStateOf<UserProfile?>(dbHelper.getActiveUserProfile()) }
                var selectedTab by remember { mutableStateOf(AppTab.BOARD_4X4) }
                var activeOpponent by remember { mutableStateOf("Grandma Betty (Board)") }

                val permissionLauncher = rememberLauncherForActivityResult(
                    ActivityResultContracts.RequestMultiplePermissions()
                ) { permissions ->
                    if (permissions.values.all { it }) {
                        bleManager.startScan()
                    }
                }

                LaunchedEffect(Unit) {
                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                        val hasScan = ContextCompat.checkSelfPermission(context, Manifest.permission.BLUETOOTH_SCAN) == PackageManager.PERMISSION_GRANTED
                        val hasConnect = ContextCompat.checkSelfPermission(context, Manifest.permission.BLUETOOTH_CONNECT) == PackageManager.PERMISSION_GRANTED
                        if (hasScan && hasConnect) {
                            bleManager.startScan()
                        } else {
                            permissionLauncher.launch(arrayOf(Manifest.permission.BLUETOOTH_SCAN, Manifest.permission.BLUETOOTH_CONNECT))
                        }
                    } else {
                        val hasLocation = ContextCompat.checkSelfPermission(context, Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED
                        if (hasLocation) {
                            bleManager.startScan()
                        } else {
                            permissionLauncher.launch(arrayOf(Manifest.permission.ACCESS_FINE_LOCATION))
                        }
                    }
                }

                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = Color(0xFFF9F6F0)
                ) {
                    if (currentUser == null) {
                        AuthScreen(
                            onAuthenticated = { profile ->
                                currentUser = profile
                                selectedTab = AppTab.BOARD_4X4
                            },
                            modifier = Modifier.safeDrawingPadding()
                        )
                    } else {
                        Scaffold(
                            modifier = Modifier.safeDrawingPadding(),
                            topBar = {
                                CenterAlignedTopAppBar(
                                    title = {
                                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                                            Text(
                                                text = "Smart Crossword",
                                                fontWeight = FontWeight.Black,
                                                fontSize = 18.sp,
                                                color = Color(0xFF2C1810)
                                            )
                                            Text(
                                                text = "4x4 Hardware Test Edition",
                                                fontSize = 11.sp,
                                                color = Color(0xFF6D4C41)
                                            )
                                        }
                                    },
                                    colors = TopAppBarDefaults.topAppBarColors(
                                        containerColor = Color(0xFFEFEBE9)
                                    )
                                )
                            },
                            bottomBar = {
                                NavigationBar(
                                    containerColor = Color(0xFFEFEBE9)
                                ) {
                                    NavigationBarItem(
                                        selected = selectedTab == AppTab.BOARD_4X4,
                                        onClick = { selectedTab = AppTab.BOARD_4X4 },
                                        label = { Text("Play 4x4") },
                                        icon = { Text("🎲", fontSize = 18.sp) }
                                    )
                                    NavigationBarItem(
                                        selected = selectedTab == AppTab.FRIENDS,
                                        onClick = { selectedTab = AppTab.FRIENDS },
                                        label = { Text("Friends") },
                                        icon = { Text("👥", fontSize = 18.sp) }
                                    )
                                    NavigationBarItem(
                                        selected = selectedTab == AppTab.DEBUG,
                                        onClick = { selectedTab = AppTab.DEBUG },
                                        label = { Text("Debug") },
                                        icon = { Text("🛠️", fontSize = 18.sp) }
                                    )
                                    NavigationBarItem(
                                        selected = selectedTab == AppTab.PROFILE,
                                        onClick = { selectedTab = AppTab.PROFILE },
                                        label = { Text("Account") },
                                        icon = { Text("👤", fontSize = 18.sp) }
                                    )
                                }
                            }
                        ) { innerPadding ->
                            when (selectedTab) {
                                AppTab.BOARD_4X4 -> {
                                    Board4x4Screen(
                                        playerName = currentUser!!.displayName,
                                        opponentName = activeOpponent,
                                        bleManager = bleManager,
                                        modifier = Modifier.padding(innerPadding)
                                    )
                                }
                                AppTab.FRIENDS -> {
                                    FriendsScreen(
                                        userHandle = currentUser!!.uniqueUsername,
                                        displayName = currentUser!!.displayName,
                                        onPlayAgainst = { opponent ->
                                            activeOpponent = opponent
                                            selectedTab = AppTab.BOARD_4X4
                                        },
                                        modifier = Modifier.padding(innerPadding)
                                    )
                                }
                                AppTab.DEBUG -> {
                                    HardwareDebugScreen(
                                        bleManager = bleManager,
                                        modifier = Modifier.padding(innerPadding)
                                    )
                                }
                                AppTab.PROFILE -> {
                                    Column(
                                        modifier = Modifier
                                            .padding(innerPadding)
                                            .fillMaxSize()
                                            .padding(24.dp),
                                        horizontalAlignment = Alignment.CenterHorizontally
                                    ) {
                                        Card(
                                            modifier = Modifier.fillMaxWidth(),
                                            colors = CardDefaults.cardColors(containerColor = Color.White),
                                            shape = RoundedCornerShape(12.dp)
                                        ) {
                                            Column(modifier = Modifier.padding(16.dp)) {
                                                Text(
                                                    text = "Profile Settings",
                                                    fontWeight = FontWeight.Bold,
                                                    fontSize = 18.sp,
                                                    color = Color(0xFF3E2723)
                                                )
                                                Spacer(modifier = Modifier.height(10.dp))
                                                Text("Display Name: ${currentUser!!.displayName}", fontSize = 15.sp)
                                                Text("Unique Handle: ${currentUser!!.uniqueUsername}", fontWeight = FontWeight.SemiBold, fontSize = 15.sp, color = Color(0xFF6D4C41))
                                                Text("Email: ${currentUser!!.email ?: "N/A"}", fontSize = 14.sp, color = Color.Gray)
                                                Spacer(modifier = Modifier.height(16.dp))
                                                Button(
                                                    onClick = {
                                                        dbHelper.logoutAllUsers()
                                                        currentUser = null
                                                    },
                                                    colors = ButtonDefaults.buttonColors(containerColor = Color(0xFFD32F2F)),
                                                    modifier = Modifier.fillMaxWidth()
                                                ) {
                                                    Text("Switch Player / Sign Out")
                                                }
                                                Spacer(modifier = Modifier.height(10.dp))
                                                OutlinedButton(
                                                    onClick = {
                                                        dbHelper.clearAllData()
                                                        currentUser = null
                                                    },
                                                    colors = ButtonDefaults.outlinedButtonColors(contentColor = Color(0xFFC62828)),
                                                    modifier = Modifier.fillMaxWidth()
                                                ) {
                                                    Text("🗑️ Reset & Clear Local Database")
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

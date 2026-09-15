package com.example.crosswordcompanion.ui.screens

import android.Manifest
import android.content.pm.PackageManager
import android.os.Build
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
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
import androidx.core.content.ContextCompat
import com.example.crosswordcompanion.bluetooth.BleConnectionState
import com.example.crosswordcompanion.bluetooth.BleManager
import com.example.crosswordcompanion.bluetooth.BleProtocol

private fun getScrabbleLetterPoints(c: Char): Int {
    return when (c.uppercaseChar()) {
        'A', 'E', 'I', 'O', 'U', 'L', 'N', 'S', 'T', 'R' -> 1
        'D', 'G' -> 2
        'B', 'C', 'M', 'P' -> 3
        'F', 'H', 'V', 'W', 'Y' -> 4
        'K' -> 5
        'J', 'X' -> 8
        'Q', 'Z' -> 10
        else -> 0
    }
}

@Composable
fun HardwareDebugScreen(
    bleManager: BleManager,
    modifier: Modifier = Modifier
) {
    val context = LocalContext.current
    val connectionState by bleManager.connectionState.collectAsState()
    val telemetry by bleManager.scanTelemetry.collectAsState()
    val boardState by bleManager.boardState.collectAsState()

    var autoReconnect by remember { mutableStateOf(bleManager.autoReconnectEnabled) }
    var selectedLetter by remember { mutableStateOf('A') }
    var enrollmentMessage by remember { mutableStateOf<String?>(null) }
    var lastEnrolledUid by remember { mutableStateOf<String?>(null) }

    val activeChannel = telemetry.activeChannel ?: 0

    // Permissions launcher
    val permissionLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { permissions ->
        if (permissions.values.all { it }) {
            bleManager.startScan()
        }
    }

    fun requestBlePermissionsAndScan() {
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

    Column(
        modifier = modifier
            .fillMaxSize()
            .background(Color(0xFFF9F6F0))
            .verticalScroll(rememberScrollState())
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        // --- 1. Connection & Auto-Reconnect Header ---
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(
                containerColor = when (connectionState) {
                    is BleConnectionState.Connected -> Color(0xFFE8F5E9)
                    is BleConnectionState.Scanning, is BleConnectionState.Connecting -> Color(0xFFFFF8E1)
                    is BleConnectionState.Error -> Color(0xFFFFEBEE)
                    else -> Color(0xFFECEFF1)
                }
            ),
            shape = RoundedCornerShape(12.dp),
            elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
        ) {
            Column(modifier = Modifier.padding(14.dp)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text(
                            text = when (connectionState) {
                                is BleConnectionState.Connected -> "🟢"
                                is BleConnectionState.Scanning -> "🟡"
                                is BleConnectionState.Connecting -> "⏳"
                                is BleConnectionState.Error -> "⚠️"
                                else -> "⚪"
                            },
                            fontSize = 18.sp,
                            modifier = Modifier.padding(end = 8.dp)
                        )
                        Column {
                            Text(
                                text = when (connectionState) {
                                    is BleConnectionState.Connected -> "Board Connected"
                                    is BleConnectionState.Scanning -> "Searching for Board..."
                                    is BleConnectionState.Connecting -> "Connecting..."
                                    is BleConnectionState.Error -> "Connection Error"
                                    else -> "Board Disconnected"
                                },
                                fontWeight = FontWeight.Bold,
                                fontSize = 14.sp,
                                color = Color(0xFF263238)
                            )
                            Text(
                                text = "Device: ${BleProtocol.DEVICE_NAME}",
                                fontSize = 11.sp,
                                color = Color(0xFF546E7A)
                            )
                        }
                    }

                    Row(verticalAlignment = Alignment.CenterVertically) {
                        if (connectionState is BleConnectionState.Connected) {
                            OutlinedButton(
                                onClick = { bleManager.disconnect() },
                                shape = RoundedCornerShape(6.dp),
                                contentPadding = PaddingValues(horizontal = 8.dp, vertical = 2.dp),
                                modifier = Modifier.height(30.dp)
                            ) {
                                Text("Disconnect", fontSize = 11.sp)
                            }
                        } else {
                            Button(
                                onClick = { requestBlePermissionsAndScan() },
                                shape = RoundedCornerShape(6.dp),
                                contentPadding = PaddingValues(horizontal = 10.dp, vertical = 2.dp),
                                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF455A64)),
                                modifier = Modifier.height(30.dp)
                            ) {
                                Text("Scan / Connect", fontSize = 11.sp, fontWeight = FontWeight.Bold)
                            }
                        }
                    }
                }

                Spacer(modifier = Modifier.height(8.dp))
                HorizontalDivider(color = Color(0x1F000000))
                Spacer(modifier = Modifier.height(8.dp))

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "Auto-Reconnect in Background",
                        fontSize = 12.sp,
                        fontWeight = FontWeight.Medium,
                        color = Color(0xFF37474F)
                    )
                    Switch(
                        checked = autoReconnect,
                        onCheckedChange = {
                            autoReconnect = it
                            bleManager.autoReconnectEnabled = it
                            if (it && connectionState is BleConnectionState.Disconnected) {
                                bleManager.startScan()
                            }
                        },
                        modifier = Modifier.scale(0.8f)
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // --- 2. Channel Matrix Power Controller ---
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = Color.White),
            shape = RoundedCornerShape(12.dp),
            elevation = CardDefaults.cardElevation(defaultElevation = 3.dp)
        ) {
            Column(modifier = Modifier.padding(14.dp)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text(
                            text = "⚡ Coil Power & Channel Matrix",
                            fontWeight = FontWeight.Bold,
                            fontSize = 15.sp,
                            color = Color(0xFF3E2723)
                        )
                        Text(
                            text = "Tap any square to route RF power directly to that coil",
                            fontSize = 11.sp,
                            color = Color(0xFF6D4C41)
                        )
                    }
                    Badge(containerColor = Color(0xFFFFD54F)) {
                        Text(
                            text = "Active: Ch $activeChannel",
                            color = Color(0xFF3E2723),
                            fontWeight = FontWeight.Bold,
                            fontSize = 11.sp
                        )
                    }
                }

                Spacer(modifier = Modifier.height(12.dp))

                // 4x4 Grid of channel selection buttons
                for (r in 0 until 4) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(vertical = 2.dp),
                        horizontalArrangement = Arrangement.spacedBy(6.dp)
                    ) {
                        for (c in 0 until 4) {
                            val ch = r * 4 + c
                            val isPowered = ch == activeChannel
                            val hasTile = boardState.containsKey(ch)
                            val tileChar = boardState[ch]

                            Box(
                                modifier = Modifier
                                    .weight(1f)
                                    .height(48.dp)
                                    .clip(RoundedCornerShape(8.dp))
                                    .background(
                                        when {
                                            isPowered -> Color(0xFFFFE082)
                                            hasTile -> Color(0xFFD7CCC8)
                                            else -> Color(0xFFECEFF1)
                                        }
                                    )
                                    .border(
                                        width = if (isPowered) 2.5.dp else 1.dp,
                                        color = if (isPowered) Color(0xFFE65100) else Color(0x22000000),
                                        shape = RoundedCornerShape(8.dp)
                                    )
                                    .clickable {
                                        bleManager.selectChannel(ch)
                                    },
                                contentAlignment = Alignment.Center
                            ) {
                                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                                    Text(
                                        text = if (isPowered) "⚡ $ch" else "$ch",
                                        fontWeight = FontWeight.Bold,
                                        fontSize = 13.sp,
                                        color = if (isPowered) Color(0xFFBF360C) else Color(0xFF37474F)
                                    )
                                    Text(
                                        text = if (hasTile) "[$tileChar]" else "R$r,C$c",
                                        fontSize = 9.sp,
                                        fontWeight = if (hasTile) FontWeight.Black else FontWeight.Normal,
                                        color = if (hasTile) Color(0xFF1B5E20) else Color(0xFF78909C)
                                    )
                                }
                            }
                        }
                    }
                }

                Spacer(modifier = Modifier.height(10.dp))

                // Quick Step & MUX Control Buttons
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(6.dp)
                ) {
                    OutlinedButton(
                        onClick = {
                            val prev = (activeChannel + 15) % 16
                            bleManager.selectChannel(prev)
                        },
                        modifier = Modifier.weight(1f),
                        contentPadding = PaddingValues(4.dp),
                        shape = RoundedCornerShape(8.dp)
                    ) {
                        Text("◀ Prev", fontSize = 11.sp)
                    }

                    OutlinedButton(
                        onClick = {
                            val next = (activeChannel + 1) % 16
                            bleManager.selectChannel(next)
                        },
                        modifier = Modifier.weight(1f),
                        contentPadding = PaddingValues(4.dp),
                        shape = RoundedCornerShape(8.dp)
                    ) {
                        Text("Next ▶", fontSize = 11.sp)
                    }

                    OutlinedButton(
                        onClick = { bleManager.toggleMux() },
                        modifier = Modifier.weight(1.1f),
                        contentPadding = PaddingValues(4.dp),
                        shape = RoundedCornerShape(8.dp)
                    ) {
                        Text("Toggle MUX", fontSize = 11.sp)
                    }

                    Button(
                        onClick = { bleManager.triggerSweep() },
                        colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF00897B)),
                        modifier = Modifier.weight(1.2f),
                        contentPadding = PaddingValues(4.dp),
                        shape = RoundedCornerShape(8.dp)
                    ) {
                        Text("⚡ Sweep All", fontSize = 11.sp, fontWeight = FontWeight.Bold)
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // --- 3. Piece Registration Studio ---
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = Color.White),
            shape = RoundedCornerShape(12.dp),
            elevation = CardDefaults.cardElevation(defaultElevation = 3.dp)
        ) {
            Column(modifier = Modifier.padding(14.dp)) {
                Text(
                    text = "🏷️ Piece Registration Studio",
                    fontWeight = FontWeight.Bold,
                    fontSize = 15.sp,
                    color = Color(0xFF3E2723)
                )
                Text(
                    text = "Enroll NFC tags on the active square as tournament Scrabble tiles",
                    fontSize = 11.sp,
                    color = Color(0xFF6D4C41)
                )

                Spacer(modifier = Modifier.height(10.dp))

                // Tag presence card
                val hasTagDetected = (telemetry.status == BleProtocol.STATUS_TAG_DETECTED) && !telemetry.tagUid.isNullOrBlank()
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(
                        containerColor = if (hasTagDetected) Color(0xFFE8F5E9) else Color(0xFFFFF8E1)
                    ),
                    shape = RoundedCornerShape(8.dp)
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(12.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = if (hasTagDetected) "🎯" else "⏳",
                            fontSize = 22.sp,
                            modifier = Modifier.padding(end = 10.dp)
                        )
                        Column(modifier = Modifier.weight(1f)) {
                            Text(
                                text = if (hasTagDetected) "Tag Detected on Square $activeChannel!" else "Waiting for Tag on Square $activeChannel...",
                                fontWeight = FontWeight.Bold,
                                fontSize = 13.sp,
                                color = if (hasTagDetected) Color(0xFF2E7D32) else Color(0xFFE65100)
                            )
                            if (hasTagDetected && telemetry.tagUid != null) {
                                Text(
                                    text = "UID: ${telemetry.tagUid}",
                                    fontWeight = FontWeight.SemiBold,
                                    fontSize = 12.sp,
                                    color = Color(0xFF1B5E20)
                                )
                            } else {
                                Text(
                                    text = "Place an NFC sticker or Scrabble tile on the active square to enable registration.",
                                    fontSize = 11.sp,
                                    color = Color(0xFF78909C)
                                )
                            }
                            val currentAssigned = boardState[activeChannel]
                            if (currentAssigned != null) {
                                Text(
                                    text = "Currently Enrolled: Letter '$currentAssigned' (${getScrabbleLetterPoints(currentAssigned)} pts)",
                                    fontSize = 11.sp,
                                    fontWeight = FontWeight.Medium,
                                    color = Color(0xFF37474F)
                                )
                            }
                        }
                    }
                }

                if (enrollmentMessage != null) {
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = enrollmentMessage!!,
                        color = Color(0xFF2E7D32),
                        fontWeight = FontWeight.Bold,
                        fontSize = 12.sp
                    )
                }

                Spacer(modifier = Modifier.height(12.dp))

                Text(
                    text = "Select Letter to Assign to this Tag:",
                    fontWeight = FontWeight.Bold,
                    fontSize = 12.sp,
                    color = Color(0xFF37474F)
                )

                Spacer(modifier = Modifier.height(6.dp))

                // Letter Selection Grid (A to Z)
                val letters = ('A'..'Z').toList()
                val chunkedLetters = letters.chunked(7)

                Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                    for (row in chunkedLetters) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(4.dp)
                        ) {
                            for (char in row) {
                                val isSelected = selectedLetter == char
                                Box(
                                    modifier = Modifier
                                        .weight(1f)
                                        .height(38.dp)
                                        .clip(RoundedCornerShape(6.dp))
                                        .background(if (isSelected) Color(0xFFFFB300) else Color(0xFFFFE0B2))
                                        .border(
                                            width = if (isSelected) 2.dp else 1.dp,
                                            color = if (isSelected) Color(0xFFE65100) else Color(0x33000000),
                                            shape = RoundedCornerShape(6.dp)
                                        )
                                        .clickable {
                                            selectedLetter = char
                                            enrollmentMessage = null
                                        },
                                    contentAlignment = Alignment.Center
                                ) {
                                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                                        Text(
                                            text = char.toString(),
                                            fontWeight = FontWeight.Bold,
                                            fontSize = 14.sp,
                                            color = Color(0xFF2C1810)
                                        )
                                        Text(
                                            text = "${getScrabbleLetterPoints(char)}pt",
                                            fontSize = 7.sp,
                                            color = Color(0xFF5D4037)
                                        )
                                    }
                                }
                            }
                            // Fill remaining slots in last row
                            if (row.size < 7) {
                                for (empty in 0 until (7 - row.size)) {
                                    Spacer(modifier = Modifier.weight(1f))
                                }
                            }
                        }
                    }
                }

                Spacer(modifier = Modifier.height(12.dp))

                // Enroll Button
                val isConnected = connectionState is BleConnectionState.Connected
                val canEnroll = isConnected && hasTagDetected

                Button(
                    onClick = {
                        if (!canEnroll) return@Button
                        val success = bleManager.enrollTag(activeChannel, selectedLetter)
                        if (success) {
                            lastEnrolledUid = telemetry.tagUid
                            enrollmentMessage = "✅ Enrolled Tag on Square $activeChannel as Letter '$selectedLetter' (${getScrabbleLetterPoints(selectedLetter)} pts)!"
                        } else {
                            enrollmentMessage = "⚠️ Could not send enrollment command (board not connected)."
                        }
                    },
                    enabled = canEnroll,
                    colors = ButtonDefaults.buttonColors(
                        containerColor = Color(0xFF2E7D32),
                        disabledContainerColor = Color(0xFFCFD8DC),
                        disabledContentColor = Color(0xFF78909C)
                    ),
                    shape = RoundedCornerShape(8.dp),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text(
                        text = when {
                            !isConnected -> "Connect Board to Register"
                            !hasTagDetected -> "No Tag Detected on Square $activeChannel"
                            else -> "Register Tag on Square $activeChannel as '$selectedLetter' (${getScrabbleLetterPoints(selectedLetter)} pts)"
                        },
                        fontWeight = FontWeight.Bold,
                        fontSize = 13.sp
                    )
                }
            }
        }
    }
}

private fun Modifier.scale(scale: Float): Modifier = this.then(
    Modifier.padding(0.dp)
)

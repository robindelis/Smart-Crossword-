package com.example.crosswordcompanion.ui.screens

import android.Manifest
import android.content.pm.PackageManager
import android.os.Build
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
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
import androidx.core.content.ContextCompat
import com.example.crosswordcompanion.bluetooth.BleConnectionState
import com.example.crosswordcompanion.bluetooth.BleManager
import com.example.crosswordcompanion.bluetooth.BleProtocol
import com.example.crosswordcompanion.game.EnglishReferee
import com.example.crosswordcompanion.game.RefereeResult
import com.example.crosswordcompanion.model.Board4x4
import com.example.crosswordcompanion.model.BoardCell
import com.example.crosswordcompanion.model.SquareType
import com.example.crosswordcompanion.model.Tile

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
fun Board4x4Screen(
    playerName: String = "Sarah",
    opponentName: String = "Grandma Betty (Board)",
    modifier: Modifier = Modifier
) {
    val context = LocalContext.current
    val bleManager = remember { BleManager(context) }
    val bleConnectionState by bleManager.connectionState.collectAsState()
    val scanTelemetry by bleManager.scanTelemetry.collectAsState()
    val physicalTiles by bleManager.boardState.collectAsState()

    var cells by remember { mutableStateOf(Board4x4.createDefaultLayout()) }
    var playerScore by remember { mutableIntStateOf(0) }
    var opponentScore by remember { mutableIntStateOf(0) }
    var isFirstMove by remember { mutableStateOf(true) }

    // Sample initial 7 tiles for English play
    var rackTiles by remember {
        mutableStateOf(
            listOf(
                Tile('P', 3),
                Tile('L', 1),
                Tile('A', 1),
                Tile('Y', 4),
                Tile('E', 1),
                Tile('R', 1),
                Tile('S', 1)
            )
        )
    }

    var selectedTileIndex by remember { mutableStateOf<Int?>(null) }
    var refereeResult by remember {
        mutableStateOf<RefereeResult?>(
            RefereeResult(false, 0, emptyList(), "Place tiles covering center star (★) to begin!")
        )
    }

    val referee = remember { EnglishReferee() }
    var dictionaryCount by remember { mutableIntStateOf(referee.wordCount) }

    // Pulse animation for active scanning square
    val infiniteTransition = rememberInfiniteTransition(label = "scannerPulse")
    val pulseAlpha by infiniteTransition.animateFloat(
        initialValue = 0.35f,
        targetValue = 1.0f,
        animationSpec = infiniteRepeatable(
            animation = tween(350, easing = LinearEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "pulseAlpha"
    )

    // Helper to evaluate uncommitted tiles
    fun updateRefereeEvaluation() {
        val uncommitted = cells.filter { it.tile != null && !it.isCommitted }
        refereeResult = referee.evaluateMove(cells, uncommitted, isFirstMove)
    }

    // Permission launcher for BLE
    val permissionLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { permissions ->
        val granted = permissions.values.all { it }
        if (granted) {
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
                permissionLauncher.launch(
                    arrayOf(
                        Manifest.permission.BLUETOOTH_SCAN,
                        Manifest.permission.BLUETOOTH_CONNECT
                    )
                )
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

    // Clean up BLE on dispose
    DisposableEffect(Unit) {
        onDispose {
            bleManager.disconnect()
        }
    }

    // Load Scrabble dictionary
    LaunchedEffect(Unit) {
        kotlinx.coroutines.withContext(kotlinx.coroutines.Dispatchers.IO) {
            try {
                context.assets.open("dict_en.txt").use { stream ->
                    val count = referee.loadDictionary(stream)
                    kotlinx.coroutines.withContext(kotlinx.coroutines.Dispatchers.Main) {
                        dictionaryCount = count
                        if (isFirstMove && cells.none { it.tile != null }) {
                            refereeResult = RefereeResult(
                                false,
                                0,
                                emptyList(),
                                "Ready (${java.text.NumberFormat.getIntegerInstance().format(count)} words loaded). Place tiles covering center star (★)."
                            )
                        }
                    }
                }
            } catch (e: Exception) {
                // Fall back cleanly
            }
        }
    }

    // Synchronize physical tiles reported by ESP32 over BLE
    LaunchedEffect(physicalTiles) {
        var changed = false
        val updated = cells.map { cell ->
            val ch = cell.row * 4 + cell.col
            if (physicalTiles.containsKey(ch)) {
                val letter = physicalTiles[ch]!!
                if (cell.tile?.letter != letter || !cell.isPhysical) {
                    changed = true
                    cell.copy(
                        tile = Tile(letter, getScrabbleLetterPoints(letter)),
                        isPhysical = true,
                        isCommitted = false
                    )
                } else cell
            } else if (cell.isPhysical && !cell.isCommitted) {
                // Tile lifted from physical board
                changed = true
                cell.copy(tile = null, isPhysical = false)
            } else {
                cell
            }
        }
        if (changed) {
            cells = updated
            updateRefereeEvaluation()
        }
    }

    Column(
        modifier = modifier
            .fillMaxSize()
            .background(Color(0xFFF9F6F0))
            .padding(14.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        // --- 1. Board Connection & Scan Telemetry Bar ---
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(
                containerColor = when (bleConnectionState) {
                    is BleConnectionState.Connected -> Color(0xFFE8F5E9)
                    is BleConnectionState.Scanning, is BleConnectionState.Connecting -> Color(0xFFFFF8E1)
                    is BleConnectionState.Error -> Color(0xFFFFEBEE)
                    else -> Color(0xFFECEFF1)
                }
            ),
            shape = RoundedCornerShape(10.dp),
            elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 12.dp, vertical = 8.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.weight(1f)) {
                    Text(
                        text = when (bleConnectionState) {
                            is BleConnectionState.Connected -> "🟢"
                            is BleConnectionState.Scanning -> "🟡"
                            is BleConnectionState.Connecting -> "⏳"
                            is BleConnectionState.Error -> "⚠️"
                            else -> "⚪"
                        },
                        fontSize = 15.sp,
                        modifier = Modifier.padding(end = 8.dp)
                    )
                    Column {
                        Text(
                            text = when (bleConnectionState) {
                                is BleConnectionState.Connected -> "Physical Board Linked"
                                is BleConnectionState.Scanning -> "Searching for Board..."
                                is BleConnectionState.Connecting -> "Connecting to Board..."
                                is BleConnectionState.Error -> "Connection Error"
                                else -> "Physical Board Disconnected"
                            },
                            fontWeight = FontWeight.Bold,
                            fontSize = 12.sp,
                            color = Color(0xFF263238)
                        )
                        Text(
                            text = when (bleConnectionState) {
                                is BleConnectionState.Connected -> {
                                    if (scanTelemetry.activeChannel != null) {
                                        val ch = scanTelemetry.activeChannel!!
                                        "⚡ Energizing Coil $ch (Row ${ch / 4}, Col ${ch % 4})"
                                    } else {
                                        "Live BLE Sync Active (SmartCrossword_4x4)"
                                    }
                                }
                                is BleConnectionState.Error -> (bleConnectionState as BleConnectionState.Error).message
                                is BleConnectionState.Scanning -> "Scanning BLE nearby..."
                                is BleConnectionState.Connecting -> "Handshaking GATT..."
                                else -> "Tap to connect physical wooden board"
                            },
                            fontSize = 11.sp,
                            color = Color(0xFF546E7A)
                        )
                    }
                }

                Row(verticalAlignment = Alignment.CenterVertically) {
                    when (bleConnectionState) {
                        is BleConnectionState.Connected -> {
                            Button(
                                onClick = { bleManager.triggerSweep() },
                                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF00897B)),
                                contentPadding = PaddingValues(horizontal = 10.dp, vertical = 4.dp),
                                shape = RoundedCornerShape(6.dp),
                                modifier = Modifier.height(30.dp)
                            ) {
                                Text("⚡ Sweep", fontSize = 11.sp, fontWeight = FontWeight.Bold)
                            }
                            Spacer(modifier = Modifier.width(6.dp))
                            IconButton(
                                onClick = { bleManager.disconnect() },
                                modifier = Modifier.size(26.dp)
                            ) {
                                Text("✕", fontSize = 13.sp, color = Color.Gray)
                            }
                        }
                        is BleConnectionState.Scanning, is BleConnectionState.Connecting -> {
                            CircularProgressIndicator(
                                modifier = Modifier.size(18.dp),
                                strokeWidth = 2.dp,
                                color = Color(0xFFF57C00)
                            )
                        }
                        else -> {
                            Button(
                                onClick = { requestBlePermissionsAndScan() },
                                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF455A64)),
                                contentPadding = PaddingValues(horizontal = 10.dp, vertical = 4.dp),
                                shape = RoundedCornerShape(6.dp),
                                modifier = Modifier.height(30.dp)
                            ) {
                                Text("Connect", fontSize = 11.sp, fontWeight = FontWeight.Bold)
                            }
                        }
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(10.dp))

        // --- 2. Scoreboard Card ---
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = Color(0xFF3E2723)),
            shape = RoundedCornerShape(12.dp),
            elevation = CardDefaults.cardElevation(defaultElevation = 3.dp)
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 10.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text(
                        text = playerName,
                        color = Color(0xFFFFCC80),
                        fontWeight = FontWeight.Bold,
                        fontSize = 15.sp
                    )
                    Text(
                        text = "$playerScore pts",
                        color = Color.White,
                        fontWeight = FontWeight.Black,
                        fontSize = 20.sp
                    )
                }
                Text(
                    text = "VS",
                    color = Color(0xFFBCAAA4),
                    fontWeight = FontWeight.Bold,
                    fontSize = 13.sp
                )
                Column(horizontalAlignment = Alignment.End) {
                    Text(
                        text = opponentName,
                        color = Color(0xFFD7CCC8),
                        fontWeight = FontWeight.Medium,
                        fontSize = 13.sp
                    )
                    Text(
                        text = "$opponentScore pts",
                        color = Color.White,
                        fontWeight = FontWeight.Black,
                        fontSize = 20.sp
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(8.dp))

        // --- 3. Referee Announcement Banner ---
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(
                containerColor = when {
                    refereeResult?.isValid == true -> Color(0xFFE8F5E9)
                    else -> Color(0xFFFFF3E0)
                }
            ),
            shape = RoundedCornerShape(8.dp)
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(8.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = when {
                        refereeResult?.isValid == true -> "✅"
                        else -> "ℹ️"
                    },
                    fontSize = 16.sp,
                    modifier = Modifier.padding(end = 6.dp)
                )
                Text(
                    text = refereeResult?.message ?: "Place tiles on the board.",
                    color = when {
                        refereeResult?.isValid == true -> Color(0xFF2E7D32)
                        else -> Color(0xFFE65100)
                    },
                    fontWeight = FontWeight.SemiBold,
                    fontSize = 12.sp
                )
            }
        }

        Spacer(modifier = Modifier.height(12.dp))

        // --- 4. 4x4 Grid Board with Live Radar Scanning Effect ---
        Box(
            modifier = Modifier
                .size(310.dp)
                .shadow(6.dp, RoundedCornerShape(12.dp))
                .clip(RoundedCornerShape(12.dp))
                .background(Color(0xFF5D4037))
                .padding(6.dp)
        ) {
            Column(
                modifier = Modifier.fillMaxSize(),
                verticalArrangement = Arrangement.spacedBy(4.dp)
            ) {
                for (r in 0 until Board4x4.SIZE) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .weight(1f),
                        horizontalArrangement = Arrangement.spacedBy(4.dp)
                    ) {
                        for (c in 0 until Board4x4.SIZE) {
                            val ch = r * 4 + c
                            val cell = cells.find { it.row == r && it.col == c }!!
                            val isEnergized = scanTelemetry.activeChannel == ch && scanTelemetry.status == BleProtocol.STATUS_ENERGIZED
                            val isTagHit = scanTelemetry.activeChannel == ch && scanTelemetry.status == BleProtocol.STATUS_TAG_DETECTED

                            Box(
                                modifier = Modifier
                                    .weight(1f)
                                    .fillMaxHeight()
                                    .clip(RoundedCornerShape(6.dp))
                                    .background(
                                        when {
                                            isTagHit -> Color(0xFFC8E6C9)
                                            isEnergized -> Color(0xFFB2EBF2).copy(alpha = pulseAlpha)
                                            else -> Color(cell.squareType.badgeColor)
                                        }
                                    )
                                    .border(
                                        width = when {
                                            isEnergized -> 3.dp
                                            isTagHit -> 3.dp
                                            cell.tile != null && !cell.isCommitted -> 2.dp
                                            else -> 1.dp
                                        },
                                        color = when {
                                            isTagHit -> Color(0xFF00E676)
                                            isEnergized -> Color(0xFF00E5FF).copy(alpha = pulseAlpha)
                                            cell.tile != null && cell.isPhysical -> Color(0xFF2E7D32)
                                            cell.tile != null && !cell.isCommitted -> Color(0xFF4CAF50)
                                            else -> Color(0x33000000)
                                        },
                                        shape = RoundedCornerShape(6.dp)
                                    )
                                    .clickable {
                                        if (cell.tile != null && !cell.isCommitted && !cell.isPhysical) {
                                            // Recall uncommitted touch tile back to rack
                                            rackTiles = rackTiles + cell.tile
                                            cells = cells.map {
                                                if (it.row == r && it.col == c) it.copy(tile = null) else it
                                            }
                                            updateRefereeEvaluation()
                                        } else if (cell.tile == null && selectedTileIndex != null) {
                                            // Place selected touch tile
                                            val tileToPlace = rackTiles[selectedTileIndex!!]
                                            rackTiles = rackTiles.toMutableList().also { it.removeAt(selectedTileIndex!!) }
                                            selectedTileIndex = null
                                            cells = cells.map {
                                                if (it.row == r && it.col == c) it.copy(tile = tileToPlace, isCommitted = false, isPhysical = false) else it
                                            }
                                            updateRefereeEvaluation()
                                        }
                                    },
                                contentAlignment = Alignment.Center
                            ) {
                                if (cell.tile != null) {
                                    // Wooden Tile
                                    Box(
                                        modifier = Modifier
                                            .fillMaxSize()
                                            .padding(2.dp)
                                            .shadow(2.dp, RoundedCornerShape(4.dp))
                                            .clip(RoundedCornerShape(4.dp))
                                            .background(
                                                when {
                                                    cell.isCommitted -> Color(0xFFD7CCC8)
                                                    cell.isPhysical -> Color(0xFFFFD54F)
                                                    else -> Color(0xFFFFE0B2)
                                                }
                                            ),
                                        contentAlignment = Alignment.Center
                                    ) {
                                        // Physical tile badge indicator
                                        if (cell.isPhysical) {
                                            Text(
                                                text = "⊚",
                                                fontSize = 11.sp,
                                                fontWeight = FontWeight.Black,
                                                color = Color(0xFF1B5E20),
                                                modifier = Modifier
                                                    .align(Alignment.TopStart)
                                                    .padding(start = 3.dp, top = 1.dp)
                                            )
                                        }

                                        Text(
                                            text = cell.tile.letter.toString(),
                                            fontWeight = FontWeight.Bold,
                                            fontSize = 22.sp,
                                            color = Color(0xFF2C1810)
                                        )
                                        Text(
                                            text = cell.tile.points.toString(),
                                            fontWeight = FontWeight.Bold,
                                            fontSize = 9.sp,
                                            color = Color(0xFF5D4037),
                                            modifier = Modifier
                                                .align(Alignment.BottomEnd)
                                                .padding(end = 3.dp, bottom = 2.dp)
                                        )
                                    }
                                } else {
                                    // Bonus badge label or scanning indicator
                                    if (isEnergized) {
                                        Text(
                                            text = "⚡",
                                            fontSize = 16.sp
                                        )
                                    } else if (cell.squareType.label.isNotEmpty()) {
                                        Text(
                                            text = cell.squareType.label,
                                            fontWeight = FontWeight.ExtraBold,
                                            fontSize = if (cell.squareType == SquareType.CENTER) 18.sp else 12.sp,
                                            color = if (cell.squareType == SquareType.TRIPLE_WORD || cell.squareType == SquareType.TRIPLE_LETTER) Color.White else Color(0xFF3E2723)
                                        )
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(12.dp))

        // --- 5. Tile Rack ---
        Text(
            text = "Your Rack (Tap to Select):",
            fontWeight = FontWeight.Bold,
            fontSize = 12.sp,
            color = Color(0xFF5D4037),
            modifier = Modifier.align(Alignment.Start)
        )

        Spacer(modifier = Modifier.height(4.dp))

        Row(
            modifier = Modifier
                .fillMaxWidth()
                .shadow(2.dp, RoundedCornerShape(8.dp))
                .clip(RoundedCornerShape(8.dp))
                .background(Color(0xFF8D6E63))
                .padding(horizontal = 6.dp, vertical = 6.dp),
            horizontalArrangement = Arrangement.SpaceEvenly
        ) {
            rackTiles.forEachIndexed { index, tile ->
                val isSelected = selectedTileIndex == index
                Box(
                    modifier = Modifier
                        .size(38.dp)
                        .shadow(if (isSelected) 4.dp else 1.dp, RoundedCornerShape(4.dp))
                        .clip(RoundedCornerShape(4.dp))
                        .background(if (isSelected) Color(0xFFFFD54F) else Color(0xFFFFE0B2))
                        .border(
                            width = if (isSelected) 2.dp else 1.dp,
                            color = if (isSelected) Color(0xFFE65100) else Color(0xFF8D6E63),
                            shape = RoundedCornerShape(4.dp)
                        )
                        .clickable {
                            selectedTileIndex = if (isSelected) null else index
                        },
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = tile.letter.toString(),
                        fontWeight = FontWeight.Bold,
                        fontSize = 18.sp,
                        color = Color(0xFF2C1810)
                    )
                    Text(
                        text = tile.points.toString(),
                        fontWeight = FontWeight.Bold,
                        fontSize = 8.sp,
                        color = Color(0xFF5D4037),
                        modifier = Modifier
                            .align(Alignment.BottomEnd)
                            .padding(end = 2.dp, bottom = 1.dp)
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(12.dp))

        // --- 6. Action Buttons ---
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            OutlinedButton(
                onClick = {
                    // Recall all uncommitted touch tiles
                    val uncommittedTouch = cells.filter { it.tile != null && !it.isCommitted && !it.isPhysical }
                    rackTiles = rackTiles + uncommittedTouch.map { it.tile!! }
                    cells = cells.map {
                        if (!it.isCommitted && !it.isPhysical) it.copy(tile = null) else it
                    }
                    selectedTileIndex = null
                    updateRefereeEvaluation()
                },
                modifier = Modifier.weight(1f),
                shape = RoundedCornerShape(8.dp)
            ) {
                Text("Recall", fontSize = 12.sp)
            }

            OutlinedButton(
                onClick = {
                    rackTiles = rackTiles.shuffled()
                },
                modifier = Modifier.weight(1f),
                shape = RoundedCornerShape(8.dp)
            ) {
                Text("Shuffle", fontSize = 12.sp)
            }

            Button(
                onClick = {
                    if (refereeResult?.isValid == true) {
                        playerScore += refereeResult!!.score
                        cells = cells.map {
                            if (it.tile != null) it.copy(isCommitted = true) else it
                        }
                        isFirstMove = false
                        selectedTileIndex = null
                        bleManager.sendCommand(BleProtocol.CMD_COMMIT_TURN)
                        refereeResult = RefereeResult(
                            false,
                            0,
                            emptyList(),
                            "Turn submitted! Scored ${refereeResult!!.score} pts. Waiting for opponent."
                        )
                    }
                },
                enabled = refereeResult?.isValid == true,
                modifier = Modifier.weight(1.3f),
                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF2E7D32)),
                shape = RoundedCornerShape(8.dp)
            ) {
                Text("Submit Move", fontWeight = FontWeight.Bold, fontSize = 12.sp)
            }
        }
    }
}

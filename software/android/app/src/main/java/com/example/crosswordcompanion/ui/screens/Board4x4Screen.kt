package com.example.crosswordcompanion.ui.screens

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
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.crosswordcompanion.game.EnglishReferee
import com.example.crosswordcompanion.game.RefereeResult
import com.example.crosswordcompanion.model.Board4x4
import com.example.crosswordcompanion.model.BoardCell
import com.example.crosswordcompanion.model.SquareType
import com.example.crosswordcompanion.model.Tile

@Composable
fun Board4x4Screen(
    playerName: String = "Sarah",
    opponentName: String = "Grandma Betty (Board)",
    modifier: Modifier = Modifier
) {
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

    // Helper to evaluate uncommitted tiles
    fun updateRefereeEvaluation() {
        val uncommitted = cells.filter { it.tile != null && !it.isCommitted }
        refereeResult = referee.evaluateMove(cells, uncommitted, isFirstMove)
    }

    Column(
        modifier = modifier
            .fillMaxSize()
            .background(Color(0xFFF9F6F0))
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        // Scoreboard Card
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = Color(0xFF3E2723)),
            shape = RoundedCornerShape(12.dp),
            elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 12.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text(
                        text = playerName,
                        color = Color(0xFFFFCC80),
                        fontWeight = FontWeight.Bold,
                        fontSize = 16.sp
                    )
                    Text(
                        text = "$playerScore pts",
                        color = Color.White,
                        fontWeight = FontWeight.Black,
                        fontSize = 22.sp
                    )
                }
                Text(
                    text = "VS",
                    color = Color(0xFFBCAAA4),
                    fontWeight = FontWeight.Bold,
                    fontSize = 14.sp
                )
                Column(horizontalAlignment = Alignment.End) {
                    Text(
                        text = opponentName,
                        color = Color(0xFFD7CCC8),
                        fontWeight = FontWeight.Medium,
                        fontSize = 14.sp
                    )
                    Text(
                        text = "$opponentScore pts",
                        color = Color.White,
                        fontWeight = FontWeight.Black,
                        fontSize = 22.sp
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(12.dp))

        // Referee Announcement Banner
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
                    .padding(10.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = when {
                        refereeResult?.isValid == true -> "✅"
                        else -> "ℹ️"
                    },
                    fontSize = 18.sp,
                    modifier = Modifier.padding(end = 8.dp)
                )
                Text(
                    text = refereeResult?.message ?: "Place tiles on the board.",
                    color = when {
                        refereeResult?.isValid == true -> Color(0xFF2E7D32)
                        else -> Color(0xFFE65100)
                    },
                    fontWeight = FontWeight.SemiBold,
                    fontSize = 13.sp
                )
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // 4x4 Grid Board
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
                            val cell = cells.find { it.row == r && it.col == c }!!
                            Box(
                                modifier = Modifier
                                    .weight(1f)
                                    .fillMaxHeight()
                                    .clip(RoundedCornerShape(6.dp))
                                    .background(Color(cell.squareType.badgeColor))
                                    .border(
                                        width = if (cell.tile != null && !cell.isCommitted) 2.dp else 1.dp,
                                        color = if (cell.tile != null && !cell.isCommitted) Color(0xFF4CAF50) else Color(0x33000000),
                                        shape = RoundedCornerShape(6.dp)
                                    )
                                    .clickable {
                                        if (cell.tile != null && !cell.isCommitted) {
                                            // Recall uncommitted tile back to rack
                                            rackTiles = rackTiles + cell.tile
                                            cells = cells.map {
                                                if (it.row == r && it.col == c) it.copy(tile = null) else it
                                            }
                                            updateRefereeEvaluation()
                                        } else if (cell.tile == null && selectedTileIndex != null) {
                                            // Place selected tile
                                            val tileToPlace = rackTiles[selectedTileIndex!!]
                                            rackTiles = rackTiles.toMutableList().also { it.removeAt(selectedTileIndex!!) }
                                            selectedTileIndex = null
                                            cells = cells.map {
                                                if (it.row == r && it.col == c) it.copy(tile = tileToPlace, isCommitted = false) else it
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
                                                if (cell.isCommitted) Color(0xFFD7CCC8) else Color(0xFFFFE0B2)
                                            ),
                                        contentAlignment = Alignment.Center
                                    ) {
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
                                    // Bonus badge label
                                    if (cell.squareType.label.isNotEmpty()) {
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

        Spacer(modifier = Modifier.height(16.dp))

        // Tile Rack
        Text(
            text = "Your Rack (Tap to Select):",
            fontWeight = FontWeight.Bold,
            fontSize = 13.sp,
            color = Color(0xFF5D4037),
            modifier = Modifier.align(Alignment.Start)
        )

        Spacer(modifier = Modifier.height(6.dp))

        Row(
            modifier = Modifier
                .fillMaxWidth()
                .shadow(3.dp, RoundedCornerShape(8.dp))
                .clip(RoundedCornerShape(8.dp))
                .background(Color(0xFF8D6E63))
                .padding(horizontal = 6.dp, vertical = 8.dp),
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

        Spacer(modifier = Modifier.height(14.dp))

        // Action Buttons
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            OutlinedButton(
                onClick = {
                    // Recall all uncommitted tiles
                    val uncommitted = cells.filter { it.tile != null && !it.isCommitted }
                    rackTiles = rackTiles + uncommitted.map { it.tile!! }
                    cells = cells.map {
                        if (!it.isCommitted) it.copy(tile = null) else it
                    }
                    selectedTileIndex = null
                    updateRefereeEvaluation()
                },
                modifier = Modifier.weight(1f),
                shape = RoundedCornerShape(8.dp)
            ) {
                Text("Recall", fontSize = 13.sp)
            }

            OutlinedButton(
                onClick = {
                    rackTiles = rackTiles.shuffled()
                },
                modifier = Modifier.weight(1f),
                shape = RoundedCornerShape(8.dp)
            ) {
                Text("Shuffle", fontSize = 13.sp)
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
                Text("Submit Move", fontWeight = FontWeight.Bold, fontSize = 13.sp)
            }
        }
    }
}

package com.example.crosswordcompanion.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.crosswordcompanion.data.AppDatabaseHelper
import com.example.crosswordcompanion.data.FriendRecord
import com.example.crosswordcompanion.model.UniqueUsernameGenerator

@Composable
fun FriendsScreen(
    userHandle: String = "sarah#4821",
    displayName: String = "Sarah",
    onPlayAgainst: (String) -> Unit = {},
    modifier: Modifier = Modifier
) {
    val context = LocalContext.current
    val dbHelper = remember { AppDatabaseHelper(context) }

    var friendsList by remember { mutableStateOf(dbHelper.getAllFriends()) }
    var inputName by remember { mutableStateOf("") }
    var inputHandle by remember { mutableStateOf("") }
    var isBoardCheckbox by remember { mutableStateOf(false) }
    var errorMessage by remember { mutableStateOf<String?>(null) }
    var successMessage by remember { mutableStateOf<String?>(null) }

    Column(
        modifier = modifier
            .fillMaxSize()
            .background(Color(0xFFF9F6F0))
            .padding(16.dp)
    ) {
        // Your Unique Username Card
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = Color(0xFF4E342E)),
            shape = RoundedCornerShape(12.dp)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = "YOUR UNIQUE PLAYER IDENTITY",
                    fontSize = 11.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color(0xFFFFCC80)
                )
                Spacer(modifier = Modifier.height(4.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text(
                            text = displayName,
                            fontSize = 20.sp,
                            fontWeight = FontWeight.Bold,
                            color = Color.White
                        )
                        Text(
                            text = userHandle,
                            fontSize = 14.sp,
                            fontWeight = FontWeight.Medium,
                            color = Color(0xFFD7CCC8)
                        )
                    }
                    Surface(
                        color = Color(0xFF6D4C41),
                        shape = RoundedCornerShape(6.dp)
                    ) {
                        Text(
                            text = "Share Handle",
                            color = Color.White,
                            fontSize = 12.sp,
                            fontWeight = FontWeight.SemiBold,
                            modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp)
                        )
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Add Friend or Board Card
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = Color.White),
            shape = RoundedCornerShape(12.dp),
            elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
        ) {
            Column(modifier = Modifier.padding(14.dp)) {
                Text(
                    text = "Add Friend or Smart Board",
                    fontWeight = FontWeight.Bold,
                    fontSize = 15.sp,
                    color = Color(0xFF3E2723)
                )
                Spacer(modifier = Modifier.height(8.dp))

                OutlinedTextField(
                    value = inputName,
                    onValueChange = { inputName = it; errorMessage = null },
                    label = { Text("Display Name (e.g. Grandma Betty)") },
                    singleLine = true,
                    modifier = Modifier.fillMaxWidth()
                )

                Spacer(modifier = Modifier.height(8.dp))

                OutlinedTextField(
                    value = inputHandle,
                    onValueChange = { inputHandle = it; errorMessage = null },
                    label = { Text("Unique Handle (e.g. sarah#4821 or SCB-8492)") },
                    singleLine = true,
                    modifier = Modifier.fillMaxWidth()
                )

                Spacer(modifier = Modifier.height(6.dp))

                Row(verticalAlignment = Alignment.CenterVertically) {
                    Checkbox(
                        checked = isBoardCheckbox,
                        onCheckedChange = { isBoardCheckbox = it }
                    )
                    Text(
                        text = "This is a physical Smart Crossword Board",
                        fontSize = 13.sp,
                        color = Color(0xFF5D4037)
                    )
                }

                if (errorMessage != null) {
                    Text(
                        text = errorMessage!!,
                        color = Color.Red,
                        fontSize = 12.sp,
                        modifier = Modifier.padding(top = 4.dp)
                    )
                }

                if (successMessage != null) {
                    Text(
                        text = successMessage!!,
                        color = Color(0xFF2E7D32),
                        fontSize = 12.sp,
                        modifier = Modifier.padding(top = 4.dp)
                    )
                }

                Spacer(modifier = Modifier.height(8.dp))

                Button(
                    onClick = {
                        val name = inputName.trim()
                        val handle = inputHandle.trim().lowercase()

                        if (name.isEmpty()) {
                            errorMessage = "Please enter a display name."
                            return@Button
                        }
                        if (!UniqueUsernameGenerator.isValidHandle(handle)) {
                            errorMessage = "Invalid handle format. Use name#1234 or SCB-1234."
                            return@Button
                        }

                        val added = dbHelper.addFriend(name, handle, isBoardCheckbox)
                        if (added) {
                            friendsList = dbHelper.getAllFriends()
                            inputName = ""
                            inputHandle = ""
                            successMessage = "Added '$name' to your friends!"
                            errorMessage = null
                        } else {
                            errorMessage = "A friend or board with this handle already exists."
                        }
                    },
                    modifier = Modifier.align(Alignment.End),
                    colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF6D4C41)),
                    shape = RoundedCornerShape(8.dp)
                ) {
                    Text("Add Contact")
                }
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Paired Contacts List
        Text(
            text = "Paired Friends & Physical Boards (${friendsList.size})",
            fontWeight = FontWeight.Bold,
            fontSize = 14.sp,
            color = Color(0xFF4E342E)
        )

        Spacer(modifier = Modifier.height(8.dp))

        LazyColumn(
            modifier = Modifier.fillMaxWidth(),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            items(friendsList) { friend ->
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(containerColor = Color.White),
                    shape = RoundedCornerShape(10.dp),
                    elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(12.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Box(
                                modifier = Modifier
                                    .size(36.dp)
                                    .clip(RoundedCornerShape(8.dp))
                                    .background(if (friend.isBoard) Color(0xFFFFE0B2) else Color(0xFFE1BEE7)),
                                contentAlignment = Alignment.Center
                            ) {
                                Text(
                                    text = if (friend.isBoard) "🪵" else "📱",
                                    fontSize = 18.sp
                                )
                            }
                            Spacer(modifier = Modifier.width(12.dp))
                            Column {
                                Text(
                                    text = friend.displayName,
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 15.sp,
                                    color = Color(0xFF2C1810)
                                )
                                Text(
                                    text = friend.uniqueUsername,
                                    fontSize = 12.sp,
                                    color = Color(0xFF757575)
                                )
                            }
                        }

                        Button(
                            onClick = { onPlayAgainst(friend.displayName) },
                            colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF2E7D32)),
                            shape = RoundedCornerShape(6.dp),
                            contentPadding = PaddingValues(horizontal = 12.dp, vertical = 6.dp)
                        ) {
                            Text("Play", fontSize = 12.sp, fontWeight = FontWeight.Bold)
                        }
                    }
                }
            }
        }
    }
}

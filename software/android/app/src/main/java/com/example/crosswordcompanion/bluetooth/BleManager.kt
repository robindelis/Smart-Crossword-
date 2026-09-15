package com.example.crosswordcompanion.bluetooth

import android.annotation.SuppressLint
import android.bluetooth.*
import android.bluetooth.le.ScanCallback
import android.bluetooth.le.ScanFilter
import android.bluetooth.le.ScanResult
import android.bluetooth.le.ScanSettings
import android.content.Context
import android.os.Build
import android.os.ParcelUuid
import android.util.Log
import com.example.crosswordcompanion.data.AppDatabaseHelper
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import java.util.UUID

sealed interface BleConnectionState {
    object Disconnected : BleConnectionState
    object Scanning : BleConnectionState
    data class Connecting(val deviceName: String) : BleConnectionState
    data class Connected(val deviceName: String, val rssi: Int = 0) : BleConnectionState
    data class Error(val message: String) : BleConnectionState
}

data class ScanTelemetry(
    val activeChannel: Int? = null, // 0..15, or null when idle
    val status: Int = 0,            // 1 = scanning/energized, 2 = tag hit, 0 = idle
    val tagUid: String? = null      // e.g. "04:A1:B2:C3:D4:E5:10"
)

object BleProtocol {
    val SERVICE_UUID: UUID = UUID.fromString("19B10000-E8F2-537E-4F6C-D104768A1214")
    val CHAR_BOARD_STATE_UUID: UUID = UUID.fromString("19B10001-E8F2-537E-4F6C-D104768A1214")
    val CHAR_SCAN_TELEMETRY_UUID: UUID = UUID.fromString("19B10002-E8F2-537E-4F6C-D104768A1214")
    val CHAR_BOARD_COMMAND_UUID: UUID = UUID.fromString("19B10003-E8F2-537E-4F6C-D104768A1214")
    val CLIENT_CONFIG_DESCRIPTOR: UUID = UUID.fromString("00002902-0000-1000-8000-00805f9b34fb")

    const val DEVICE_NAME = "SmartCrossword_4x4"

    // Command Codes sent from Phone to Board
    const val CMD_TRIGGER_SWEEP: Byte = 0x01
    const val CMD_TOGGLE_CONTINUOUS: Byte = 0x02
    const val CMD_SELECT_CHANNEL: Byte = 0x03
    const val CMD_TOGGLE_MUX: Byte = 0x04
    const val CMD_ENROLL_TAG: Byte = 0x05
    const val CMD_SYNC_TILE: Byte = 0x06
    const val CMD_COMMIT_TURN: Byte = 0x10

    // Telemetry Status Codes
    const val STATUS_IDLE = 0
    const val STATUS_ENERGIZED = 1
    const val STATUS_TAG_DETECTED = 2

    /**
     * Unpacks 16-byte payload representing squares 0..15.
     * Returns a map from square index (0..15) to uppercase letter Char.
     */
    fun parseBoardState(bytes: ByteArray): Map<Int, Char> {
        val result = mutableMapOf<Int, Char>()
        val count = minOf(bytes.size, 16)
        for (i in 0 until count) {
            val byteVal = bytes[i]
            val charVal = byteVal.toInt().toChar()
            if (charVal in 'A'..'Z') {
                result[i] = charVal
            } else if (charVal in 'a'..'z') {
                result[i] = charVal.uppercaseChar()
            } else if (charVal == '?') {
                result[i] = '?'
            }
        }
        return result
    }

    /**
     * Parses telemetry packet: [channel, status, (optional) uidLen, (optional) uid bytes...].
     * Byte 0: 0..15 (channel), or 0xFF (idle/sweep complete).
     * Byte 1: status (1 = scanning/probing, 2 = hit, 0 = idle).
     * Byte 2: uidLen (e.g. 7 or 4)
     * Bytes 3..3+uidLen: Raw UID bytes
     */
    fun parseScanTelemetry(bytes: ByteArray): ScanTelemetry {
        if (bytes.size < 2) return ScanTelemetry()
        val rawCh = bytes[0].toInt() and 0xFF
        val status = bytes[1].toInt() and 0xFF
        val channel = if (rawCh in 0..15) rawCh else null

        var uidString: String? = null
        if (bytes.size >= 3) {
            val uidLen = bytes[2].toInt() and 0xFF
            if (uidLen in 1..7 && bytes.size >= 3 + uidLen) {
                val hexList = mutableListOf<String>()
                for (i in 0 until uidLen) {
                    hexList.add(String.format("%02X", bytes[3 + i]))
                }
                uidString = hexList.joinToString(":")
            }
        }
        return ScanTelemetry(activeChannel = channel, status = status, tagUid = uidString)
    }

    /**
     * Parses a hex UID string like "04:A1:B2:C3:D4:E5:10" or "04A1B2C3D4E510" into a ByteArray.
     */
    fun parseHexUid(uidHex: String): ByteArray {
        val clean = uidHex.replace(":", "").replace(" ", "").trim()
        if (clean.isEmpty() || clean.length % 2 != 0) return ByteArray(0)
        val bytes = ByteArray(clean.length / 2)
        for (i in bytes.indices) {
            val byteStr = clean.substring(i * 2, i * 2 + 2)
            val intVal = byteStr.toIntOrNull(16) ?: return ByteArray(0)
            bytes[i] = intVal.toByte()
        }
        return bytes
    }

    /**
     * Formats raw UID bytes to colon-delimited hex string e.g. "04:A1:B2:C3:D4:E5:10".
     */
    fun formatHexUid(bytes: ByteArray): String {
        val hexList = mutableListOf<String>()
        for (b in bytes) {
            hexList.add(String.format("%02X", b))
        }
        return hexList.joinToString(":")
    }

    /**
     * Standard Scrabble letter point values.
     */
    fun getLetterPoints(c: Char): Int {
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

    /**
     * Builds packet for CMD_SYNC_TILE: [CMD_SYNC_TILE, uidLen, uidBytes..., letter, points].
     */
    fun buildSyncTilePayload(uidHex: String, letter: Char, points: Int): ByteArray? {
        val uidBytes = parseHexUid(uidHex)
        if (uidBytes.isEmpty() || uidBytes.size > 10) return null
        val payload = ByteArray(2 + uidBytes.size + 2)
        payload[0] = CMD_SYNC_TILE
        payload[1] = uidBytes.size.toByte()
        System.arraycopy(uidBytes, 0, payload, 2, uidBytes.size)
        payload[2 + uidBytes.size] = letter.uppercaseChar().code.toByte()
        payload[3 + uidBytes.size] = points.toByte()
        return payload
    }
}

class BleManager private constructor(private val context: Context) {
    companion object {
        private const val TAG = "SmartCrossword_BLE"

        @Volatile
        private var instance: BleManager? = null

        fun getInstance(context: Context): BleManager {
            return instance ?: synchronized(this) {
                instance ?: BleManager(context.applicationContext).also { instance = it }
            }
        }
    }

    val dbHelper = AppDatabaseHelper(context)

    private val bluetoothManager = context.getSystemService(Context.BLUETOOTH_SERVICE) as? BluetoothManager
    private val bluetoothAdapter = bluetoothManager?.adapter

    private val _connectionState = MutableStateFlow<BleConnectionState>(BleConnectionState.Disconnected)
    val connectionState: StateFlow<BleConnectionState> = _connectionState.asStateFlow()

    private val _scanTelemetry = MutableStateFlow(ScanTelemetry())
    val scanTelemetry: StateFlow<ScanTelemetry> = _scanTelemetry.asStateFlow()

    private val _boardState = MutableStateFlow<Map<Int, Char>>(emptyMap())
    val boardState: StateFlow<Map<Int, Char>> = _boardState.asStateFlow()

    var autoReconnectEnabled = true

    private var activeGatt: BluetoothGatt? = null
    private var isScanning = false
    private val scope = CoroutineScope(Dispatchers.Main + SupervisorJob())
    private var scanTimeoutJob: Job? = null
    private var reconnectJob: Job? = null
    private var lastAutoHealedUid: String? = null
    private var lastAutoHealedTime: Long = 0L

    private val descriptorQueue = mutableListOf<BluetoothGattDescriptor>()
    private var isWritingDescriptor = false

    private val scanCallback = object : ScanCallback() {
        @SuppressLint("MissingPermission")
        override fun onScanResult(callbackType: Int, result: ScanResult) {
            val device = result.device
            val name = device.name ?: result.scanRecord?.deviceName

            if (name == BleProtocol.DEVICE_NAME ||
                result.scanRecord?.serviceUuids?.any { it.uuid == BleProtocol.SERVICE_UUID } == true
            ) {
                Log.i(TAG, "🎯 Smart Crossword Board found! Connecting to ${device.address}...")
                stopScan()
                connect(device)
            }
        }

        override fun onScanFailed(errorCode: Int) {
            Log.e(TAG, "BLE Scan failed with error code: $errorCode")
            _connectionState.value = BleConnectionState.Error("Scan failed: code $errorCode")
            isScanning = false
            scheduleAutoReconnect()
        }
    }

    private val gattCallback = object : BluetoothGattCallback() {
        @SuppressLint("MissingPermission")
        override fun onConnectionStateChange(gatt: BluetoothGatt, status: Int, newState: Int) {
            val devName = gatt.device.name ?: BleProtocol.DEVICE_NAME
            when (newState) {
                BluetoothProfile.STATE_CONNECTED -> {
                    Log.i(TAG, "Connected to GATT server on $devName. Requesting MTU 64...")
                    _connectionState.value = BleConnectionState.Connecting(devName)
                    activeGatt = gatt
                    gatt.requestMtu(64)
                }
                BluetoothProfile.STATE_DISCONNECTED -> {
                    Log.w(TAG, "Disconnected from GATT server on $devName.")
                    _connectionState.value = BleConnectionState.Disconnected
                    _scanTelemetry.value = ScanTelemetry()
                    cleanupGatt()
                    scheduleAutoReconnect()
                }
            }
        }

        @SuppressLint("MissingPermission")
        override fun onMtuChanged(gatt: BluetoothGatt, mtu: Int, status: Int) {
            Log.d(TAG, "MTU changed to $mtu, discovering services...")
            gatt.discoverServices()
        }

        @SuppressLint("MissingPermission")
        override fun onServicesDiscovered(gatt: BluetoothGatt, status: Int) {
            if (status != BluetoothGatt.GATT_SUCCESS) {
                Log.e(TAG, "Service discovery failed with status $status")
                _connectionState.value = BleConnectionState.Error("Service discovery failed ($status)")
                scheduleAutoReconnect()
                return
            }

            val service = gatt.getService(BleProtocol.SERVICE_UUID)
            if (service == null) {
                Log.e(TAG, "Board Service UUID not found on device!")
                _connectionState.value = BleConnectionState.Error("Smart Crossword Service not found")
                scheduleAutoReconnect()
                return
            }

            Log.i(TAG, "Board Service located. Enabling characteristic notifications...")
            val devName = gatt.device.name ?: BleProtocol.DEVICE_NAME
            _connectionState.value = BleConnectionState.Connected(devName)

            // Queue notifications for BOARD_STATE and SCAN_TELEMETRY
            descriptorQueue.clear()
            isWritingDescriptor = false

            enableNotification(gatt, service, BleProtocol.CHAR_BOARD_STATE_UUID)
            enableNotification(gatt, service, BleProtocol.CHAR_SCAN_TELEMETRY_UUID)

            writeNextDescriptor(gatt)

            // Auto-sync all local tiles to board after connection and notifications initialized
            scope.launch {
                delay(600)
                syncAllTilesToBoard()
            }
        }

        override fun onDescriptorWrite(gatt: BluetoothGatt, descriptor: BluetoothGattDescriptor, status: Int) {
            Log.d(TAG, "Descriptor write complete for ${descriptor.uuid}, status=$status")
            isWritingDescriptor = false
            writeNextDescriptor(gatt)
        }

        @Deprecated("Deprecated for API 33+", ReplaceWith("onCharacteristicChanged"))
        override fun onCharacteristicChanged(gatt: BluetoothGatt, characteristic: BluetoothGattCharacteristic) {
            @Suppress("DEPRECATION")
            handleCharacteristicUpdate(characteristic.uuid, characteristic.value)
        }

        override fun onCharacteristicChanged(
            gatt: BluetoothGatt,
            characteristic: BluetoothGattCharacteristic,
            value: ByteArray
        ) {
            handleCharacteristicUpdate(characteristic.uuid, value)
        }
    }

    private fun handleCharacteristicUpdate(uuid: UUID, value: ByteArray?) {
        if (value == null) return
        when (uuid) {
            BleProtocol.CHAR_BOARD_STATE_UUID -> {
                val parsed = BleProtocol.parseBoardState(value)
                _boardState.value = parsed
            }
            BleProtocol.CHAR_SCAN_TELEMETRY_UUID -> {
                val telemetry = BleProtocol.parseScanTelemetry(value)
                val current = _scanTelemetry.value
                val resolved = if (telemetry.tagUid == null &&
                    telemetry.status == BleProtocol.STATUS_ENERGIZED &&
                    telemetry.activeChannel != null &&
                    telemetry.activeChannel == current.activeChannel &&
                    current.tagUid != null
                ) {
                    telemetry.copy(tagUid = current.tagUid, status = BleProtocol.STATUS_TAG_DETECTED)
                } else {
                    telemetry
                }
                _scanTelemetry.value = resolved

                if (resolved.status == BleProtocol.STATUS_IDLE) {
                    lastAutoHealedUid = null
                }

                // Auto-heal: If tag detected with UID, and board has it as '?' or unregistered, check local DB
                val uid = resolved.tagUid
                val ch = resolved.activeChannel
                if (resolved.status == BleProtocol.STATUS_TAG_DETECTED && !uid.isNullOrBlank() && ch != null) {
                    val boardChar = _boardState.value[ch]
                    if (boardChar == null || boardChar == '?') {
                        val now = System.currentTimeMillis()
                        if (uid != lastAutoHealedUid || now - lastAutoHealedTime > 2000L) {
                            lastAutoHealedUid = uid
                            lastAutoHealedTime = now
                            scope.launch(Dispatchers.IO) {
                                val localTile = dbHelper.getTile(uid)
                                if (localTile != null) {
                                    Log.i(TAG, "🩹 Auto-healing tag $uid as '${localTile.letter}' on square $ch from local DB")
                                    syncTile(localTile.uid, localTile.letter, localTile.points)
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    @SuppressLint("MissingPermission")
    private fun enableNotification(gatt: BluetoothGatt, service: BluetoothGattService, charUuid: UUID) {
        val characteristic = service.getCharacteristic(charUuid) ?: return
        gatt.setCharacteristicNotification(characteristic, true)
        val descriptor = characteristic.getDescriptor(BleProtocol.CLIENT_CONFIG_DESCRIPTOR)
        if (descriptor != null) {
            descriptorQueue.add(descriptor)
        }
    }

    @SuppressLint("MissingPermission")
    private fun writeNextDescriptor(gatt: BluetoothGatt) {
        if (isWritingDescriptor || descriptorQueue.isEmpty()) return
        val descriptor = descriptorQueue.removeAt(0)
        isWritingDescriptor = true

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            gatt.writeDescriptor(descriptor, BluetoothGattDescriptor.ENABLE_NOTIFICATION_VALUE)
        } else {
            @Suppress("DEPRECATION")
            descriptor.value = BluetoothGattDescriptor.ENABLE_NOTIFICATION_VALUE
            @Suppress("DEPRECATION")
            gatt.writeDescriptor(descriptor)
        }
    }

    private fun scheduleAutoReconnect() {
        if (!autoReconnectEnabled) return
        reconnectJob?.cancel()
        reconnectJob = scope.launch {
            delay(3500)
            if (autoReconnectEnabled && _connectionState.value is BleConnectionState.Disconnected) {
                Log.d(TAG, "🔄 Auto-reconnecting to SmartCrossword board...")
                startScan()
            }
        }
    }

    @SuppressLint("MissingPermission")
    fun startScan() {
        if (bluetoothAdapter == null || !bluetoothAdapter.isEnabled) {
            _connectionState.value = BleConnectionState.Error("Bluetooth is disabled")
            return
        }

        if (isScanning || _connectionState.value is BleConnectionState.Connected) return

        val scanner = bluetoothAdapter.bluetoothLeScanner
        if (scanner == null) {
            _connectionState.value = BleConnectionState.Error("BLE Scanner not available")
            return
        }

        val settings = ScanSettings.Builder()
            .setScanMode(ScanSettings.SCAN_MODE_LOW_LATENCY)
            .build()

        _connectionState.value = BleConnectionState.Scanning
        isScanning = true

        try {
            scanner.startScan(null, settings, scanCallback)
            Log.i(TAG, "BLE scan started for ${BleProtocol.DEVICE_NAME}...")

            // Auto-stop scan after 12 seconds, then schedule retry
            scanTimeoutJob?.cancel()
            scanTimeoutJob = scope.launch {
                delay(12000)
                if (isScanning && _connectionState.value is BleConnectionState.Scanning) {
                    stopScan()
                    _connectionState.value = BleConnectionState.Disconnected
                    Log.d(TAG, "Scan timed out without finding board.")
                    scheduleAutoReconnect()
                }
            }
        } catch (e: SecurityException) {
            Log.e(TAG, "Permission denied for startScan", e)
            _connectionState.value = BleConnectionState.Error("Bluetooth permissions missing")
            isScanning = false
        }
    }

    @SuppressLint("MissingPermission")
    fun stopScan() {
        if (!isScanning) return
        try {
            bluetoothAdapter?.bluetoothLeScanner?.stopScan(scanCallback)
        } catch (e: Exception) {
            Log.e(TAG, "Error stopping scan", e)
        }
        isScanning = false
        scanTimeoutJob?.cancel()
    }

    @SuppressLint("MissingPermission")
    fun connect(device: BluetoothDevice) {
        stopScan()
        val devName = device.name ?: BleProtocol.DEVICE_NAME
        _connectionState.value = BleConnectionState.Connecting(devName)
        try {
            activeGatt = device.connectGatt(context, false, gattCallback, BluetoothDevice.TRANSPORT_LE)
        } catch (e: SecurityException) {
            _connectionState.value = BleConnectionState.Error("Bluetooth permission denied")
        }
    }

    @SuppressLint("MissingPermission")
    fun triggerSweep(): Boolean {
        return sendCommand(byteArrayOf(BleProtocol.CMD_TRIGGER_SWEEP))
    }

    @SuppressLint("MissingPermission")
    fun toggleContinuous(): Boolean {
        return sendCommand(byteArrayOf(BleProtocol.CMD_TOGGLE_CONTINUOUS))
    }

    @SuppressLint("MissingPermission")
    fun selectChannel(channel: Int): Boolean {
        if (channel !in 0..15) return false
        return sendCommand(byteArrayOf(BleProtocol.CMD_SELECT_CHANNEL, channel.toByte()))
    }

    @SuppressLint("MissingPermission")
    fun toggleMux(): Boolean {
        return sendCommand(byteArrayOf(BleProtocol.CMD_TOGGLE_MUX))
    }

    @SuppressLint("MissingPermission")
    fun enrollTag(channel: Int, letter: Char, explicitUid: String? = null): Boolean {
        if (channel !in 0..15) return false
        val letCode = letter.uppercaseChar().code.toByte()
        val success = sendCommand(byteArrayOf(BleProtocol.CMD_ENROLL_TAG, channel.toByte(), letCode))
        val uid = explicitUid ?: _scanTelemetry.value.tagUid
        if (!uid.isNullOrBlank()) {
            val points = BleProtocol.getLetterPoints(letter)
            dbHelper.saveTile(uid, letter.uppercaseChar(), points)
            Log.i(TAG, "💾 Persisted enrolled tile $uid -> '$letter' ($points pts) to local DB")
        }
        return success
    }

    @SuppressLint("MissingPermission")
    fun syncTile(uidHex: String, letter: Char, points: Int): Boolean {
        val payload = BleProtocol.buildSyncTilePayload(uidHex, letter, points) ?: return false
        return sendCommand(payload)
    }

    suspend fun syncAllTilesToBoard(): Int = withContext(Dispatchers.IO) {
        val tiles = dbHelper.getAllTiles()
        var count = 0
        for (tile in tiles) {
            val success = syncTile(tile.uid, tile.letter, tile.points)
            if (success) {
                count++
            }
            delay(40)
        }
        Log.i(TAG, "Synced $count/${tiles.size} tiles from local DB to board")
        count
    }

    @SuppressLint("MissingPermission")
    fun commitTurn(): Boolean {
        return sendCommand(byteArrayOf(BleProtocol.CMD_COMMIT_TURN))
    }

    @SuppressLint("MissingPermission")
    fun sendCommand(payload: ByteArray): Boolean {
        val gatt = activeGatt ?: return false
        val service = gatt.getService(BleProtocol.SERVICE_UUID) ?: return false
        val char = service.getCharacteristic(BleProtocol.CHAR_BOARD_COMMAND_UUID) ?: return false

        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            gatt.writeCharacteristic(char, payload, BluetoothGattCharacteristic.WRITE_TYPE_NO_RESPONSE) == BluetoothStatusCodes.SUCCESS
        } else {
            @Suppress("DEPRECATION")
            char.value = payload
            @Suppress("DEPRECATION")
            char.writeType = BluetoothGattCharacteristic.WRITE_TYPE_NO_RESPONSE
            @Suppress("DEPRECATION")
            gatt.writeCharacteristic(char)
        }
    }

    @SuppressLint("MissingPermission")
    fun sendCommand(commandByte: Byte): Boolean {
        return sendCommand(byteArrayOf(commandByte))
    }

    @SuppressLint("MissingPermission")
    fun disconnect() {
        autoReconnectEnabled = false
        reconnectJob?.cancel()
        stopScan()
        try {
            activeGatt?.disconnect()
        } catch (e: Exception) {
            Log.e(TAG, "Error disconnecting GATT", e)
        }
        cleanupGatt()
        _connectionState.value = BleConnectionState.Disconnected
        _scanTelemetry.value = ScanTelemetry()
        _boardState.value = emptyMap()
    }

    @SuppressLint("MissingPermission")
    private fun cleanupGatt() {
        try {
            activeGatt?.close()
        } catch (e: Exception) {
            // Ignore
        }
        activeGatt = null
        descriptorQueue.clear()
        isWritingDescriptor = false
    }
}

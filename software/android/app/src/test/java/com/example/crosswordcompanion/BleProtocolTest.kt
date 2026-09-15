package com.example.crosswordcompanion

import com.example.crosswordcompanion.bluetooth.BleProtocol
import org.junit.Assert.*
import org.junit.Test

class BleProtocolTest {

    @Test
    fun testParseBoardState_emptyBoard() {
        val emptyBytes = ByteArray(16) { 0 }
        val parsed = BleProtocol.parseBoardState(emptyBytes)
        assertTrue("Empty byte array should result in empty tile map", parsed.isEmpty())
    }

    @Test
    fun testParseBoardState_dottedBoard() {
        val dotBytes = "................".toByteArray(Charsets.US_ASCII)
        val parsed = BleProtocol.parseBoardState(dotBytes)
        assertTrue("Dotted board should result in empty tile map", parsed.isEmpty())
    }

    @Test
    fun testParseBoardState_validTiles() {
        // Construct 16-byte board: Square 0='W', Square 5='O', Square 6='R', Square 7='D'
        val bytes = ByteArray(16) { 0 }
        bytes[0] = 'W'.code.toByte()
        bytes[5] = 'O'.code.toByte()
        bytes[6] = 'R'.code.toByte()
        bytes[7] = 'D'.code.toByte()

        val parsed = BleProtocol.parseBoardState(bytes)
        assertEquals(4, parsed.size)
        assertEquals('W', parsed[0])
        assertEquals('O', parsed[5])
        assertEquals('R', parsed[6])
        assertEquals('D', parsed[7])
        assertNull(parsed[1])
    }

    @Test
    fun testParseScanTelemetry_activeScanning() {
        // Channel 5 energized, scanning
        val packet = byteArrayOf(5.toByte(), BleProtocol.STATUS_ENERGIZED.toByte())
        val telemetry = BleProtocol.parseScanTelemetry(packet)
        assertEquals(5, telemetry.activeChannel)
        assertEquals(BleProtocol.STATUS_ENERGIZED, telemetry.status)
    }

    @Test
    fun testParseScanTelemetry_tagHit() {
        // Channel 12 tag detected
        val packet = byteArrayOf(12.toByte(), BleProtocol.STATUS_TAG_DETECTED.toByte())
        val telemetry = BleProtocol.parseScanTelemetry(packet)
        assertEquals(12, telemetry.activeChannel)
        assertEquals(BleProtocol.STATUS_TAG_DETECTED, telemetry.status)
    }

    @Test
    fun testParseScanTelemetry_idle() {
        // Sweep complete / idle
        val packet = byteArrayOf(0xFF.toByte(), BleProtocol.STATUS_IDLE.toByte())
        val telemetry = BleProtocol.parseScanTelemetry(packet)
        assertNull(telemetry.activeChannel)
        assertEquals(BleProtocol.STATUS_IDLE, telemetry.status)
        assertNull(telemetry.tagUid)
    }

    @Test
    fun testParseScanTelemetry_with7ByteUid() {
        // Channel 0, tag detected, 7-byte UID: 04:A1:B2:C3:D4:E5:10
        val packet = byteArrayOf(
            0.toByte(),
            BleProtocol.STATUS_TAG_DETECTED.toByte(),
            7.toByte(),
            0x04.toByte(),
            0xA1.toByte(),
            0xB2.toByte(),
            0xC3.toByte(),
            0xD4.toByte(),
            0xE5.toByte(),
            0x10.toByte()
        )
        val telemetry = BleProtocol.parseScanTelemetry(packet)
        assertEquals(0, telemetry.activeChannel)
        assertEquals(BleProtocol.STATUS_TAG_DETECTED, telemetry.status)
        assertEquals("04:A1:B2:C3:D4:E5:10", telemetry.tagUid)
    }

    @Test
    fun testCommandConstants() {
        assertEquals(0x01.toByte(), BleProtocol.CMD_TRIGGER_SWEEP)
        assertEquals(0x02.toByte(), BleProtocol.CMD_TOGGLE_CONTINUOUS)
        assertEquals(0x03.toByte(), BleProtocol.CMD_SELECT_CHANNEL)
        assertEquals(0x04.toByte(), BleProtocol.CMD_TOGGLE_MUX)
        assertEquals(0x05.toByte(), BleProtocol.CMD_ENROLL_TAG)
        assertEquals(0x10.toByte(), BleProtocol.CMD_COMMIT_TURN)
    }
}


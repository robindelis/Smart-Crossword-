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
        assertEquals(0x06.toByte(), BleProtocol.CMD_SYNC_TILE)
        assertEquals(0x10.toByte(), BleProtocol.CMD_COMMIT_TURN)
    }

    @Test
    fun testParseHexUid_validFormats() {
        val uidColon = "04:A1:B2:C3:D4:E5:10"
        val bytes = BleProtocol.parseHexUid(uidColon)
        assertEquals(7, bytes.size)
        assertEquals(0x04.toByte(), bytes[0])
        assertEquals(0xA1.toByte(), bytes[1])
        assertEquals(0xB2.toByte(), bytes[2])
        assertEquals(0xC3.toByte(), bytes[3])
        assertEquals(0xD4.toByte(), bytes[4])
        assertEquals(0xE5.toByte(), bytes[5])
        assertEquals(0x10.toByte(), bytes[6])

        // Without colons, mixed case
        val uidNoColon = "04a1b2c3d4e510"
        val bytes2 = BleProtocol.parseHexUid(uidNoColon)
        assertArrayEquals(bytes, bytes2)

        // 4-byte UID
        val uid4Byte = "A1:B2:C3:D4"
        val bytes4 = BleProtocol.parseHexUid(uid4Byte)
        assertEquals(4, bytes4.size)
        assertEquals(0xA1.toByte(), bytes4[0])
    }

    @Test
    fun testParseHexUid_invalidInputs() {
        assertTrue("Empty string should return empty byte array", BleProtocol.parseHexUid("").isEmpty())
        assertTrue("Odd length string should return empty byte array", BleProtocol.parseHexUid("04:A").isEmpty())
        assertTrue("Invalid hex characters should return empty byte array", BleProtocol.parseHexUid("04:ZZ:10").isEmpty())
    }

    @Test
    fun testFormatHexUid() {
        val bytes = byteArrayOf(0x04.toByte(), 0xA1.toByte(), 0xB2.toByte())
        val formatted = BleProtocol.formatHexUid(bytes)
        assertEquals("04:A1:B2", formatted)
    }

    @Test
    fun testGetLetterPoints() {
        assertEquals(1, BleProtocol.getLetterPoints('A'))
        assertEquals(1, BleProtocol.getLetterPoints('e'))
        assertEquals(2, BleProtocol.getLetterPoints('D'))
        assertEquals(3, BleProtocol.getLetterPoints('B'))
        assertEquals(4, BleProtocol.getLetterPoints('F'))
        assertEquals(5, BleProtocol.getLetterPoints('K'))
        assertEquals(8, BleProtocol.getLetterPoints('J'))
        assertEquals(10, BleProtocol.getLetterPoints('Q'))
        assertEquals(10, BleProtocol.getLetterPoints('Z'))
        assertEquals(0, BleProtocol.getLetterPoints('?'))
    }

    @Test
    fun testBuildSyncTilePayload() {
        val payload = BleProtocol.buildSyncTilePayload("04:A1:B2:C3:D4:E5:10", 'Z', 10)
        assertNotNull(payload)
        assertEquals(11, payload!!.size)
        assertEquals(BleProtocol.CMD_SYNC_TILE, payload[0])
        assertEquals(7.toByte(), payload[1])
        assertEquals(0x04.toByte(), payload[2])
        assertEquals(0xA1.toByte(), payload[3])
        assertEquals(0xB2.toByte(), payload[4])
        assertEquals(0xC3.toByte(), payload[5])
        assertEquals(0xD4.toByte(), payload[6])
        assertEquals(0xE5.toByte(), payload[7])
        assertEquals(0x10.toByte(), payload[8])
        assertEquals('Z'.code.toByte(), payload[9])
        assertEquals(10.toByte(), payload[10])
    }

    @Test
    fun testBuildSyncTilePayload_invalidUidReturnsNull() {
        assertNull(BleProtocol.buildSyncTilePayload("invalid", 'A', 1))
        assertNull(BleProtocol.buildSyncTilePayload("", 'A', 1))
    }
}


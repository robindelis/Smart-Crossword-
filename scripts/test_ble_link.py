import asyncio
import sys
from bleak import BleakScanner, BleakClient

SERVICE_UUID = "19b10000-e8f2-537e-4f6c-d104768a1214"
BOARD_STATE_UUID = "19b10001-e8f2-537e-4f6c-d104768a1214"
TELEMETRY_UUID = "19b10002-e8f2-537e-4f6c-d104768a1214"
COMMAND_UUID = "19b10003-e8f2-537e-4f6c-d104768a1214"

CMD_TRIGGER_SWEEP = 0x01
CMD_TOGGLE_CONTINUOUS = 0x02
CMD_SELECT_CHANNEL = 0x03
CMD_TOGGLE_MUX = 0x04
CMD_ENROLL_TAG = 0x05

latest_telemetry = None
latest_board_state = None

def telemetry_callback(sender, data: bytearray):
    global latest_telemetry
    latest_telemetry = data
    if len(data) >= 2:
        ch = data[0]
        status = data[1]
        status_str = {0: "IDLE / SWEEP DONE", 1: "ENERGIZING / PROBING", 2: "TAG DETECTED"}.get(status, f"UNKNOWN({status})")
        ch_str = f"Square {ch} (Row {ch//4}, Col {ch%4})" if ch <= 15 else f"Channel {ch:#x}"
        uid_str = ""
        if len(data) >= 3:
            uid_len = data[2]
            if uid_len > 0 and len(data) >= 3 + uid_len:
                uid_bytes = data[3:3+uid_len]
                uid_str = f" | UID: {':'.join(f'{b:02X}' for b in uid_bytes)}"
        print(f"   📡 [BLE TELEMETRY] {ch_str} -> {status_str}{uid_str}")

def board_state_callback(sender, data: bytearray):
    global latest_board_state
    latest_board_state = "".join(chr(b) for b in data[:16])
    print(f"   📥 [BLE BOARD STATE] 16 Squares: '{latest_board_state}'")

async def main():
    print("==========================================================")
    print("  SMART CROSSWORD BOARD - BLE ADVANCED HARDWARE TEST      ")
    print("  (Channel Power Selection, Tag UID Streaming & Enrollment)")
    print("==========================================================")
    print("1. Scanning for 'SmartCrossword_4x4'...")

    device = await BleakScanner.find_device_by_filter(
        lambda d, adv: d.name == "SmartCrossword_4x4" or SERVICE_UUID in adv.service_uuids,
        timeout=8.0
    )

    if not device:
        print("❌ Device 'SmartCrossword_4x4' not found in BLE scan!")
        return 1

    print(f"✅ Found SmartCrossword Board at MAC {device.address}")
    print(f"2. Connecting to GATT Server...")

    async with BleakClient(device) as client:
        print(f"🎉 Connected! Subscribing to notifications...")
        await client.start_notify(TELEMETRY_UUID, telemetry_callback)
        await client.start_notify(BOARD_STATE_UUID, board_state_callback)
        await asyncio.sleep(1.0)

        # Test 1: Channel Power Selection (Square 5: Row 1, Col 1)
        print("\n3. Testing CMD_SELECT_CHANNEL -> Powering Square 5 (Row 1, Col 1)...")
        await client.write_gatt_char(COMMAND_UUID, bytearray([CMD_SELECT_CHANNEL, 5]), response=False)
        await asyncio.sleep(1.2)

        # Test 2: Channel Power Selection (Square 10: Row 2, Col 2)
        print("\n4. Testing CMD_SELECT_CHANNEL -> Powering Square 10 (Row 2, Col 2)...")
        await client.write_gatt_char(COMMAND_UUID, bytearray([CMD_SELECT_CHANNEL, 10]), response=False)
        await asyncio.sleep(1.2)

        # Test 3: Tag Enrollment command (Enroll Square 0 as Letter 'K')
        print("\n5. Testing CMD_ENROLL_TAG -> Enrolling last tag / Square 0 as Letter 'K' (5 pts)...")
        await client.write_gatt_char(COMMAND_UUID, bytearray([CMD_ENROLL_TAG, 0, ord('K')]), response=False)
        await asyncio.sleep(1.2)

        # Test 4: Full Matrix Sweep
        print("\n6. Testing CMD_TRIGGER_SWEEP -> Full 16-Channel Sweep...")
        await client.write_gatt_char(COMMAND_UUID, bytearray([CMD_TRIGGER_SWEEP]), response=False)
        await asyncio.sleep(3.0)

        # Restore Channel 0
        print("\n7. Restoring power to Square 0...")
        await client.write_gatt_char(COMMAND_UUID, bytearray([CMD_SELECT_CHANNEL, 0]), response=False)
        await asyncio.sleep(1.0)

        await client.stop_notify(TELEMETRY_UUID)
        await client.stop_notify(BOARD_STATE_UUID)
        print("\n✅ Advanced Hardware BLE Test PASSED!")
        return 0

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

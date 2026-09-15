import asyncio
import sys
from bleak import BleakScanner, BleakClient

SERVICE_UUID = "19b10000-e8f2-537e-4f6c-d104768a1214"
BOARD_STATE_UUID = "19b10001-e8f2-537e-4f6c-d104768a1214"
TELEMETRY_UUID = "19b10002-e8f2-537e-4f6c-d104768a1214"
COMMAND_UUID = "19b10003-e8f2-537e-4f6c-d104768a1214"

def telemetry_callback(sender, data: bytearray):
    if len(data) >= 2:
        ch = data[0]
        status = data[1]
        status_str = {0: "IDLE / SWEEP DONE", 1: "ENERGIZING / PROBING", 2: "TAG DETECTED"}.get(status, f"UNKNOWN({status})")
        ch_str = f"Square {ch} (Row {ch//4}, Col {ch%4})" if ch <= 15 else f"Channel {ch:#x}"
        print(f"   📡 [BLE TELEMETRY] {ch_str} -> {status_str}")

def board_state_callback(sender, data: bytearray):
    board_chars = "".join(chr(b) for b in data[:16])
    print(f"   📥 [BLE BOARD STATE] 16 Squares: '{board_chars}'")

async def main():
    print("==================================================")
    print("  SMART CROSSWORD BOARD - BLE AIR INTERFACE TEST  ")
    print("==================================================")
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
        print(f"🎉 Connected! GATT Services Discovered:")
        for service in client.services:
            if service.uuid.lower() == SERVICE_UUID.lower():
                print(f"   [FOUND] Smart Crossword Service: {service.uuid}")
                for char in service.characteristics:
                    print(f"      - Char {char.uuid} ({','.join(char.properties)})")

        # Read initial board state
        board_bytes = await client.read_gatt_char(BOARD_STATE_UUID)
        initial_board = "".join(chr(b) for b in board_bytes[:16])
        print(f"\n3. Initial Board State Characteristic: '{initial_board}'")

        # Subscribe to notifications
        print("4. Subscribing to Telemetry & Board State notifications...")
        await client.start_notify(TELEMETRY_UUID, telemetry_callback)
        await client.start_notify(BOARD_STATE_UUID, board_state_callback)

        print("\n5. Sending Sweep Command (0x01) over BLE...")
        await client.write_gatt_char(COMMAND_UUID, bytearray([0x01]), response=False)

        print("6. Listening to live telemetry stream for 5 seconds...")
        await asyncio.sleep(5.0)

        print("\n7. Stopping notifications and disconnecting...")
        await client.stop_notify(TELEMETRY_UUID)
        await client.stop_notify(BOARD_STATE_UUID)
        print("✅ BLE Air Interface Verification PASSED!")
        return 0

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

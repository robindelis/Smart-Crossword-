#!/usr/bin/env bash
# inspect_db.sh - View or clear Crossword Companion SQLite database on connected device

PACKAGE="com.example.crosswordcompanion"
DB_NAME="crossword_companion.db"
TEMP_DB="/tmp/crossword_companion_inspect.db"

if [ "$1" == "--clear" ] || [ "$1" == "-c" ]; then
    echo "Clearing app data and database for $PACKAGE..."
    adb shell pm clear "$PACKAGE"
    echo "Done! Local database is completely reset."
    exit 0
fi

echo "=== Crossword Companion Database Inspector ==="
echo "Target: $PACKAGE ($DB_NAME)"
echo ""

# Pull the DB file via run-as
if ! adb exec-out run-as "$PACKAGE" cat "databases/$DB_NAME" > "$TEMP_DB" 2>/dev/null; then
    echo "Error: Could not read $DB_NAME from device."
    echo "Ensure the device is connected via ADB and the app has been opened at least once."
    exit 1
fi

if [ ! -s "$TEMP_DB" ]; then
    echo "Database file is empty or does not exist yet."
    exit 0
fi

echo "--- Tables ---"
sqlite3 "$TEMP_DB" ".tables"
echo ""

echo "--- USERS ---"
sqlite3 -box "$TEMP_DB" "SELECT id, display_name, unique_username, email, is_logged_in FROM users;" 2>/dev/null || sqlite3 -header -column "$TEMP_DB" "SELECT * FROM users;"
echo ""

echo "--- FRIENDS ---"
sqlite3 -box "$TEMP_DB" "SELECT id, display_name, unique_username, is_board, status FROM friends;" 2>/dev/null || sqlite3 -header -column "$TEMP_DB" "SELECT * FROM friends;"
echo ""

echo "--- GAMES ---"
sqlite3 -box "$TEMP_DB" "SELECT * FROM games;" 2>/dev/null || sqlite3 -header -column "$TEMP_DB" "SELECT * FROM games;"
echo ""

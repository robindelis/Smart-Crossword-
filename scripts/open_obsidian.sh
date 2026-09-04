#!/usr/bin/env bash
# open_obsidian.sh - Launch Obsidian and open the Smart Crossword Board Project Cockpit

VAULT_DIR="/home/robin/Smart-Crossword-Board"
VAULT_NAME="Smart-Crossword-Board"
CANVAS_FILE="Project_Cockpit.canvas"

echo "Launching Obsidian into '${VAULT_NAME}'..."

# Check if obsidian binary is available
if ! command -v obsidian &>/dev/null; then
  echo "Error: 'obsidian' command not found in PATH." >&2
  exit 1
fi

# Attempt to open via obsidian:// URI scheme
if command -v xdg-open &>/dev/null; then
  xdg-open "obsidian://open?vault=${VAULT_NAME}&file=${CANVAS_FILE}" &>/dev/null &
else
  obsidian "obsidian://open?vault=${VAULT_NAME}&file=${CANVAS_FILE}" &>/dev/null &
fi

echo "Obsidian cockpit opened successfully!"

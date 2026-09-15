# This document lists all the potential issues the project will suffer from
## 1. Multiple Game Handling
* **Whilst handling multiple games at a time is easy on fully virtual setups, it can get annoying to reset the physical board on every new game**
* **No solution found yet**
## 2.  Full Board Scan speed
* **Scanning all possible squares is not optimal because some squares are too far away from the playing zone and therefore not legally playable in any scenario**
* **Potential Solutions:**
	* Quick presence only pre-scan (LPCD), no full UUID reads on all the squares yet, and only perform UUID read on squares where a tile is detected.
	* Hold a potential legal squares list and only perform scans on these squares. Update the list on every new tile set event (only check in lines once a new tile has been layed down).
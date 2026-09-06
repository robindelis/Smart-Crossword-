# Multi-Language Lexicons & Tile Sets

The Smart Crossword Board has built-in support for **5 official languages**: English, French, Dutch, German, and Spanish.

---

## 1. Official Word Lists (2.1M Total Words)

All word lists are cleaned, sorted, and stored in [`data/`](data/):

| Language | Official Tournament Lexicon | Word Count | File |
| :--- | :--- | :--- | :--- |
| **English (EN)** | **ENABLE1 / TWL06** | 168,551 words | [`data/dict_en.txt`](data/dict_en.txt) |
| **French (FR)** | **ODS8** (Officiel du Scrabble) | 402,325 words | [`data/dict_fr.txt`](data/dict_fr.txt) |
| **Dutch (NL)** | **OpenTaal** Wordlist | 337,502 words | [`data/dict_nl.txt`](data/dict_nl.txt) |
| **German (DE)** | **Scrabble DE** Tournament List | 590,751 words | [`data/dict_de.txt`](data/dict_de.txt) |
| **Spanish (ES)** | **FISE** (Federación de Scrabble) | 635,091 words | [`data/dict_es.txt`](data/dict_es.txt) |

Total verified vocabulary: **2,134,220 words**.

---

## 2. Letter Point Values & Tile Differences

Letter scores and tile frequencies are completely localized per language:

* **French (FR - 102 tiles)**:
  * 10 pts: `W`, `K`, `X`, `Y`, `Z`
  * 8 pts: `J`, `Q`
  * 4 pts: `F`, `H`, `V`
  * 3 pts: `B`, `C`, `P`
  * 2 pts: `D`, `M`, `G`
  * 1 pt: `E` (15 tiles), `A` (9), `I` (8), `N`, `O`, `R`, `S`, `T`, `U`, `L`
* **Dutch (NL - 102 tiles)**:
  * 10 pts: `Q`
  * 8 pts: `X`, `Y`
  * 5 pts: `C`, `W`
  * 4 pts: `F`, `H`, `J`, `U`, `V`, `Z`
  * 3 pts: `B`, `G`, `K`, `L`, `M`, `P`
  * 2 pts: `D`, `R`, `S`, `T`
  * 1 pt: `E` (18 tiles), `N` (10), `A` (6), `O` (6), `I` (4)
* **German (DE - 102 tiles)**:
  * Includes regional letters: `Ä` (6 pts), `Ö` (8 pts), `Ü` (6 pts).
  * 10 pts: `Q`, `Y`
  * 8 pts: `X`, `Ö`
  * 6 pts: `Ä`, `J`, `Ü`, `V`
  * 4 pts: `C`, `F`, `K`, `P`
  * 3 pts: `B`, `M`, `W`, `Z`
  * 2 pts: `G`, `H`, `L`, `O`
  * 1 pt: `E` (15), `N` (9), `S` (7), `I` (6), `R` (6), `T` (6), `U` (6), `A` (5), `D` (4)
* **Spanish (ES - 100 tiles - FISE International Standard)**:
  * Includes dedicated single-square tiles for Spanish character and digraphs:
    * `Ñ` (**8 pts**, 1 tile)
    * `CH` (**5 pts**, 1 tile) — occupies 1 board cell
    * `LL` (**8 pts**, 1 tile) — occupies 1 board cell
    * `RR` (**8 pts**, 1 tile) — occupies 1 board cell
  * 10 pts: `Z` (1)
  * 8 pts: `J` (1), `Ñ` (1), `X` (1), `LL` (1), `RR` (1)
  * 5 pts: `Q` (1), `CH` (1)
  * 4 pts: `F` (1), `H` (2), `V` (1), `Y` (1)
  * 3 pts: `B` (2), `C` (4), `M` (2), `P` (2)
  * 2 pts: `D` (5), `G` (2)
  * 1 pt: `A` (12), `E` (12), `O` (9), `I` (6), `S` (6), `N` (5), `R` (5), `U` (5), `L` (4), `T` (4)
  * Note: The North American Hasbro edition uses 103 tiles (drops `CH` tile and adds `K`/`W`). The Smart Crossword Board uses the official 100-tile FISE International standard adopted across Spain and Latin America.
* **English (EN - 100 tiles)**:
  * Standard Scrabble distribution: 12 `E`, 9 `A`, 9 `I`, 8 `O`, 6 `N`, 6 `R`, 6 `T`, 4 `D`, 4 `L`, 4 `S`, 4 `U`, 3 `G`, 2 `B`, 2 `C`, 2 `F`, 2 `H`, 2 `M`, 2 `P`, 2 `V`, 2 `W`, 2 `Y`, 1 `J` (8 pts), 1 `K` (5 pts), 1 `Q` (10 pts), 1 `X` (8 pts), 1 `Z` (10 pts), 2 Blanks (0 pts).

See [`commercial/tile_and_rfid_sourcing.md`](file:///home/robin/Smart-Crossword-Board/commercial/tile_and_rfid_sourcing.md) for the master letter-by-letter table across all 5 languages and procurement specs.

---

## 3. Spoken Referee & Letter Spelling

When moves are confirmed, the voice referee speaks naturally in the active language:
* Spells out letters before pronouncing the word:
  * English: *"Valid move! H - E - L - L - O. HELLO, for 18 points."*
  * French: *"Coup valide ! B - O - N - J - O - U - R. BONJOUR, pour 68 points."*
  * Dutch: *"Geldige zet! F - I - E - T - S. FIETS, voor 14 punten."*
  * German: *"Gültiger Zug! S - P - I - E - L. SPIEL, für 18 Punkte."*
  * Spanish: *"¡Jugada válida! H - O - L - A. HOLA, por 14 puntos."*

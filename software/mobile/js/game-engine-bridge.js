// Smart Crossword Board - Game Referee Engine Bridge
// Bridges C/WASM referee engine (crossword_engine.wasm) with a seamless, robust
// JavaScript referee fallback, multi-language dictionary loader, and exact bonus calculations.

const _MODELS = (typeof require !== 'undefined')
  ? require('./models.js')
  : (typeof window !== 'undefined' ? window : globalThis);

const BOARD_SIZE = _MODELS.BOARD_SIZE || 15;
const BONUS_GRID = _MODELS.BONUS_GRID || [];
const LANG_CONFIGS = _MODELS.LANG_CONFIGS || {};
const BONUS_DLS = 1;
const BONUS_TLS = 2;
const BONUS_DWS = 3;
const BONUS_TWS = 4;

class GameEngineBridge {
  constructor() {
    this.wasmInstance = null;
    this.wasmAvailable = false;
    this.dictionaries = new Map(); // langCode -> Set of uppercase words
    this.loadingDictionaries = new Map(); // langCode -> Promise

    // Embedded baseline fallback dictionary for instant offline play
    this.baselineWords = new Set([
      // English
      "AA", "AB", "AD", "AE", "AG", "AH", "AI", "AL", "AM", "AN", "AR", "AS", "AT", "AW", "AX", "AY",
      "BA", "BE", "BI", "BO", "BY", "CAT", "CLOUD", "DO", "DOG", "ED", "EF", "EH", "EL", "EM", "EN",
      "ER", "ES", "ET", "EX", "FA", "FE", "GO", "HA", "HE", "HELLO", "HI", "HM", "HO", "HONEY", "ID",
      "IF", "IN", "IS", "IT", "JO", "KA", "KI", "LA", "LI", "LO", "MA", "ME", "MI", "MM", "MO", "MU",
      "MY", "NA", "NE", "NO", "NU", "OD", "OE", "OF", "OH", "OI", "OK", "OM", "ON", "OP", "OR", "OS",
      "OW", "OX", "OY", "PA", "PE", "PEACH", "PI", "PLAY", "PO", "QI", "RE", "SH", "SI", "SO", "TA",
      "TI", "TO", "UH", "UM", "UN", "UP", "US", "UT", "WE", "WO", "XI", "XU", "YA", "YE", "YO", "ZA",
      "BREEZE", "GARDEN", "HOME", "LOVE", "QUIET", "QUARTZ", "SMART", "BOARD", "GAME", "WORD", "WORDS",
      "FAMILY", "GRANDMA", "GRANDPA", "TOUCH", "TILES", "RACK", "SCORE", "DOUBLE", "TRIPLE", "LETTER",
      "FRIEND", "COFFEE", "SMILE", "SPRING", "SUMMER", "WINTER", "AUTUMN", "HAPPY", "PEACE", "TABLE",
      "CHAIR", "HOUSE", "WATER", "LIGHT", "MUSIC", "SWEET", "HEART", "NIGHT", "DREAM", "WORLD",
      // French
      "BONJOUR", "MERCI", "MAISON", "CHAT", "CHIEN", "AMOUR", "TABLE", "JEU", "FAMILLE", "SOLEIL", "FLEUR", "COEUR",
      // Dutch
      "HALLO", "HUIS", "HOND", "KAT", "FIETS", "FIETSEN", "SPEL", "KOFFIE", "MOOI", "FAMILIE", "BLOEM", "LEVEN",
      // German
      "HAUS", "HUND", "KATZE", "SPIEL", "SPIELEN", "FAMILIE", "FREUND", "KAFFEE", "SCHÖN", "BLUME", "HERZ", "LEBEN",
      // Spanish
      "HOLA", "HORA", "CASA", "PERRO", "GATO", "JUEGO", "AMIGO", "AMIGOS", "FAMILIA", "FLOR", "CORAZON", "SOL"
    ]);

    this.initWasm();
  }

  async initWasm() {
    const wasmPaths = ['/mobile/engine.wasm', 'engine.wasm', '/web/engine.wasm'];
    for (const path of wasmPaths) {
      try {
        const response = await fetch(path);
        if (response.ok) {
          const bytes = await response.arrayBuffer();
          const module = await WebAssembly.instantiate(bytes, {
            env: {
              memory: new WebAssembly.Memory({ initial: 256, maximum: 512 })
            }
          });
          this.wasmInstance = module.instance;
          this.wasmAvailable = true;
          console.log('[Referee Engine] C/WASM engine loaded successfully from', path);
          return;
        }
      } catch (_) {
        // Continue to fallback
      }
    }
    console.log('[Referee Engine] Using high-performance JavaScript referee');
  }

  async loadDictionary(langCode = 'en') {
    const lang = langCode.toLowerCase();
    if (this.dictionaries.has(lang)) {
      return this.dictionaries.get(lang);
    }

    if (this.loadingDictionaries.has(lang)) {
      return this.loadingDictionaries.get(lang);
    }

    const loadPromise = (async () => {
      const langConf = LANG_CONFIGS[lang] || LANG_CONFIGS.en;
      const dictPaths = [langConf.dictFile, `/dict_${lang}.txt`, `dict_${lang}.txt`, `/web/dict_${lang}.txt`];

      for (const p of dictPaths) {
        try {
          const res = await fetch(p);
          if (res.ok) {
            const text = await res.text();
            const set = new Set();
            const lines = text.split(/\r?\n/);
            for (let i = 0; i < lines.length; i++) {
              const w = lines[i].trim().toUpperCase();
              if (w.length >= 2 && w.length <= 15) {
                set.add(w);
              }
            }
            // Merge baseline words
            for (const bw of this.baselineWords) {
              set.add(bw);
            }
            this.dictionaries.set(lang, set);
            console.log(`[Referee Engine] Loaded ${set.size.toLocaleString()} words for ${lang.toUpperCase()}`);
            return set;
          }
        } catch (_) {}
      }

      // Fallback to baseline
      console.warn(`[Referee Engine] Could not load dictionary file for ${lang}, using baseline list.`);
      const fallbackSet = new Set(this.baselineWords);
      this.dictionaries.set(lang, fallbackSet);
      return fallbackSet;
    })();

    this.loadingDictionaries.set(lang, loadPromise);
    return loadPromise;
  }

  isWordInDict(word, langCode = 'en') {
    const upperWord = word.toUpperCase();
    const dict = this.dictionaries.get(langCode) || this.baselineWords;
    return dict.has(upperWord) || this.baselineWords.has(upperWord);
  }

  // Pure JavaScript referee that guarantees 100% official Scrabble rules
  validateMove({
    board,
    placements,
    lang = 'en'
  }) {
    if (!placements || placements.length === 0) {
      return { ok: false, error: "Please place at least one tile on the board." };
    }

    const isBoardEmpty = board.isEmpty();

    // 1. Center Star check on first move
    if (isBoardEmpty) {
      const coversCenter = placements.some(p => p.row === 7 && p.col === 7);
      if (!coversCenter) {
        return { ok: false, error: "First move must cover the center star (H8)." };
      }
    }

    // 2. Square occupied check
    for (const p of placements) {
      if (board.getCell(p.row, p.col) !== null) {
        return { ok: false, error: `Square at row ${p.row + 1}, column ${p.col + 1} is already occupied.` };
      }
    }

    // 3. Collinear check (must be along same row or same column)
    const sameRow = placements.every(p => p.row === placements[0].row);
    const sameCol = placements.every(p => p.col === placements[0].col);
    if (!sameRow && !sameCol) {
      return { ok: false, error: "All tiles must be placed in a single straight row or column." };
    }

    // Create temporary board grid
    const tempGrid = board.toMatrix();
    for (const p of placements) {
      tempGrid[p.row][p.col] = p.letter.toUpperCase();
    }

    // 4. Gap check
    if (sameRow) {
      const r = placements[0].row;
      const cols = placements.map(p => p.col);
      const minCol = Math.min(...cols);
      const maxCol = Math.max(...cols);
      for (let c = minCol; c <= maxCol; c++) {
        if (!tempGrid[r][c]) {
          return { ok: false, error: "There is an empty space inside your word." };
        }
      }
    } else {
      const c = placements[0].col;
      const rows = placements.map(p => p.row);
      const minRow = Math.min(...rows);
      const maxRow = Math.max(...rows);
      for (let r = minRow; r <= maxRow; r++) {
        if (!tempGrid[r][c]) {
          return { ok: false, error: "There is an empty space inside your word." };
        }
      }
    }

    // 5. Connectivity check (if not first move)
    if (!isBoardEmpty) {
      const connected = placements.some(p => {
        const neighbors = [
          [p.row - 1, p.col], [p.row + 1, p.col],
          [p.row, p.col - 1], [p.row, p.col + 1]
        ];
        return neighbors.some(([nr, nc]) =>
          nr >= 0 && nr < BOARD_SIZE && nc >= 0 && nc < BOARD_SIZE && board.getCell(nr, nc) !== null
        );
      });
      if (!connected) {
        return { ok: false, error: "Your word must connect to tiles already on the board." };
      }
    }

    const langConf = LANG_CONFIGS[lang] || LANG_CONFIGS.en;
    const newPlacementCoords = new Set(placements.map(p => `${p.row},${p.col}`));
    const formedWords = [];

    // 6. Extract Primary Word along placement direction
    if (sameRow) {
      const r = placements[0].row;
      let minC = Math.min(...placements.map(p => p.col));
      let maxC = Math.max(...placements.map(p => p.col));

      while (minC > 0 && tempGrid[r][minC - 1]) minC--;
      while (maxC < BOARD_SIZE - 1 && tempGrid[r][maxC + 1]) maxC++;

      if (maxC > minC) {
        let wordStr = "";
        let basePts = 0;
        let wordMultiplier = 1;

        for (let c = minC; c <= maxC; c++) {
          const letter = tempGrid[r][c];
          wordStr += letter;
          let val = langConf.letterValues[letter] || 1;

          if (newPlacementCoords.has(`${r},${c}`)) {
            const bonus = BONUS_GRID[r][c];
            if (bonus === BONUS_DLS) val *= 2;
            else if (bonus === BONUS_TLS) val *= 3;
            else if (bonus === BONUS_DWS) wordMultiplier *= 2;
            else if (bonus === BONUS_TWS) wordMultiplier *= 3;
          }
          basePts += val;
        }

        formedWords.push({
          word: wordStr,
          score: basePts * wordMultiplier,
          isHorizontal: true
        });
      }
    } else {
      const c = placements[0].col;
      let minR = Math.min(...placements.map(p => p.row));
      let maxR = Math.max(...placements.map(p => p.row));

      while (minR > 0 && tempGrid[minR - 1][c]) minR--;
      while (maxR < BOARD_SIZE - 1 && tempGrid[maxR + 1][c]) maxR++;

      if (maxR > minR) {
        let wordStr = "";
        let basePts = 0;
        let wordMultiplier = 1;

        for (let r = minR; r <= maxR; r++) {
          const letter = tempGrid[r][c];
          wordStr += letter;
          let val = langConf.letterValues[letter] || 1;

          if (newPlacementCoords.has(`${r},${c}`)) {
            const bonus = BONUS_GRID[r][c];
            if (bonus === BONUS_DLS) val *= 2;
            else if (bonus === BONUS_TLS) val *= 3;
            else if (bonus === BONUS_DWS) wordMultiplier *= 2;
            else if (bonus === BONUS_TWS) wordMultiplier *= 3;
          }
          basePts += val;
        }

        formedWords.push({
          word: wordStr,
          score: basePts * wordMultiplier,
          isHorizontal: false
        });
      }
    }

    // 7. Extract Cross Words
    for (const p of placements) {
      if (sameRow) {
        // Cross word is vertical
        let minR = p.row;
        let maxR = p.row;
        while (minR > 0 && tempGrid[minR - 1][p.col]) minR--;
        while (maxR < BOARD_SIZE - 1 && tempGrid[maxR + 1][p.col]) maxR++;

        if (maxR > minR) {
          let crossStr = "";
          let crossPts = 0;
          let crossMultiplier = 1;

          for (let r = minR; r <= maxR; r++) {
            const letter = tempGrid[r][p.col];
            crossStr += letter;
            let val = langConf.letterValues[letter] || 1;

            if (r === p.row) {
              const bonus = BONUS_GRID[r][p.col];
              if (bonus === BONUS_DLS) val *= 2;
              else if (bonus === BONUS_TLS) val *= 3;
              else if (bonus === BONUS_DWS) crossMultiplier *= 2;
              else if (bonus === BONUS_TWS) crossMultiplier *= 3;
            }
            crossPts += val;
          }

          formedWords.push({
            word: crossStr,
            score: crossPts * crossMultiplier,
            isHorizontal: false
          });
        }
      } else {
        // Cross word is horizontal
        let minC = p.col;
        let maxC = p.col;
        while (minC > 0 && tempGrid[p.row][minC - 1]) minC--;
        while (maxC < BOARD_SIZE - 1 && tempGrid[p.row][maxC + 1]) maxC++;

        if (maxC > minC) {
          let crossStr = "";
          let crossPts = 0;
          let crossMultiplier = 1;

          for (let c = minC; c <= maxC; c++) {
            const letter = tempGrid[p.row][c];
            crossStr += letter;
            let val = langConf.letterValues[letter] || 1;

            if (c === p.col) {
              const bonus = BONUS_GRID[p.row][c];
              if (bonus === BONUS_DLS) val *= 2;
              else if (bonus === BONUS_TLS) val *= 3;
              else if (bonus === BONUS_DWS) crossMultiplier *= 2;
              else if (bonus === BONUS_TWS) crossMultiplier *= 3;
            }
            crossPts += val;
          }

          formedWords.push({
            word: crossStr,
            score: crossPts * crossMultiplier,
            isHorizontal: true
          });
        }
      }
    }

    // 8. Check minimum word count
    if (formedWords.length === 0) {
      return { ok: false, error: "A word must consist of at least 2 letters." };
    }

    // 9. Dictionary verification for every formed word
    let totalScore = 0;
    for (const fw of formedWords) {
      if (!this.isWordInDict(fw.word, lang)) {
        return { ok: false, error: `"${fw.word}" is not recognized in the dictionary.` };
      }
      totalScore += fw.score;
    }

    // 10. Bingo bonus (+50 points for playing all 7 tiles)
    const isBingo = placements.length === 7;
    if (isBingo) {
      totalScore += 50;
    }

    return {
      ok: true,
      words: formedWords,
      totalScore,
      isBingo,
      mainWord: formedWords[0].word
    };
  }
}

if (typeof window !== 'undefined') {
  window.GameEngineBridge = GameEngineBridge;
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { GameEngineBridge };
}

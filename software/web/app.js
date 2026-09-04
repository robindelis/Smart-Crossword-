// Smart Crossword Board - Multi-Language Game Controller & Engine
// Supported Languages: English (EN), French (FR), Dutch (NL), German (DE), Spanish (ES)

const BOARD_SIZE = 15;

// Bonus grid: 0: None, 1: DLS, 2: TLS, 3: DWS, 4: TWS
const BONUS_GRID = [
  [4, 0, 0, 1, 0, 0, 0, 4, 0, 0, 0, 1, 0, 0, 4],
  [0, 3, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 3, 0],
  [0, 0, 3, 0, 0, 0, 1, 0, 1, 0, 0, 0, 3, 0, 0],
  [1, 0, 0, 3, 0, 0, 0, 1, 0, 0, 0, 3, 0, 0, 1],
  [0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0],
  [0, 2, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 2, 0],
  [0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0],
  [4, 0, 0, 1, 0, 0, 0, 3, 0, 0, 0, 1, 0, 0, 4],
  [0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0],
  [0, 2, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 2, 0],
  [0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0],
  [1, 0, 0, 3, 0, 0, 0, 1, 0, 0, 0, 3, 0, 0, 1],
  [0, 0, 3, 0, 0, 0, 1, 0, 1, 0, 0, 0, 3, 0, 0],
  [0, 3, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 3, 0],
  [4, 0, 0, 1, 0, 0, 0, 4, 0, 0, 0, 1, 0, 0, 4]
];

// Language configurations with official Scrabble tile points and distributions
const LANGUAGES = {
  en: {
    name: "English",
    flag: "🇬🇧",
    speechLocale: "en-US",
    dictFile: "dict_en.txt",
    remotePlayer: "Sarah (Phone)",
    letterValues: {
      A: 1, B: 3, C: 3, D: 2, E: 1, F: 4, G: 2, H: 4, I: 1, J: 8, K: 5, L: 1, M: 3,
      N: 1, O: 1, P: 3, Q: 10, R: 1, S: 1, T: 1, U: 1, V: 4, W: 4, X: 8, Y: 4, Z: 10
    },
    tileBag: "AAAAAAAAABBCCDDDDEEEEEEEEEEEEFFGGGHHIIIIIIIIIJKLLLLMMNNNNNNOOOOOOOOPPQRRRRRRSSSSTTTTTTUUUUVVWWXYYZ",
    turn1Rack: ["H", "E", "L", "L", "O", "A", "T"],
    remoteSim: {
      turn1: { word: "HELLO", r: 7, c: 7, isHorizontal: true, score: 18 },
      turn2: { branchChar: "H", branchR: 7, branchC: 7, word: "HONEY", r: 8, c: 7, isHorizontal: false, score: 15 }
    },
    strings: {
      ready: "Ready ({count} words loaded). Place tiles covering center star (H8).",
      loading: "Loading English dictionary ({file})...",
      centerError: "First move must cover the center star (H8).",
      lineError: "All tiles must be in a single row or column.",
      gapError: "There is an empty space inside your word.",
      connectError: "Your word must connect to tiles already on the board.",
      minLenError: "Word must be at least 2 letters.",
      notInDict: "'{word}' is not in the dictionary.",
      validMove: "Valid move! You played {word} for {score} points.",
      voiceMove: "Valid move! You played {word} for {score} points.",
      tilesRecalled: "Tiles recalled to rack.",
      newGameStarted: "New game started. Place tiles covering center star (H8).",
      voiceNewGame: "New game started. It's your turn.",
      remoteTurn1: "{player} played {word} on center for {score} points!",
      remoteTurn2: "{player} played {word} for {score} points!",
      remoteDone: "Remote move already completed. Start a new game to reset."
    }
  },
  fr: {
    name: "Français",
    flag: "🇫🇷",
    speechLocale: "fr-FR",
    dictFile: "dict_fr.txt",
    remotePlayer: "Sophie (Téléphone)",
    letterValues: {
      A: 1, B: 3, C: 3, D: 2, E: 1, F: 4, G: 2, H: 4, I: 1, J: 8, K: 10, L: 1, M: 2,
      N: 1, O: 1, P: 3, Q: 8, R: 1, S: 1, T: 1, U: 1, V: 4, W: 10, X: 10, Y: 10, Z: 10
    },
    tileBag: "AAAAAAAAABBCDDEEEEEEEEEEEEEEEFFGGHHIIIIIIIIJKLLLLLMMMNNNNNNOOOOOOPPQRRRRRRSSSSSSTTTTTTUUUUUUVVWXYZ",
    turn1Rack: ["B", "O", "N", "J", "O", "U", "R"],
    remoteSim: {
      turn1: { word: "CHAT", r: 7, c: 7, isHorizontal: true, score: 18 },
      turn2: { branchChar: "C", branchR: 7, branchC: 7, word: "COEUR", r: 8, c: 7, isHorizontal: false, score: 14 }
    },
    strings: {
      ready: "Prêt ({count} mots chargés). Placez des lettres sur l'étoile centrale (H8).",
      loading: "Chargement du dictionnaire français ({file})...",
      centerError: "Le premier mot doit passer par l'étoile centrale (H8).",
      lineError: "Toutes les lettres doivent être alignées sur une ligne ou colonne.",
      gapError: "Il y a un espace vide dans votre mot.",
      connectError: "Votre mot doit être rattaché aux lettres du plateau.",
      minLenError: "Un mot doit comporter au moins 2 lettres.",
      notInDict: "« {word} » n'est pas dans le dictionnaire.",
      validMove: "Coup valide ! Vous avez joué {word} pour {score} points.",
      voiceMove: "Coup valide ! Vous avez joué {word} pour {score} points.",
      tilesRecalled: "Lettres remises sur votre chevalet.",
      newGameStarted: "Nouvelle partie commencée. Placez vos lettres sur l'étoile centrale.",
      voiceNewGame: "Nouvelle partie commencée. À vous de jouer.",
      remoteTurn1: "{player} a joué {word} au centre pour {score} points !",
      remoteTurn2: "{player} a joué {word} pour {score} points !",
      remoteDone: "Coup simulé déjà joué. Démarrez une nouvelle partie pour recommencer."
    }
  },
  nl: {
    name: "Nederlands",
    flag: "🇳🇱",
    speechLocale: "nl-NL",
    dictFile: "dict_nl.txt",
    remotePlayer: "Sanne (Telefoon)",
    letterValues: {
      A: 1, B: 3, C: 5, D: 2, E: 1, F: 4, G: 3, H: 4, I: 1, J: 4, K: 3, L: 3, M: 3,
      N: 1, O: 1, P: 3, Q: 10, R: 2, S: 2, T: 2, U: 4, V: 4, W: 5, X: 8, Y: 8, Z: 4
    },
    tileBag: "AAAAAABBCCDDDDDEEEEEEEEEEEEEEEEEEFFGGGHHIIIIJJKKKLLLMMMNNNNNNNNNNOOOOOOPPQRRRRRSSSSSTTTTTUUUVVWWXYZZ",
    turn1Rack: ["F", "I", "E", "T", "S", "E", "N"],
    remoteSim: {
      turn1: { word: "HUIS", r: 7, c: 7, isHorizontal: true, score: 16 },
      turn2: { branchChar: "H", branchR: 7, branchC: 7, word: "HOND", r: 8, c: 7, isHorizontal: false, score: 14 }
    },
    strings: {
      ready: "Klaar ({count} woorden geladen). Leg letters over de centrale ster (H8).",
      loading: "Nederlands woordenboek laden ({file})...",
      centerError: "De eerste zet moet het middelste vakje (H8) bedekken.",
      lineError: "Alle letters moeten op één rij of kolom liggen.",
      gapError: "Er zit een lege plek in je woord.",
      connectError: "Je woord moet aansluiten op bestaande letters van het bord.",
      minLenError: "Een woord moet minstens 2 letters bevatten.",
      notInDict: "'{word}' staat niet in het woordenboek.",
      validMove: "Geldige zet! Je speelde {word} voor {score} punten.",
      voiceMove: "Geldige zet! Je speelde {word} voor {score} punten.",
      tilesRecalled: "Letters teruggelegd op je plankje.",
      newGameStarted: "Nieuw spel gestart. Leg letters over de centrale ster.",
      voiceNewGame: "Nieuw spel gestart. Het is jouw beurt.",
      remoteTurn1: "{player} speelde {word} op het centrum voor {score} punten!",
      remoteTurn2: "{player} speelde {word} voor {score} punten!",
      remoteDone: "Gesimuleerde zet is al voltooid. Start een nieuw spel om te resetten."
    }
  },
  de: {
    name: "Deutsch",
    flag: "🇩🇪",
    speechLocale: "de-DE",
    dictFile: "dict_de.txt",
    remotePlayer: "Sabine (Smartphone)",
    letterValues: {
      A: 1, B: 3, C: 4, D: 1, E: 1, F: 4, G: 2, H: 2, I: 1, J: 6, K: 4, L: 2, M: 3,
      N: 1, O: 2, P: 4, Q: 10, R: 1, S: 1, T: 1, U: 1, V: 6, W: 3, X: 8, Y: 10, Z: 3,
      Ä: 6, Ö: 8, Ü: 6
    },
    tileBag: "AAAAABBCDDDDEEEEEEEEEEEEEEEFFGGGHHHHIIIIIIJKKLLLMMMMNNNNNNNNNOOOPQRRRRRRSSSSSSSTTTTTTUUUUUUVWWXYZÄÖÜ",
    turn1Rack: ["S", "P", "I", "E", "L", "E", "N"],
    remoteSim: {
      turn1: { word: "HAUS", r: 7, c: 7, isHorizontal: true, score: 14 },
      turn2: { branchChar: "H", branchR: 7, branchC: 7, word: "HUND", r: 8, c: 7, isHorizontal: false, score: 12 }
    },
    strings: {
      ready: "Bereit ({count} Wörter geladen). Buchstaben auf den Stern (H8) legen.",
      loading: "Lade deutsches Wörterbuch ({file})...",
      centerError: "Der erste Zug muss den Stern in der Mitte (H8) bedecken.",
      lineError: "Alle Buchstaben müssen in einer Reihe oder Spalte liegen.",
      gapError: "Es gibt eine Lücke in deinem Wort.",
      connectError: "Dein Wort muss an liegende Buchstaben anknüpfen.",
      minLenError: "Ein Wort muss mindestens 2 Buchstaben haben.",
      notInDict: "„{word}“ steht nicht im Wörterbuch.",
      validMove: "Gültiger Zug! Du hast {word} für {score} Punkte gelegt.",
      voiceMove: "Gültiger Zug! Du hast {word} für {score} Punkte gelegt.",
      tilesRecalled: "Buchstaben zurück auf die Bank gelegt.",
      newGameStarted: "Neues Spiel gestartet. Lege Buchstaben über den Stern.",
      voiceNewGame: "Neues Spiel gestartet. Du bist am Zug.",
      remoteTurn1: "{player} hat {word} in der Mitte für {score} Punkte gelegt!",
      remoteTurn2: "{player} hat {word} für {score} Punkte gelegt!",
      remoteDone: "Simulierter Zug bereits abgeschlossen. Starte ein neues Spiel."
    }
  },
  es: {
    name: "Español",
    flag: "🇪🇸",
    speechLocale: "es-ES",
    dictFile: "dict_es.txt",
    remotePlayer: "Sara (Móvil)",
    letterValues: {
      A: 1, B: 3, C: 3, D: 2, E: 1, F: 4, G: 2, H: 4, I: 1, J: 8, K: 8, L: 1, M: 3,
      N: 1, Ñ: 8, O: 1, P: 3, Q: 5, R: 1, S: 1, T: 1, U: 1, V: 4, W: 8, X: 8, Y: 4, Z: 10
    },
    tileBag: "AAAAAAAAAAAABBCCCCDDDDDEEEEEEEEEEEEFGGHHIIIIIIJLLLLMMNNNNNÑOOOOOOOOOPPQRRRRRSSSSSTTTTUUUUUVXYZ",
    turn1Rack: ["A", "M", "I", "G", "O", "S", "A"],
    remoteSim: {
      turn1: { word: "HOLA", r: 7, c: 7, isHorizontal: true, score: 14 },
      turn2: { branchChar: "H", branchR: 7, branchC: 7, word: "HORA", r: 8, c: 7, isHorizontal: false, score: 12 }
    },
    strings: {
      ready: "Listo ({count} palabras cargadas). Coloca fichas cubriendo la estrella central (H8).",
      loading: "Cargando diccionario en español ({file})...",
      centerError: "La primera palabra debe cubrir la estrella central (H8).",
      lineError: "Todas las fichas deben estar en una sola fila o columna.",
      gapError: "Hay un espacio vacío dentro de tu palabra.",
      connectError: "Tu palabra debe conectarse con las fichas del tablero.",
      minLenError: "La palabra debe tener al menos 2 letras.",
      notInDict: "«{word}» no está en el diccionario.",
      validMove: "¡Jugada válida! Has colocado {word} por {score} puntos.",
      voiceMove: "¡Jugada válida! Has colocado {word} por {score} puntos.",
      tilesRecalled: "Fichas devueltas al atril.",
      newGameStarted: "Nueva partida iniciada. Coloca fichas en la estrella central.",
      voiceNewGame: "Nueva partida iniciada. Es tu turno.",
      remoteTurn1: "¡{player} colocó {word} en el centro por {score} puntos!",
      remoteTurn2: "¡{player} colocó {word} por {score} puntos!",
      remoteDone: "Jugada remota ya realizada. Inicia una nueva partida para reiniciar."
    }
  }
};

// Global Game State
let currentLangKey = "en";
let currentLang = LANGUAGES.en;
const DICTIONARY_CACHE = {};
let currentDictionary = new Set();

let tileBag = [];
let boardState = Array.from({ length: BOARD_SIZE }, () => Array(BOARD_SIZE).fill(null));
let currentPlacements = [];
let playerRack = [];
let selectedRackIndex = null;
let p1Score = 0;
let p2Score = 0;
let voiceEnabled = true;

// DOM Elements
const boardEl = document.getElementById("board");
const rackEl = document.getElementById("tile-rack");
const statusEl = document.getElementById("console-status");
const wordsEl = document.getElementById("detail-words");
const pointsEl = document.getElementById("detail-points");
const bonusEl = document.getElementById("detail-bonus");
const dictCountEl = document.getElementById("detail-dict-count");
const player1ScoreEl = document.getElementById("player-1-score");
const player2ScoreEl = document.getElementById("player-2-score");
const player2NameEl = document.getElementById("player-2-name");
const selectLangEl = document.getElementById("select-language");

// Audio Speech Announcement with language auto-detection
function speak(text) {
  if (!voiceEnabled || !window.speechSynthesis) return;
  window.speechSynthesis.cancel();

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = currentLang.speechLocale;
  utterance.rate = 0.92;
  utterance.pitch = 1.0;

  const voices = window.speechSynthesis.getVoices();
  const prefix = currentLang.speechLocale.split("-")[0];
  const matchedVoice = voices.find(v => v.lang && v.lang.startsWith(prefix));
  if (matchedVoice) {
    utterance.voice = matchedVoice;
  }

  window.speechSynthesis.speak(utterance);
}

function formatString(template, vars) {
  return template.replace(/\{(\w+)\}/g, (_, key) => vars[key] !== undefined ? vars[key] : "");
}

async function loadLanguageDictionary(langKey) {
  const langConfig = LANGUAGES[langKey];
  if (!langConfig) return;

  if (DICTIONARY_CACHE[langKey]) {
    currentDictionary = DICTIONARY_CACHE[langKey];
    updateDictionaryUI(currentDictionary.size);
    return;
  }

  statusEl.className = "status-msg info";
  statusEl.innerText = formatString(langConfig.strings.loading, { file: langConfig.dictFile });
  if (dictCountEl) dictCountEl.innerText = "Loading...";

  try {
    const res = await fetch(langConfig.dictFile);
    if (!res.ok) throw new Error("HTTP " + res.status);
    const text = await res.text();
    const wordsSet = new Set();
    const lines = text.split(/\r?\n/);
    for (let i = 0; i < lines.length; i++) {
      const w = lines[i].trim();
      if (w.length >= 2 && w.length <= 15) {
        wordsSet.add(w);
      }
    }
    DICTIONARY_CACHE[langKey] = wordsSet;
    if (currentLangKey === langKey) {
      currentDictionary = wordsSet;
      updateDictionaryUI(wordsSet.size);
    }
  } catch (err) {
    console.warn("Failed to load " + langConfig.dictFile + ":", err);
    const fallbackSet = new Set(["HELLO", "CAT", "DOG", "BONJOUR", "MAISON", "HALLO", "HUIS", "SPIEL", "HAUS", "HOLA", "CASA"]);
    DICTIONARY_CACHE[langKey] = fallbackSet;
    if (currentLangKey === langKey) {
      currentDictionary = fallbackSet;
      updateDictionaryUI(fallbackSet.size);
    }
  }
}

function updateDictionaryUI(count) {
  const formattedCount = count.toLocaleString();
  if (dictCountEl) {
    dictCountEl.innerText = formattedCount + " words (" + currentLang.flag + " " + currentLang.name + ")";
  }
  const isBoardEmpty = boardState.every(row => row.every(cell => cell === null));
  if (isBoardEmpty && currentPlacements.length === 0) {
    statusEl.className = "status-msg info";
    statusEl.innerText = formatString(currentLang.strings.ready, { count: formattedCount });
  }
}

function initBag() {
  tileBag = [];
  const chars = Array.from(currentLang.tileBag);
  tileBag = [...chars];
  shuffle(tileBag);
}

function shuffle(array) {
  for (let i = array.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    const tmp = array[i];
    array[i] = array[j];
    array[j] = tmp;
  }
}

function drawTiles(count) {
  const drawn = [];
  for (let i = 0; i < count && tileBag.length > 0; i++) {
    drawn.push(tileBag.pop());
  }
  return drawn;
}

function buildBoardDOM() {
  boardEl.innerHTML = "";
  for (let r = 0; r < BOARD_SIZE; r++) {
    for (let c = 0; c < BOARD_SIZE; c++) {
      const cell = document.createElement("div");
      cell.className = "cell";
      cell.dataset.row = r;
      cell.dataset.col = c;

      const bonus = BONUS_GRID[r][c];
      if (r === 7 && c === 7) {
        cell.classList.add("center");
        cell.innerText = "★";
      } else if (bonus === 4) {
        cell.classList.add("tws");
        cell.innerText = "3W";
      } else if (bonus === 3) {
        cell.classList.add("dws");
        cell.innerText = "2W";
      } else if (bonus === 2) {
        cell.classList.add("tls");
        cell.innerText = "3L";
      } else if (bonus === 1) {
        cell.classList.add("dls");
        cell.innerText = "2L";
      }

      cell.addEventListener("click", () => handleCellClick(r, c));
      boardEl.appendChild(cell);
    }
  }
}

function renderRack() {
  rackEl.innerHTML = "";
  playerRack.forEach((letter, index) => {
    if (letter === null) return;
    const tile = document.createElement("div");
    tile.className = "tile";
    if (selectedRackIndex === index) tile.classList.add("selected");

    const letSpan = document.createElement("span");
    letSpan.className = "tile-letter";
    letSpan.innerText = letter;

    const ptSpan = document.createElement("span");
    ptSpan.className = "tile-pts";
    ptSpan.innerText = currentLang.letterValues[letter] || 0;

    tile.appendChild(letSpan);
    tile.appendChild(ptSpan);

    tile.addEventListener("click", () => {
      selectedRackIndex = (selectedRackIndex === index) ? null : index;
      renderRack();
    });

    rackEl.appendChild(tile);
  });
}

function handleCellClick(r, c) {
  const existingPlacementIdx = currentPlacements.findIndex(p => p.row === r && p.col === c);
  if (existingPlacementIdx !== -1) {
    const p = currentPlacements[existingPlacementIdx];
    playerRack[p.rackIndex] = p.letter;
    currentPlacements.splice(existingPlacementIdx, 1);
    updateBoardView();
    renderRack();
    return;
  }

  if (boardState[r][c] !== null) return;

  if (selectedRackIndex !== null && playerRack[selectedRackIndex] !== null) {
    const letter = playerRack[selectedRackIndex];
    playerRack[selectedRackIndex] = null;
    currentPlacements.push({ row: r, col: c, letter, rackIndex: selectedRackIndex });
    selectedRackIndex = null;
    updateBoardView();
    renderRack();
  }
}

function updateBoardView() {
  const cells = boardEl.querySelectorAll(".cell");
  cells.forEach(cell => {
    const r = parseInt(cell.dataset.row);
    const c = parseInt(cell.dataset.col);

    const existingTile = cell.querySelector(".tile");
    if (existingTile) existingTile.remove();

    const committedLetter = boardState[r][c];
    const pendingPlacement = currentPlacements.find(p => p.row === r && p.col === c);
    const letter = pendingPlacement ? pendingPlacement.letter : committedLetter;

    if (letter) {
      const tile = document.createElement("div");
      tile.className = "tile";
      if (pendingPlacement) tile.classList.add("just-placed");

      const letSpan = document.createElement("span");
      letSpan.className = "tile-letter";
      letSpan.innerText = letter;

      const ptSpan = document.createElement("span");
      ptSpan.className = "tile-pts";
      ptSpan.innerText = currentLang.letterValues[letter] || 0;

      tile.appendChild(letSpan);
      tile.appendChild(ptSpan);
      cell.appendChild(tile);
    }
  });
}

function validateMove() {
  if (currentPlacements.length === 0) {
    return { ok: false, msg: currentLang.strings.minLenError };
  }

  const isBoardEmpty = boardState.every(row => row.every(cell => cell === null));

  if (isBoardEmpty) {
    const coversCenter = currentPlacements.some(p => p.row === 7 && p.col === 7);
    if (!coversCenter) {
      return { ok: false, msg: currentLang.strings.centerError };
    }
  }

  const sameRow = currentPlacements.every(p => p.row === currentPlacements[0].row);
  const sameCol = currentPlacements.every(p => p.col === currentPlacements[0].col);
  if (!sameRow && !sameCol) {
    return { ok: false, msg: currentLang.strings.lineError };
  }

  const tempGrid = boardState.map(r => [...r]);
  currentPlacements.forEach(p => {
    tempGrid[p.row][p.col] = p.letter;
  });

  if (sameRow) {
    const r = currentPlacements[0].row;
    const cols = currentPlacements.map(p => p.col);
    const minCol = Math.min(...cols);
    const maxCol = Math.max(...cols);
    for (let c = minCol; c <= maxCol; c++) {
      if (!tempGrid[r][c]) {
        return { ok: false, msg: currentLang.strings.gapError };
      }
    }
  } else {
    const c = currentPlacements[0].col;
    const rows = currentPlacements.map(p => p.row);
    const minRow = Math.min(...rows);
    const maxRow = Math.max(...rows);
    for (let r = minRow; r <= maxRow; r++) {
      if (!tempGrid[r][c]) {
        return { ok: false, msg: currentLang.strings.gapError };
      }
    }
  }

  if (!isBoardEmpty) {
    const connected = currentPlacements.some(p => {
      const neighbors = [
        [p.row - 1, p.col], [p.row + 1, p.col],
        [p.row, p.col - 1], [p.row, p.col + 1]
      ];
      return neighbors.some(([nr, nc]) => nr >= 0 && nr < BOARD_SIZE && nc >= 0 && nc < BOARD_SIZE && boardState[nr][nc] !== null);
    });
    if (!connected) {
      return { ok: false, msg: currentLang.strings.connectError };
    }
  }

  const newPlacementsSet = new Set(currentPlacements.map(p => p.row + "," + p.col));
  const wordsFormed = [];
  let totalScore = 0;

  let mainWord = "";
  let mainPts = 0;
  let mainMult = 1;

  if (sameRow) {
    const r = currentPlacements[0].row;
    let minC = Math.min(...currentPlacements.map(p => p.col));
    let maxC = Math.max(...currentPlacements.map(p => p.col));
    while (minC > 0 && tempGrid[r][minC - 1]) minC--;
    while (maxC < BOARD_SIZE - 1 && tempGrid[r][maxC + 1]) maxC++;

    if (maxC > minC) {
      for (let c = minC; c <= maxC; c++) {
        const letChar = tempGrid[r][c];
        mainWord += letChar;
        let val = currentLang.letterValues[letChar] || 0;
        if (newPlacementsSet.has(r + "," + c)) {
          const b = BONUS_GRID[r][c];
          if (b === 1) val *= 2;
          else if (b === 2) val *= 3;
          else if (b === 3) mainMult *= 2;
          else if (b === 4) mainMult *= 3;
        }
        mainPts += val;
      }
      wordsFormed.push({ word: mainWord, score: mainPts * mainMult });
    }
  } else {
    const c = currentPlacements[0].col;
    let minR = Math.min(...currentPlacements.map(p => p.row));
    let maxR = Math.max(...currentPlacements.map(p => p.row));
    while (minR > 0 && tempGrid[minR - 1][c]) minR--;
    while (maxR < BOARD_SIZE - 1 && tempGrid[maxR + 1][c]) maxR++;

    if (maxR > minR) {
      for (let r = minR; r <= maxR; r++) {
        const letChar = tempGrid[r][c];
        mainWord += letChar;
        let val = currentLang.letterValues[letChar] || 0;
        if (newPlacementsSet.has(r + "," + c)) {
          const b = BONUS_GRID[r][c];
          if (b === 1) val *= 2;
          else if (b === 2) val *= 3;
          else if (b === 3) mainMult *= 2;
          else if (b === 4) mainMult *= 3;
        }
        mainPts += val;
      }
      wordsFormed.push({ word: mainWord, score: mainPts * mainMult });
    }
  }

  currentPlacements.forEach(p => {
    let crossWord = "";
    let crossPts = 0;
    let crossMult = 1;

    if (sameRow) {
      let minR = p.row;
      let maxR = p.row;
      while (minR > 0 && tempGrid[minR - 1][p.col]) minR--;
      while (maxR < BOARD_SIZE - 1 && tempGrid[maxR + 1][p.col]) maxR++;

      if (maxR > minR) {
        for (let r = minR; r <= maxR; r++) {
          const letChar = tempGrid[r][p.col];
          crossWord += letChar;
          let val = currentLang.letterValues[letChar] || 0;
          if (r === p.row) {
            const b = BONUS_GRID[r][p.col];
            if (b === 1) val *= 2;
            else if (b === 2) val *= 3;
            else if (b === 3) crossMult *= 2;
            else if (b === 4) crossMult *= 3;
          }
          crossPts += val;
        }
        wordsFormed.push({ word: crossWord, score: crossPts * crossMult });
      }
    } else {
      let minC = p.col;
      let maxC = p.col;
      while (minC > 0 && tempGrid[p.row][minC - 1]) minC--;
      while (maxC < BOARD_SIZE - 1 && tempGrid[p.row][maxC + 1]) maxC++;

      if (maxC > minC) {
        for (let c = minC; c <= maxC; c++) {
          const letChar = tempGrid[p.row][c];
          crossWord += letChar;
          let val = currentLang.letterValues[letChar] || 0;
          if (c === p.col) {
            const b = BONUS_GRID[p.row][c];
            if (b === 1) val *= 2;
            else if (b === 2) val *= 3;
            else if (b === 3) crossMult *= 2;
            else if (b === 4) crossMult *= 3;
          }
          crossPts += val;
        }
        wordsFormed.push({ word: crossWord, score: crossPts * crossMult });
      }
    }
  });

  if (wordsFormed.length === 0) {
    return { ok: false, msg: currentLang.strings.minLenError };
  }

  for (const wf of wordsFormed) {
    if (!currentDictionary.has(wf.word)) {
      return { ok: false, msg: formatString(currentLang.strings.notInDict, { word: wf.word }) };
    }
    totalScore += wf.score;
  }

  const isBingo = currentPlacements.length === 7;
  if (isBingo) totalScore += 50;

  return {
    ok: true,
    words: wordsFormed,
    totalScore,
    isBingo
  };
}

document.getElementById("btn-submit").addEventListener("click", () => {
  const result = validateMove();

  if (!result.ok) {
    statusEl.className = "status-msg error";
    statusEl.innerText = result.msg;
    speak(result.msg);
    return;
  }

  currentPlacements.forEach(p => {
    boardState[p.row][p.col] = p.letter;
  });

  p1Score += result.totalScore;
  player1ScoreEl.innerText = p1Score;

  const wordsStr = result.words.map(w => w.word + " (" + w.score + " pts)").join(", ");
  wordsEl.innerText = wordsStr;
  pointsEl.innerText = result.totalScore + " pts";
  bonusEl.innerText = result.isBingo ? "+50 Bingo Bonus!" : "Standard";

  const successMsg = formatString(currentLang.strings.validMove, {
    word: result.words[0].word,
    score: result.totalScore
  });
  statusEl.className = "status-msg success";
  statusEl.innerText = successMsg;

  const announceText = formatString(currentLang.strings.voiceMove, {
    word: result.words[0].word,
    score: result.totalScore
  });
  speak(announceText);

  const emptySlots = playerRack.filter(l => l === null).length;
  const newTiles = drawTiles(emptySlots);
  let newIdx = 0;
  for (let i = 0; i < playerRack.length; i++) {
    if (playerRack[i] === null) {
      playerRack[i] = newTiles[newIdx++] || null;
    }
  }

  currentPlacements = [];
  renderRack();
  updateBoardView();
});

document.getElementById("btn-recall").addEventListener("click", () => {
  currentPlacements.forEach(p => {
    playerRack[p.rackIndex] = p.letter;
  });
  currentPlacements = [];
  selectedRackIndex = null;
  renderRack();
  updateBoardView();
  statusEl.className = "status-msg info";
  statusEl.innerText = currentLang.strings.tilesRecalled;
});

document.getElementById("btn-shuffle").addEventListener("click", () => {
  const nonNull = playerRack.filter(l => l !== null);
  shuffle(nonNull);
  let idx = 0;
  for (let i = 0; i < playerRack.length; i++) {
    if (playerRack[i] !== null) {
      playerRack[i] = nonNull[idx++];
    }
  }
  renderRack();
});

document.getElementById("btn-audio-toggle").addEventListener("click", (e) => {
  voiceEnabled = !voiceEnabled;
  e.target.innerText = voiceEnabled ? "🔊 Voice: On" : "🔇 Voice: Off";
});

document.getElementById("btn-simulate-remote").addEventListener("click", () => {
  const isBoardEmpty = boardState.every(row => row.every(cell => cell === null));
  const sim = currentLang.remoteSim;

  if (isBoardEmpty) {
    const t1 = sim.turn1;
    for (let i = 0; i < t1.word.length; i++) {
      if (t1.isHorizontal) {
        boardState[t1.r][t1.c + i] = t1.word[i];
      } else {
        boardState[t1.r + i][t1.c] = t1.word[i];
      }
    }
    p2Score += t1.score;
    player2ScoreEl.innerText = p2Score;
    updateBoardView();
    const msg = formatString(currentLang.strings.remoteTurn1, {
      player: currentLang.remotePlayer.split(" ")[0],
      word: t1.word,
      score: t1.score
    });
    statusEl.className = "status-msg info";
    statusEl.innerText = msg;
    speak(msg);
  } else {
    const t2 = sim.turn2;
    if (boardState[t2.branchR][t2.branchC] === t2.branchChar && boardState[t2.r][t2.c] === null) {
      for (let i = 0; i < t2.word.length - 1; i++) {
        if (t2.isHorizontal) {
          boardState[t2.r][t2.c + i] = t2.word[i + 1];
        } else {
          boardState[t2.r + i][t2.c] = t2.word[i + 1];
        }
      }
      p2Score += t2.score;
      player2ScoreEl.innerText = p2Score;
      updateBoardView();
      const msg = formatString(currentLang.strings.remoteTurn2, {
        player: currentLang.remotePlayer.split(" ")[0],
        word: t2.word,
        score: t2.score
      });
      statusEl.className = "status-msg info";
      statusEl.innerText = msg;
      speak(msg);
    } else {
      alert(currentLang.strings.remoteDone);
    }
  }
});

function resetGame() {
  initBag();
  boardState = Array.from({ length: BOARD_SIZE }, () => Array(BOARD_SIZE).fill(null));
  currentPlacements = [];
  selectedRackIndex = null;
  p1Score = 0;
  p2Score = 0;
  player1ScoreEl.innerText = "0";
  player2ScoreEl.innerText = "0";
  wordsEl.innerText = "-";
  pointsEl.innerText = "0";
  bonusEl.innerText = "None";

  playerRack = [...currentLang.turn1Rack];

  statusEl.className = "status-msg info";
  statusEl.innerText = currentLang.strings.newGameStarted;

  buildBoardDOM();
  renderRack();
  updateBoardView();
  speak(currentLang.strings.voiceNewGame);
}

document.getElementById("btn-new-game").addEventListener("click", () => {
  resetGame();
});

selectLangEl.addEventListener("change", (e) => {
  const newLang = e.target.value;
  if (LANGUAGES[newLang]) {
    currentLangKey = newLang;
    currentLang = LANGUAGES[newLang];
    player2NameEl.innerText = currentLang.remotePlayer;
    loadLanguageDictionary(newLang);
    resetGame();
  }
});

(async function init() {
  buildBoardDOM();
  resetGame();
  await loadLanguageDictionary("en");
})();

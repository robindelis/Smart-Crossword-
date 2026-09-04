// Smart Crossword Board - Web Prototype & Engine Controller

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

const LETTER_VALUES = {
  A: 1, B: 3, C: 3, D: 2, E: 1, F: 4, G: 2, H: 4, I: 1, J: 8, K: 5, L: 1, M: 3,
  N: 1, O: 1, P: 3, Q: 10, R: 1, S: 1, T: 1, U: 1, V: 4, W: 4, X: 8, Y: 4, Z: 10
};

// Builtin dictionary
const DICTIONARY = new Set([
  "AA", "AB", "AD", "AE", "AG", "AH", "AI", "AL", "AM", "AN", "AR", "AS", "AT", "AW", "AX", "AY",
  "BA", "BE", "BI", "BO", "BY", "CAT", "CLOUD", "DO", "DOG", "ED", "EF", "EH", "EL", "EM", "EN",
  "ER", "ES", "ET", "EX", "FA", "FE", "GO", "HA", "HE", "HELLO", "HI", "HM", "HO", "HONEY", "ID",
  "IF", "IN", "IS", "IT", "JO", "KA", "KI", "LA", "LI", "LO", "MA", "ME", "MI", "MM", "MO", "MU",
  "MY", "NA", "NE", "NO", "NU", "OD", "OE", "OF", "OH", "OI", "OK", "OM", "ON", "OP", "OR", "OS",
  "OW", "OX", "OY", "PA", "PE", "PEACH", "PI", "PLAY", "PO", "QI", "RE", "SH", "SI", "SO", "TA",
  "TI", "TO", "UH", "UM", "UN", "UP", "US", "UT", "WE", "WO", "XI", "XU", "YA", "YE", "YO", "ZA",
  "BREEZE", "GARDEN", "HOME", "LOVE", "QUIET", "QUARTZ", "SMART", "BOARD", "GAME", "WORD", "WORDS",
  "FAMILY", "GRANDMA", "GRANDPA", "TOUCH", "TILES", "RACK", "SCORE", "DOUBLE", "TRIPLE", "LETTER"
]);

// Full English Scrabble tile distribution (100 tiles)
const TILE_BAG_DISTRIBUTION = "AAAAAAAAABBCCDDDDEEEEEEEEEEEEFFGGGHHIIIIIIIIIJKLLLLMMNNNNNNOOOOOOOOPPQRRRRRRSSSSTTTTTTUUUUVVWWXYYZ";

// Game State
let tileBag = [];
let boardState = Array.from({ length: BOARD_SIZE }, () => Array(BOARD_SIZE).fill(null));
let currentPlacements = []; // { row, col, letter, rackIndex }
let playerRack = [];
let selectedRackIndex = null;
let p1Score = 0;
let p2Score = 0;
let voiceEnabled = true;

// Initialize Bag
function initBag() {
  tileBag = TILE_BAG_DISTRIBUTION.split("");
  shuffle(tileBag);
}

function shuffle(array) {
  for (let i = array.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]];
  }
}

function drawTiles(count) {
  const drawn = [];
  for (let i = 0; i < count && tileBag.length > 0; i++) {
    drawn.push(tileBag.pop());
  }
  return drawn;
}

// Speak announcements
function speak(text) {
  if (!voiceEnabled || !window.speechSynthesis) return;
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate = 0.95; // Slightly calmer pace for seniors
  utterance.pitch = 1.0;
  window.speechSynthesis.speak(utterance);
}

// Render Board DOM
const boardEl = document.getElementById("board");

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

// Render Rack DOM
const rackEl = document.getElementById("tile-rack");

function renderRack() {
  rackEl.innerHTML = "";
  playerRack.forEach((letter, index) => {
    if (letter === null) return; // Placed on board
    const tile = document.createElement("div");
    tile.className = "tile";
    if (selectedRackIndex === index) tile.classList.add("selected");

    const letSpan = document.createElement("span");
    letSpan.className = "tile-letter";
    letSpan.innerText = letter;

    const ptSpan = document.createElement("span");
    ptSpan.className = "tile-pts";
    ptSpan.innerText = LETTER_VALUES[letter] || 0;

    tile.appendChild(letSpan);
    tile.appendChild(ptSpan);

    tile.addEventListener("click", () => {
      if (selectedRackIndex === index) {
        selectedRackIndex = null;
      } else {
        selectedRackIndex = index;
      }
      renderRack();
    });

    rackEl.appendChild(tile);
  });
}

// Handle Board Cell Clicks
function handleCellClick(r, c) {
  // Check if cell has an uncommitted placement -> return to rack
  const existingPlacementIdx = currentPlacements.findIndex(p => p.row === r && p.col === c);
  if (existingPlacementIdx !== -1) {
    const p = currentPlacements[existingPlacementIdx];
    playerRack[p.rackIndex] = p.letter;
    currentPlacements.splice(existingPlacementIdx, 1);
    updateBoardView();
    renderRack();
    return;
  }

  // If already locked on board, do nothing
  if (boardState[r][c] !== null) return;

  // Place selected rack tile onto cell
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

    // Clear tile if previously rendered
    const existingTile = cell.querySelector(".tile");
    if (existingTile) existingTile.remove();

    // Check committed board
    const committedLetter = boardState[r][c];
    // Check pending placement
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
      ptSpan.innerText = LETTER_VALUES[letter] || 0;

      tile.appendChild(letSpan);
      tile.appendChild(ptSpan);
      cell.appendChild(tile);
    }
  });
}

// Move Validation & Scoring (Matches crossword_engine.c logic)
function validateMove() {
  if (currentPlacements.length === 0) {
    return { ok: false, msg: "No tiles placed on the board." };
  }

  const isBoardEmpty = boardState.every(row => row.every(cell => cell === null));

  // 1. Center Star Check
  if (isBoardEmpty) {
    const coversCenter = currentPlacements.some(p => p.row === 7 && p.col === 7);
    if (!coversCenter) {
      return { ok: false, msg: "First move must cover the center star (H8)." };
    }
  }

  // 2. Collinear Check
  const sameRow = currentPlacements.every(p => p.row === currentPlacements[0].row);
  const sameCol = currentPlacements.every(p => p.col === currentPlacements[0].col);
  if (!sameRow && !sameCol) {
    return { ok: false, msg: "All tiles must be in a single row or column." };
  }

  // Working grid
  const tempGrid = boardState.map(r => [...r]);
  currentPlacements.forEach(p => {
    tempGrid[p.row][p.col] = p.letter;
  });

  // 3. Continuity Check
  if (sameRow) {
    const r = currentPlacements[0].row;
    const cols = currentPlacements.map(p => p.col);
    const minCol = Math.min(...cols);
    const maxCol = Math.max(...cols);
    for (let c = minCol; c <= maxCol; c++) {
      if (!tempGrid[r][c]) {
        return { ok: false, msg: "There is an empty space inside your word." };
      }
    }
  } else {
    const c = currentPlacements[0].col;
    const rows = currentPlacements.map(p => p.row);
    const minRow = Math.min(...rows);
    const maxRow = Math.max(...rows);
    for (let r = minRow; r <= maxRow; r++) {
      if (!tempGrid[r][c]) {
        return { ok: false, msg: "There is an empty space inside your word." };
      }
    }
  }

  // 4. Connectivity Check (if not first turn)
  if (!isBoardEmpty) {
    const connected = currentPlacements.some(p => {
      const neighbors = [
        [p.row - 1, p.col], [p.row + 1, p.col],
        [p.row, p.col - 1], [p.row, p.col + 1]
      ];
      return neighbors.some(([nr, nc]) => nr >= 0 && nr < BOARD_SIZE && nc >= 0 && nc < BOARD_SIZE && boardState[nr][nc] !== null);
    });
    if (!connected) {
      return { ok: false, msg: "Your word must connect to tiles already on the board." };
    }
  }

  // 5. Extract words and calculate points
  const newPlacementsSet = new Set(currentPlacements.map(p => `${p.row},${p.col}`));
  const wordsFormed = [];
  let totalScore = 0;

  // Main word
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
        let val = LETTER_VALUES[letChar] || 0;
        if (newPlacementsSet.has(`${r},${c}`)) {
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
        let val = LETTER_VALUES[letChar] || 0;
        if (newPlacementsSet.has(`${r},${c}`)) {
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

  // Cross-words
  currentPlacements.forEach(p => {
    let crossWord = "";
    let crossPts = 0;
    let crossMult = 1;

    if (sameRow) {
      // Check vertical cross-word
      let minR = p.row;
      let maxR = p.row;
      while (minR > 0 && tempGrid[minR - 1][p.col]) minR--;
      while (maxR < BOARD_SIZE - 1 && tempGrid[maxR + 1][p.col]) maxR++;

      if (maxR > minR) {
        for (let r = minR; r <= maxR; r++) {
          const letChar = tempGrid[r][p.col];
          crossWord += letChar;
          let val = LETTER_VALUES[letChar] || 0;
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
      // Check horizontal cross-word
      let minC = p.col;
      let maxC = p.col;
      while (minC > 0 && tempGrid[p.row][minC - 1]) minC--;
      while (maxC < BOARD_SIZE - 1 && tempGrid[p.row][maxC + 1]) maxC++;

      if (maxC > minC) {
        for (let c = minC; c <= maxC; c++) {
          const letChar = tempGrid[p.row][c];
          crossWord += letChar;
          let val = LETTER_VALUES[letChar] || 0;
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
    return { ok: false, msg: "Word must be at least 2 letters." };
  }

  // Dictionary validation
  for (const wf of wordsFormed) {
    if (!DICTIONARY.has(wf.word)) {
      return { ok: false, msg: `'${wf.word}' is not in the dictionary.` };
    }
    totalScore += wf.score;
  }

  // Bingo bonus
  const isBingo = currentPlacements.length === 7;
  if (isBingo) totalScore += 50;

  return {
    ok: true,
    words: wordsFormed,
    totalScore,
    isBingo
  };
}

// Button Listeners
document.getElementById("btn-submit").addEventListener("click", () => {
  const result = validateMove();
  const statusEl = document.getElementById("console-status");
  const wordsEl = document.getElementById("detail-words");
  const pointsEl = document.getElementById("detail-points");
  const bonusEl = document.getElementById("detail-bonus");

  if (!result.ok) {
    statusEl.className = "status-msg error";
    statusEl.innerText = result.msg;
    speak(result.msg);
    return;
  }

  // Valid move: Commit to board
  currentPlacements.forEach(p => {
    boardState[p.row][p.col] = p.letter;
  });

  p1Score += result.totalScore;
  document.getElementById("player-1-score").innerText = p1Score;

  const wordsStr = result.words.map(w => `${w.word} (${w.score} pts)`).join(", ");
  wordsEl.innerText = wordsStr;
  pointsEl.innerText = `${result.totalScore} pts`;
  bonusEl.innerText = result.isBingo ? "+50 Bingo Bonus!" : "Standard";

  statusEl.className = "status-msg success";
  statusEl.innerText = `Valid move! Scored ${result.totalScore} points.`;

  const announceText = `Valid move! You played ${result.words[0].word} for ${result.totalScore} points.`;
  speak(announceText);

  // Refill rack
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
  document.getElementById("console-status").className = "status-msg info";
  document.getElementById("console-status").innerText = "Tiles recalled to rack.";
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

// Simulate turn played remotely from phone (Sarah)
document.getElementById("btn-simulate-remote").addEventListener("click", () => {
  const isBoardEmpty = boardState.every(row => row.every(cell => cell === null));
  if (isBoardEmpty) {
    // Play "HELLO" across center (7,7)
    const word = "HELLO";
    for (let i = 0; i < word.length; i++) {
      boardState[7][7 + i] = word[i];
    }
    p2Score += 18;
    document.getElementById("player-2-score").innerText = p2Score;
    updateBoardView();
    const msg = "Sarah played HELLO on center for 18 points!";
    document.getElementById("console-status").className = "status-msg info";
    document.getElementById("console-status").innerText = msg;
    speak(msg);
  } else {
    // Branch "HONEY" vertically off the 'H' at (7,7)
    if (boardState[7][7] === 'H' && boardState[8][7] === null) {
      boardState[8][7] = 'O';
      boardState[9][7] = 'N';
      boardState[10][7] = 'E';
      boardState[11][7] = 'Y';
      p2Score += 15;
      document.getElementById("player-2-score").innerText = p2Score;
      updateBoardView();
      const msg = "Sarah played HONEY for 15 points!";
      document.getElementById("console-status").className = "status-msg info";
      document.getElementById("console-status").innerText = msg;
      speak(msg);
    } else {
      alert("Simulated move already completed. Start a new game to reset.");
    }
  }
});

// New Game
document.getElementById("btn-new-game").addEventListener("click", () => {
  initBag();
  boardState = Array.from({ length: BOARD_SIZE }, () => Array(BOARD_SIZE).fill(null));
  currentPlacements = [];
  selectedRackIndex = null;
  p1Score = 0;
  p2Score = 0;
  document.getElementById("player-1-score").innerText = "0";
  document.getElementById("player-2-score").innerText = "0";
  document.getElementById("detail-words").innerText = "-";
  document.getElementById("detail-points").innerText = "0";
  document.getElementById("detail-bonus").innerText = "None";

  // Deal 7 tiles
  playerRack = drawTiles(7);
  // Ensure we have letters that make "HELLO" or "CAT" or "DOG" on turn 1
  if (!playerRack.includes('H')) playerRack[0] = 'H';
  if (!playerRack.includes('E')) playerRack[1] = 'E';
  if (!playerRack.includes('L')) playerRack[2] = 'L';
  if (!playerRack.includes('L')) playerRack[3] = 'L';
  if (!playerRack.includes('O')) playerRack[4] = 'O';

  document.getElementById("console-status").className = "status-msg info";
  document.getElementById("console-status").innerText = "New game started. Place tiles covering center star (H8).";

  buildBoardDOM();
  renderRack();
  updateBoardView();
  speak("New game started. It's your turn.");
});

// Initial boot
initBag();
playerRack = drawTiles(7);
// Seed with good letters for first turn
playerRack[0] = 'H';
playerRack[1] = 'E';
playerRack[2] = 'L';
playerRack[3] = 'L';
playerRack[4] = 'O';

buildBoardDOM();
renderRack();
updateBoardView();

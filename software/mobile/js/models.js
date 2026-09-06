// Smart Crossword Board - Mobile Companion Data Models
// Clean, isomorphic models for Game, Board, Move, Player, Tile, and Cheer

const BOARD_SIZE = 15;

// Bonus Types
const BONUS_NONE = 0;
const BONUS_DLS = 1; // Double Letter Score
const BONUS_TLS = 2; // Triple Letter Score
const BONUS_DWS = 3; // Double Word Score
const BONUS_TWS = 4; // Triple Word Score

// Standard 15x15 Scrabble Bonus Grid
const BONUS_GRID = [
  [4, 0, 0, 1, 0, 0, 0, 4, 0, 0, 0, 1, 0, 0, 4],
  [0, 3, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 3, 0],
  [0, 0, 3, 0, 0, 0, 1, 0, 1, 0, 0, 0, 3, 0, 0],
  [1, 0, 0, 3, 0, 0, 0, 1, 0, 0, 0, 3, 0, 0, 1],
  [0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0],
  [0, 2, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 2, 0],
  [0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0],
  [4, 0, 0, 1, 0, 0, 0, 3, 0, 0, 0, 1, 0, 0, 4], // (7,7) Center Star is DWS
  [0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0],
  [0, 2, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 2, 0],
  [0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0],
  [1, 0, 0, 3, 0, 0, 0, 1, 0, 0, 0, 3, 0, 0, 1],
  [0, 0, 3, 0, 0, 0, 1, 0, 1, 0, 0, 0, 3, 0, 0],
  [0, 3, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 3, 0],
  [4, 0, 0, 1, 0, 0, 0, 4, 0, 0, 0, 1, 0, 0, 4]
];

// Language configurations with official Scrabble letter points and distributions
const LANG_CONFIGS = {
  en: {
    code: "en",
    name: "English",
    flag: "🇬🇧",
    dictFile: "/dict_en.txt",
    speechLocale: "en-US",
    defaultBoardPlayer: "Grandma Betty",
    defaultMobilePlayer: "Sarah (You)",
    letterValues: {
      A: 1, B: 3, C: 3, D: 2, E: 1, F: 4, G: 2, H: 4, I: 1, J: 8, K: 5, L: 1, M: 3,
      N: 1, O: 1, P: 3, Q: 10, R: 1, S: 1, T: 1, U: 1, V: 4, W: 4, X: 8, Y: 4, Z: 10
    },
    tileBag: "AAAAAAAAABBCCDDDDEEEEEEEEEEEEFFGGGHHIIIIIIIIIJKLLLLMMNNNNNNOOOOOOOOPPQRRRRRRSSSSTTTTTTUUUUVVWWXYYZ"
  },
  fr: {
    code: "fr",
    name: "Français",
    flag: "🇫🇷",
    dictFile: "/dict_fr.txt",
    speechLocale: "fr-FR",
    defaultBoardPlayer: "Mamie Denise",
    defaultMobilePlayer: "Sophie (Vous)",
    letterValues: {
      A: 1, B: 3, C: 3, D: 2, E: 1, F: 4, G: 2, H: 4, I: 1, J: 8, K: 10, L: 1, M: 2,
      N: 1, O: 1, P: 3, Q: 8, R: 1, S: 1, T: 1, U: 1, V: 4, W: 10, X: 10, Y: 10, Z: 10
    },
    tileBag: "AAAAAAAAABBCDDEEEEEEEEEEEEEEEFFGGHHIIIIIIIIJKLLLLLMMMNNNNNNOOOOOOPPQRRRRRRSSSSSSTTTTTTUUUUUUVVWXYZ"
  },
  nl: {
    code: "nl",
    name: "Nederlands",
    flag: "🇳🇱",
    dictFile: "/dict_nl.txt",
    speechLocale: "nl-NL",
    defaultBoardPlayer: "Oma Fenna",
    defaultMobilePlayer: "Sanne (Jij)",
    letterValues: {
      A: 1, B: 3, C: 5, D: 2, E: 1, F: 4, G: 3, H: 4, I: 1, J: 4, K: 3, L: 3, M: 3,
      N: 1, O: 1, P: 3, Q: 10, R: 2, S: 2, T: 2, U: 4, V: 4, W: 5, X: 8, Y: 8, Z: 4
    },
    tileBag: "AAAAAABBCCDDDDDEEEEEEEEEEEEEEEEEEFFGGGHHIIIIJJKKKLLLMMMNNNNNNNNNNOOOOOOPPQRRRRRSSSSSTTTTTUUUVVWWXYZZ"
  },
  de: {
    code: "de",
    name: "Deutsch",
    flag: "🇩🇪",
    dictFile: "/dict_de.txt",
    speechLocale: "de-DE",
    defaultBoardPlayer: "Oma Katja",
    defaultMobilePlayer: "Sabine (Du)",
    letterValues: {
      A: 1, B: 3, C: 4, D: 1, E: 1, F: 4, G: 2, H: 2, I: 1, J: 6, K: 4, L: 2, M: 3,
      N: 1, O: 2, P: 4, Q: 10, R: 1, S: 1, T: 1, U: 1, V: 6, W: 3, X: 8, Y: 10, Z: 3,
      Ä: 6, Ö: 8, Ü: 6
    },
    tileBag: "AAAAABBCDDDDEEEEEEEEEEEEEEEFFGGGHHHHIIIIIIJKKLLLMMMMNNNNNNNNNOOOPQRRRRRRSSSSSSSTTTTTTUUUUUUVWWXYZÄÖÜ"
  },
  es: {
    code: "es",
    name: "Español",
    flag: "🇪🇸",
    dictFile: "/dict_es.txt",
    speechLocale: "es-ES",
    defaultBoardPlayer: "Abuela Elvira",
    defaultMobilePlayer: "Sara (Tú)",
    letterValues: {
      A: 1, B: 3, C: 3, D: 2, E: 1, F: 4, G: 2, H: 4, I: 1, J: 8, K: 8, L: 1, M: 3,
      N: 1, Ñ: 8, O: 1, P: 3, Q: 5, R: 1, S: 1, T: 1, U: 1, V: 4, W: 8, X: 8, Y: 4, Z: 10
    },
    tileBag: "AAAAAAAAAAAABBCCCCDDDDDEEEEEEEEEEEEFGGHHIIIIIIJLLLLMMNNNNNÑOOOOOOOOOPPQRRRRRSSSSSTTTTUUUUUVXYZ"
  }
};

class Tile {
  constructor({ letter = 'A', value = 1, isBlank = false, assignedLetter = null, id = null } = {}) {
    this.letter = letter.toUpperCase();
    this.value = value;
    this.isBlank = isBlank;
    this.assignedLetter = assignedLetter ? assignedLetter.toUpperCase() : null;
    this.id = id || `tile_${Math.random().toString(36).substring(2, 9)}`;
  }

  get effectiveLetter() {
    return this.isBlank ? (this.assignedLetter || '?') : this.letter;
  }

  toJSON() {
    return {
      letter: this.letter,
      value: this.value,
      isBlank: this.isBlank,
      assignedLetter: this.assignedLetter,
      id: this.id
    };
  }

  static fromJSON(data) {
    if (!data) return null;
    return new Tile(data);
  }
}

class Player {
  constructor({ id = null, name = 'Player', avatar = '👤', score = 0, isRemote = false, rack = [] } = {}) {
    this.id = id || `p_${Math.random().toString(36).substring(2, 8)}`;
    this.name = name;
    this.avatar = avatar;
    this.score = score;
    this.isRemote = isRemote;
    // Array of 7 Tile items (or nulls)
    this.rack = rack.map(t => (t instanceof Tile || t === null) ? t : Tile.fromJSON(t));
    while (this.rack.length < 7) {
      this.rack.push(null);
    }
  }

  toJSON() {
    return {
      id: this.id,
      name: this.name,
      avatar: this.avatar,
      score: this.score,
      isRemote: this.isRemote,
      rack: this.rack.map(t => t ? t.toJSON() : null)
    };
  }

  static fromJSON(data) {
    if (!data) return null;
    return new Player(data);
  }
}

class Board {
  constructor(grid = null) {
    if (grid && Array.isArray(grid)) {
      this.grid = grid.map(row => [...row]);
    } else {
      this.grid = Array.from({ length: BOARD_SIZE }, () => Array(BOARD_SIZE).fill(null));
    }
  }

  getCell(r, c) {
    if (r < 0 || r >= BOARD_SIZE || c < 0 || c >= BOARD_SIZE) return null;
    return this.grid[r][c];
  }

  setCell(r, c, letter) {
    if (r >= 0 && r < BOARD_SIZE && c >= 0 && c < BOARD_SIZE) {
      this.grid[r][c] = letter ? letter.toUpperCase() : null;
    }
  }

  getBonus(r, c) {
    if (r < 0 || r >= BOARD_SIZE || c < 0 || c >= BOARD_SIZE) return BONUS_NONE;
    return BONUS_GRID[r][c];
  }

  isEmpty() {
    for (let r = 0; r < BOARD_SIZE; r++) {
      for (let c = 0; c < BOARD_SIZE; c++) {
        if (this.grid[r][c] !== null) return false;
      }
    }
    return true;
  }

  clone() {
    return new Board(this.grid);
  }

  toMatrix() {
    return this.grid.map(row => [...row]);
  }

  toJSON() {
    return this.grid;
  }

  static fromJSON(data) {
    return new Board(data);
  }
}

class Move {
  constructor({
    id = null,
    gameId = '',
    playerId = '',
    playerName = '',
    placements = [],
    words = [],
    totalScore = 0,
    isBingo = false,
    timestamp = Date.now(),
    isRemote = false,
    boardSynced = true
  } = {}) {
    this.id = id || `mv_${Date.now()}_${Math.random().toString(36).substring(2, 6)}`;
    this.gameId = gameId;
    this.playerId = playerId;
    this.playerName = playerName;
    this.placements = placements; // [{ row, col, letter, isBlank, assignedLetter }]
    this.words = words;           // [{ word, score }]
    this.totalScore = totalScore;
    this.isBingo = isBingo;
    this.timestamp = timestamp;
    this.isRemote = isRemote;
    this.boardSynced = boardSynced;
  }

  toJSON() {
    return {
      id: this.id,
      gameId: this.gameId,
      playerId: this.playerId,
      playerName: this.playerName,
      placements: this.placements,
      words: this.words,
      totalScore: this.totalScore,
      isBingo: this.isBingo,
      timestamp: this.timestamp,
      isRemote: this.isRemote,
      boardSynced: this.boardSynced
    };
  }

  static fromJSON(data) {
    if (!data) return null;
    return new Move(data);
  }
}

class Cheer {
  constructor({
    id = null,
    gameId = '',
    senderId = '',
    senderName = '',
    text = '',
    audioData = null,
    audioDuration = 0,
    timestamp = Date.now()
  } = {}) {
    this.id = id || `chr_${Date.now()}_${Math.random().toString(36).substring(2, 6)}`;
    this.gameId = gameId;
    this.senderId = senderId;
    this.senderName = senderName;
    this.text = text;
    this.audioData = audioData; // base64 or URL
    this.audioDuration = audioDuration;
    this.timestamp = timestamp;
  }

  toJSON() {
    return {
      id: this.id,
      gameId: this.gameId,
      senderId: this.senderId,
      senderName: this.senderName,
      text: this.text,
      audioData: this.audioData,
      audioDuration: this.audioDuration,
      timestamp: this.timestamp
    };
  }

  static fromJSON(data) {
    if (!data) return null;
    return new Cheer(data);
  }
}

class Game {
  constructor({
    id = null,
    boardId = 'SCB-8492',
    mode = 'casual', // 'casual' | 'strict'
    lang = 'en',
    players = [],
    currentTurnPlayerId = null,
    board = null,
    tileBag = null,
    moveHistory = [],
    cheerHistory = [],
    pendingSyncMove = null,
    status = 'active', // 'active' | 'completed'
    createdAt = Date.now(),
    updatedAt = Date.now()
  } = {}) {
    this.id = id || `game_${boardId}_${Date.now()}`;
    this.boardId = boardId.toUpperCase();
    this.mode = mode;
    this.lang = lang;
    this.board = board instanceof Board ? board : (board ? Board.fromJSON(board) : new Board());
    this.players = players.map(p => p instanceof Player ? p : Player.fromJSON(p));
    this.currentTurnPlayerId = currentTurnPlayerId || (this.players[0] ? this.players[0].id : null);

    const langConf = LANG_CONFIGS[this.lang] || LANG_CONFIGS.en;
    if (tileBag && Array.isArray(tileBag)) {
      this.tileBag = [...tileBag];
    } else {
      this.tileBag = Array.from(langConf.tileBag);
      this.shuffleTileBag();
    }

    this.moveHistory = moveHistory.map(m => m instanceof Move ? m : Move.fromJSON(m));
    this.cheerHistory = cheerHistory.map(c => c instanceof Cheer ? c : Cheer.fromJSON(c));
    this.pendingSyncMove = pendingSyncMove ? (pendingSyncMove instanceof Move ? pendingSyncMove : Move.fromJSON(pendingSyncMove)) : null;
    this.status = status;
    this.createdAt = createdAt;
    this.updatedAt = updatedAt;
  }

  shuffleTileBag() {
    for (let i = this.tileBag.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      const tmp = this.tileBag[i];
      this.tileBag[i] = this.tileBag[j];
      this.tileBag[j] = tmp;
    }
  }

  drawTile() {
    if (this.tileBag.length === 0) return null;
    const letter = this.tileBag.pop();
    const langConf = LANG_CONFIGS[this.lang] || LANG_CONFIGS.en;
    const val = langConf.letterValues[letter] || 1;
    return new Tile({ letter, value: val });
  }

  fillRack(player) {
    for (let i = 0; i < player.rack.length; i++) {
      if (player.rack[i] === null) {
        player.rack[i] = this.drawTile();
      }
    }
  }

  getPlayer(id) {
    return this.players.find(p => p.id === id) || null;
  }

  getOpponent(myId) {
    return this.players.find(p => p.id !== myId) || null;
  }

  toJSON() {
    return {
      id: this.id,
      boardId: this.boardId,
      mode: this.mode,
      lang: this.lang,
      board: this.board.toJSON(),
      players: this.players.map(p => p.toJSON()),
      currentTurnPlayerId: this.currentTurnPlayerId,
      tileBag: this.tileBag,
      moveHistory: this.moveHistory.map(m => m.toJSON()),
      cheerHistory: this.cheerHistory.map(c => c.toJSON()),
      pendingSyncMove: this.pendingSyncMove ? this.pendingSyncMove.toJSON() : null,
      status: this.status,
      createdAt: this.createdAt,
      updatedAt: this.updatedAt
    };
  }

  static fromJSON(data) {
    if (!data) return null;
    return new Game(data);
  }
}

// Global exposure for browser scripts
if (typeof window !== 'undefined') {
  window.BOARD_SIZE = BOARD_SIZE;
  window.BONUS_GRID = BONUS_GRID;
  window.LANG_CONFIGS = LANG_CONFIGS;
  window.Tile = Tile;
  window.Player = Player;
  window.Board = Board;
  window.Move = Move;
  window.Cheer = Cheer;
  window.Game = Game;
}

// Export for Node / CJS testing
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    BOARD_SIZE,
    BONUS_GRID,
    LANG_CONFIGS,
    Tile,
    Player,
    Board,
    Move,
    Cheer,
    Game
  };
}

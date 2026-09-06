// Smart Crossword Board - Firebase Sync & Local Mock Service
// Modular cloud synchronization layer with full LocalStorage mock fallback
// enables 100% full gameplay testing immediately without external credentials.

class FirebaseSyncService {
  constructor(firebaseConfig = null) {
    this.config = firebaseConfig;
    this.isRealFirebase = false;
    this.currentUser = null;
    this.listeners = new Map(); // gameId -> Set of callback functions
    this.boardListeners = new Map(); // boardId -> Set of callback functions

    this.init();
  }

  init() {
    // Check if real Firebase SDK is available in window
    if (this.config && typeof window !== 'undefined' && window.firebase && window.firebase.initializeApp) {
      try {
        if (!window.firebase.apps.length) {
          window.firebase.initializeApp(this.config);
        }
        this.auth = window.firebase.auth();
        this.firestore = window.firebase.firestore();
        this.storage = window.firebase.storage();
        this.isRealFirebase = true;
        console.log('[FirebaseService] Connected to real Firebase cloud project');
      } catch (err) {
        console.warn('[FirebaseService] Firebase init failed, falling back to Local Mock:', err);
        this.isRealFirebase = false;
      }
    }

    if (!this.isRealFirebase) {
      this.initLocalMock();
    }
  }

  // --- LOCAL MOCK BACKEND IMPLEMENTATION ---
  initLocalMock() {
    console.log('[FirebaseService] Active mode: Transparent Local Mock Backend');

    // Load or create current user profile
    const savedUser = localStorage.getItem('crossword_companion_user');
    if (savedUser) {
      try {
        this.currentUser = JSON.parse(savedUser);
      } catch (_) {
        this.currentUser = this.createDefaultUser();
      }
    } else {
      this.currentUser = this.createDefaultUser();
      localStorage.setItem('crossword_companion_user', JSON.stringify(this.currentUser));
    }

    // Seed paired boards if not already set
    if (!localStorage.getItem('crossword_companion_boards')) {
      const defaultBoards = [
        {
          id: 'SCB-8492',
          name: "Grandma Betty's Board",
          status: 'online',
          lastSeen: Date.now() - 1000 * 60 * 2,
          location: 'Living Room'
        },
        {
          id: 'SCB-3011',
          name: "Dad's Board",
          status: 'idle',
          lastSeen: Date.now() - 1000 * 60 * 120,
          location: 'Study'
        }
      ];
      localStorage.setItem('crossword_companion_boards', JSON.stringify(defaultBoards));
    }

    // Seed an initial demo game if none exist
    if (!localStorage.getItem('crossword_companion_games')) {
      this.seedDefaultDemoGame();
    }

    // Cross-tab synchronization via storage event
    if (typeof window !== 'undefined') {
      window.addEventListener('storage', (e) => {
        if (e.key === 'crossword_companion_games') {
          this.notifyAllGameListeners();
        }
      });
    }
  }

  createDefaultUser() {
    return {
      uid: 'user_mobile_sarah',
      displayName: 'Sarah (Granddaughter)',
      email: 'sarah.family@example.com',
      avatar: '👩‍🦰',
      isAnonymous: false
    };
  }

  seedDefaultDemoGame() {
    const lang = 'en';
    const langConf = LANG_CONFIGS[lang];

    const p1 = new Player({
      id: this.currentUser.uid,
      name: 'Sarah',
      avatar: '👩‍🦰',
      score: 18,
      isRemote: false
    });

    const p2 = new Player({
      id: 'board_grandma',
      name: 'Grandma Betty',
      avatar: '👵',
      score: 15,
      isRemote: true
    });

    const game = new Game({
      id: 'game_SCB-8492_demo',
      boardId: 'SCB-8492',
      mode: 'casual',
      lang: lang,
      players: [p1, p2],
      currentTurnPlayerId: p1.id
    });

    // Populate Grandma and Sarah rack
    p1.rack = [
      new Tile({ letter: 'C', value: 3 }),
      new Tile({ letter: 'L', value: 1 }),
      new Tile({ letter: 'O', value: 1 }),
      new Tile({ letter: 'U', value: 1 }),
      new Tile({ letter: 'D', value: 2 }),
      new Tile({ letter: 'S', value: 1 }),
      new Tile({ letter: 'T', value: 1 })
    ];

    p2.rack = [
      new Tile({ letter: 'P', value: 3 }),
      new Tile({ letter: 'E', value: 1 }),
      new Tile({ letter: 'A', value: 1 }),
      new Tile({ letter: 'C', value: 3 }),
      new Tile({ letter: 'H', value: 4 }),
      new Tile({ letter: 'E', value: 1 }),
      new Tile({ letter: 'S', value: 1 })
    ];

    // Place opening move: "HELLO" across center (7,7)
    // H(4) + E(1) + L(1) + L(1) + O(1*2 DLS at 7,11) = 9 * 2 (center DWS) = 18 pts
    game.board.setCell(7, 7, 'H');
    game.board.setCell(7, 8, 'E');
    game.board.setCell(7, 9, 'L');
    game.board.setCell(7, 10, 'L');
    game.board.setCell(7, 11, 'O');

    // Move 1
    const m1 = new Move({
      id: 'mv_demo_1',
      gameId: game.id,
      playerId: p1.id,
      playerName: p1.name,
      placements: [
        { row: 7, col: 7, letter: 'H' },
        { row: 7, col: 8, letter: 'E' },
        { row: 7, col: 9, letter: 'L' },
        { row: 7, col: 10, letter: 'L' },
        { row: 7, col: 11, letter: 'O' }
      ],
      words: [{ word: 'HELLO', score: 18 }],
      totalScore: 18,
      timestamp: Date.now() - 1000 * 60 * 30,
      boardSynced: true
    });
    game.moveHistory.push(m1);

    // Place Move 2 from Grandma: "HONEY" vertically branching off H at (7,7)
    // O(1), N(1), E(1), Y(4) down cols (8,7), (9,7), (10,7), (11,7)
    game.board.setCell(8, 7, 'O');
    game.board.setCell(9, 7, 'N');
    game.board.setCell(10, 7, 'E');
    game.board.setCell(11, 7, 'Y');

    const m2 = new Move({
      id: 'mv_demo_2',
      gameId: game.id,
      playerId: p2.id,
      playerName: p2.name,
      placements: [
        { row: 8, col: 7, letter: 'O' },
        { row: 9, col: 7, letter: 'N' },
        { row: 10, col: 7, letter: 'E' },
        { row: 11, col: 7, letter: 'Y' }
      ],
      words: [{ word: 'HONEY', score: 15 }],
      totalScore: 15,
      timestamp: Date.now() - 1000 * 60 * 15,
      isRemote: true,
      boardSynced: true
    });
    game.moveHistory.push(m2);

    // Add a warm initial cheer from Grandma
    const c1 = new Cheer({
      id: 'chr_demo_1',
      gameId: game.id,
      senderId: p2.id,
      senderName: p2.name,
      text: "Good morning sweetheart! I played HONEY on the wooden board. Love you! ❤️",
      timestamp: Date.now() - 1000 * 60 * 14
    });
    game.cheerHistory.push(c1);

    const games = [game.toJSON()];
    localStorage.setItem('crossword_companion_games', JSON.stringify(games));
  }

  // --- PUBLIC API METHODS ---

  async getCurrentUser() {
    return this.currentUser;
  }

  async signInWithGoogle() {
    if (this.isRealFirebase) {
      const provider = new window.firebase.auth.GoogleAuthProvider();
      const result = await this.auth.signInWithPopup(provider);
      this.currentUser = {
        uid: result.user.uid,
        displayName: result.user.displayName,
        email: result.user.email,
        avatar: '👩‍🦰',
        isAnonymous: false
      };
      return this.currentUser;
    }

    // Local Mock Sign-In toggle
    this.currentUser = {
      uid: 'user_google_sarah',
      displayName: 'Sarah Miller',
      email: 'sarah.miller@gmail.com',
      avatar: '🌟',
      isAnonymous: false
    };
    localStorage.setItem('crossword_companion_user', JSON.stringify(this.currentUser));
    return this.currentUser;
  }

  async signOut() {
    if (this.isRealFirebase) {
      await this.auth.signOut();
    }
    this.currentUser = this.createDefaultUser();
    localStorage.setItem('crossword_companion_user', JSON.stringify(this.currentUser));
    return this.currentUser;
  }

  async getPairedBoards() {
    try {
      const raw = localStorage.getItem('crossword_companion_boards');
      return raw ? JSON.parse(raw) : [];
    } catch (_) {
      return [];
    }
  }

  async pairBoard(boardId, name = null) {
    const formattedId = boardId.trim().toUpperCase();
    const boards = await this.getPairedBoards();
    let existing = boards.find(b => b.id === formattedId);

    if (existing) {
      existing.status = 'online';
      existing.lastSeen = Date.now();
      if (name) existing.name = name;
    } else {
      existing = {
        id: formattedId,
        name: name || `Board ${formattedId}`,
        status: 'online',
        lastSeen: Date.now(),
        location: 'Paired Physical Board'
      };
      boards.push(existing);
    }

    localStorage.setItem('crossword_companion_boards', JSON.stringify(boards));
    return existing;
  }

  async listActiveGames() {
    try {
      const raw = localStorage.getItem('crossword_companion_games');
      const list = raw ? JSON.parse(raw) : [];
      return list.map(g => Game.fromJSON(g));
    } catch (_) {
      return [];
    }
  }

  async getGame(gameId) {
    const games = await this.listActiveGames();
    return games.find(g => g.id === gameId) || null;
  }

  async createGame({
    boardId = 'SCB-8492',
    mode = 'casual',
    lang = 'en',
    opponentName = 'Grandma Betty'
  }) {
    const langConf = LANG_CONFIGS[lang] || LANG_CONFIGS.en;

    const p1 = new Player({
      id: this.currentUser.uid,
      name: this.currentUser.displayName.split(' ')[0],
      avatar: this.currentUser.avatar || '👩‍🦰',
      score: 0,
      isRemote: false
    });

    const p2 = new Player({
      id: `board_${boardId}`,
      name: opponentName || langConf.defaultBoardPlayer,
      avatar: '👵',
      score: 0,
      isRemote: true
    });

    const game = new Game({
      boardId: boardId.toUpperCase(),
      mode: mode,
      lang: lang,
      players: [p1, p2],
      currentTurnPlayerId: p1.id
    });

    // Fill initial tile racks
    game.fillRack(p1);
    game.fillRack(p2);

    const games = await this.listActiveGames();
    games.unshift(game);
    this.saveGames(games);

    this.notifyGameListeners(game);
    return game;
  }

  async submitMove(gameId, moveData) {
    const games = await this.listActiveGames();
    const gameIndex = games.findIndex(g => g.id === gameId);
    if (gameIndex === -1) {
      throw new Error("Game not found: " + gameId);
    }

    const game = games[gameIndex];

    // Apply placements to board
    for (const p of moveData.placements) {
      game.board.setCell(p.row, p.col, p.letter);
    }

    // Update player score
    const player = game.getPlayer(moveData.playerId);
    if (player) {
      player.score += moveData.totalScore;
    }

    // Record move
    const move = new Move({
      gameId: game.id,
      playerId: moveData.playerId,
      playerName: moveData.playerName,
      placements: moveData.placements,
      words: moveData.words,
      totalScore: moveData.totalScore,
      isBingo: moveData.isBingo,
      timestamp: Date.now(),
      boardSynced: false // Pending RFID sync confirmation on board
    });
    game.moveHistory.push(move);
    game.pendingSyncMove = move;

    // Switch turn to opponent
    const opponent = game.getOpponent(moveData.playerId);
    if (opponent) {
      game.currentTurnPlayerId = opponent.id;
    }

    game.updatedAt = Date.now();
    games[gameIndex] = game;
    this.saveGames(games);

    this.notifyGameListeners(game);
    return game;
  }

  async sendCheer(gameId, cheerData) {
    const games = await this.listActiveGames();
    const game = games.find(g => g.id === gameId);
    if (!game) return null;

    const cheer = new Cheer({
      gameId: gameId,
      senderId: cheerData.senderId || this.currentUser.uid,
      senderName: cheerData.senderName || this.currentUser.displayName,
      text: cheerData.text || '',
      audioData: cheerData.audioData || null,
      audioDuration: cheerData.audioDuration || 0,
      timestamp: Date.now()
    });

    game.cheerHistory.push(cheer);
    game.updatedAt = Date.now();
    this.saveGames(games);

    this.notifyGameListeners(game);
    return cheer;
  }

  async confirmBoardRfidSync(gameId) {
    const games = await this.listActiveGames();
    const game = games.find(g => g.id === gameId);
    if (!game) return null;

    if (game.pendingSyncMove) {
      game.pendingSyncMove.boardSynced = true;
      const lastMove = game.moveHistory[game.moveHistory.length - 1];
      if (lastMove) lastMove.boardSynced = true;
      game.pendingSyncMove = null;
    }

    game.updatedAt = Date.now();
    this.saveGames(games);
    this.notifyGameListeners(game);
    return game;
  }

  // Simulate an async turn from Grandma Betty on the physical board
  async simulateBoardMove(gameId) {
    const games = await this.listActiveGames();
    const game = games.find(g => g.id === gameId);
    if (!game) return null;

    const boardPlayer = game.players.find(p => p.isRemote);
    if (!boardPlayer) return null;

    // Realistic moves that connect cleanly to the board
    // Check if "GARDEN" can branch or "CAT" or "PLAY"
    const samplePlays = [
      {
        word: "CLOUD",
        placements: [
          { row: 7, col: 11, letter: "O" }, // existing O from HELLO
          { row: 6, col: 11, letter: "L" },
          { row: 5, col: 11, letter: "C" },
          { row: 8, col: 11, letter: "U" },
          { row: 9, col: 11, letter: "D" }
        ],
        newPlacements: [
          { row: 5, col: 11, letter: "C" },
          { row: 6, col: 11, letter: "L" },
          { row: 8, col: 11, letter: "U" },
          { row: 9, col: 11, letter: "D" }
        ],
        score: 16
      },
      {
        word: "GARDEN",
        placements: [
          { row: 11, col: 7, letter: "Y" }, // existing Y from HONEY
          { row: 11, col: 8, letter: "E" },
          { row: 11, col: 9, letter: "S" }
        ],
        newPlacements: [
          { row: 11, col: 8, letter: "E" },
          { row: 11, col: 9, letter: "S" }
        ],
        score: 12
      },
      {
        word: "PLAY",
        placements: [
          { row: 8, col: 7, letter: "O" },
          { row: 8, col: 8, letter: "U" },
          { row: 8, col: 9, letter: "R" }
        ],
        newPlacements: [
          { row: 8, col: 8, letter: "U" },
          { row: 8, col: 9, letter: "R" }
        ],
        score: 10
      }
    ];

    // Pick an available play
    let chosenPlay = null;
    for (const sp of samplePlays) {
      const canPlace = sp.newPlacements.every(np => game.board.getCell(np.row, np.col) === null);
      if (canPlace) {
        chosenPlay = sp;
        break;
      }
    }

    if (!chosenPlay) {
      // Fallback simple placement near center
      chosenPlay = {
        word: "GO",
        newPlacements: [
          { row: 7, col: 12, letter: "G" },
          { row: 7, col: 13, letter: "O" }
        ],
        score: 8
      };
    }

    // Apply placements
    for (const p of chosenPlay.newPlacements) {
      game.board.setCell(p.row, p.col, p.letter);
    }

    boardPlayer.score += chosenPlay.score;

    const move = new Move({
      gameId: game.id,
      playerId: boardPlayer.id,
      playerName: boardPlayer.name,
      placements: chosenPlay.newPlacements,
      words: [{ word: chosenPlay.word, score: chosenPlay.score }],
      totalScore: chosenPlay.score,
      timestamp: Date.now(),
      isRemote: true,
      boardSynced: true
    });
    game.moveHistory.push(move);

    // Switch turn back to mobile player
    const mobilePlayer = game.players.find(p => !p.isRemote);
    if (mobilePlayer) {
      game.currentTurnPlayerId = mobilePlayer.id;
    }

    // Send a cheer from Grandma
    const cheerTexts = [
      `I placed ${chosenPlay.word} on the board! Your turn sweetheart! 👵❤️`,
      `Nice move earlier! I played ${chosenPlay.word} for ${chosenPlay.score} points! 🎉`,
      `Tea time and Scrabble! Placed ${chosenPlay.word}. Take your time! ☕`
    ];
    const cheer = new Cheer({
      gameId: game.id,
      senderId: boardPlayer.id,
      senderName: boardPlayer.name,
      text: cheerTexts[Math.floor(Math.random() * cheerTexts.length)],
      timestamp: Date.now() + 100
    });
    game.cheerHistory.push(cheer);

    game.updatedAt = Date.now();
    this.saveGames(games);

    this.notifyGameListeners(game);
    return game;
  }

  // --- SUBSCRIPTIONS & EVENT NOTIFICATIONS ---

  listenToGame(gameId, callback) {
    if (!this.listeners.has(gameId)) {
      this.listeners.set(gameId, new Set());
    }
    this.listeners.get(gameId).add(callback);

    // Send initial snapshot
    this.getGame(gameId).then(game => {
      if (game) callback(game);
    });

    // Return unsubscribe function
    return () => {
      if (this.listeners.has(gameId)) {
        this.listeners.get(gameId).delete(callback);
      }
    };
  }

  notifyGameListeners(game) {
    if (this.listeners.has(game.id)) {
      this.listeners.get(game.id).forEach(cb => {
        try { cb(game); } catch (e) { console.error(e); }
      });
    }
  }

  async notifyAllGameListeners() {
    const games = await this.listActiveGames();
    for (const game of games) {
      this.notifyGameListeners(game);
    }
  }

  saveGames(games) {
    localStorage.setItem('crossword_companion_games', JSON.stringify(games.map(g => g.toJSON())));
  }
}

if (typeof window !== 'undefined') {
  window.FirebaseSyncService = FirebaseSyncService;
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { FirebaseSyncService };
}

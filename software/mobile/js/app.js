// Smart Crossword Board - Main Application Controller
// Wires board viewport, tactile digital rack, referee engine, cloud sync,
// voice notes, and sound effects.

class CrosswordApp {
  constructor() {
    this.currentGame = null;
    this.currentView = 'lobby';
    this.unsubscribeGameListener = null;

    this.pendingPlacements = []; // [{ row, col, letter, rackIndex, tileId }]
    this.selectedRackIndex = null;
    this.soundEnabled = true;
    this.selectedExchangeIndices = new Set();
    this.lastAnnouncementAudio = null;

    // Services
    this.firebaseService = new FirebaseSyncService();
    this.engine = new GameEngineBridge();
    this.audioRecorder = null;
    this.viewport = null;

    // DOM Elements
    this.dom = {};
  }

  async init() {
    console.log('[App] Initializing Crossword Companion PWA...');
    this.cacheDomElements();
    this.initAudioContext();
    this.initAudioRecorder();
    this.initViewport();
    this.bindEvents();
    this.registerServiceWorker();

    // Show initial Lobby view
    await this.showLobbyView();
    console.log('[App] Ready for play.');
  }

  cacheDomElements() {
    this.dom = {
      appRoot: document.getElementById('app-root'),
      navBrandBtn: document.getElementById('nav-brand-btn'),
      btnToggleSound: document.getElementById('btn-toggle-sound'),
      soundIcon: document.getElementById('sound-icon'),
      btnNavLobby: document.getElementById('btn-nav-lobby'),
      navLobbyText: document.getElementById('nav-lobby-text'),
      btnUserProfile: document.getElementById('btn-user-profile'),
      userAvatar: document.getElementById('user-avatar'),
      userDisplayName: document.getElementById('user-display-name'),

      // Views
      viewLobby: document.getElementById('view-lobby'),
      viewGame: document.getElementById('view-game'),

      // Lobby elements
      activeGamesList: document.getElementById('active-games-list'),
      badgeActiveCount: document.getElementById('badge-active-count'),
      pairedBoardsList: document.getElementById('paired-boards-list'),
      inputBoardId: document.getElementById('input-board-id'),
      inputOpponentName: document.getElementById('input-opponent-name'),
      selectGameLang: document.getElementById('select-game-lang'),
      optModeCasual: document.getElementById('opt-mode-casual'),
      optModeStrict: document.getElementById('opt-mode-strict'),
      btnCreateGame: document.getElementById('btn-create-game'),

      // Game elements
      hudBoardInfo: document.getElementById('hud-board-info'),
      hudModePill: document.getElementById('hud-mode-pill'),
      scoreCardMobile: document.getElementById('score-card-mobile'),
      hudPlayerAvatar: document.getElementById('hud-player-avatar'),
      hudPlayerName: document.getElementById('hud-player-name'),
      hudPlayerScore: document.getElementById('hud-player-score'),
      scoreCardBoard: document.getElementById('score-card-board'),
      hudBoardAvatar: document.getElementById('hud-board-avatar'),
      hudBoardName: document.getElementById('hud-board-name'),
      hudBoardScore: document.getElementById('hud-board-score'),
      hudBagCount: document.getElementById('hud-bag-count'),

      refereeBanner: document.getElementById('referee-banner'),
      refereeText: document.getElementById('referee-text'),
      refereeBadge: document.getElementById('referee-badge'),

      syncBanner: document.getElementById('sync-banner'),
      syncStatusText: document.getElementById('sync-status-text'),
      btnSimBoardMove: document.getElementById('btn-sim-board-move'),

      boardViewport: document.getElementById('board-viewport'),
      boardTransformContainer: document.getElementById('board-transform-container'),
      boardGrid: document.getElementById('board-grid'),
      btnZoomIn: document.getElementById('btn-zoom-in'),
      btnZoomOut: document.getElementById('btn-zoom-out'),
      btnFitScreen: document.getElementById('btn-fit-screen'),
      zoomIndicator: document.getElementById('zoom-indicator'),

      cheerBubblePreview: document.getElementById('cheer-bubble-preview'),
      cheerPreviewText: document.getElementById('cheer-preview-text'),
      rackTray: document.getElementById('rack-tray'),
      btnRackShuffle: document.getElementById('btn-rack-shuffle'),
      btnRackRecall: document.getElementById('btn-rack-recall'),
      btnRackExchange: document.getElementById('btn-rack-exchange'),
      btnRackCheer: document.getElementById('btn-rack-cheer'),
      btnRackSubmit: document.getElementById('btn-rack-submit'),

      // Modals
      modalVoice: document.getElementById('modal-voice'),
      btnCloseVoiceModal: document.getElementById('btn-close-voice-modal'),
      btnRecordMic: document.getElementById('btn-record-mic'),
      recordTimer: document.getElementById('record-timer'),
      voicePreviewContainer: document.getElementById('voice-preview-container'),
      btnPlayPreview: document.getElementById('btn-play-preview'),
      btnResetRecording: document.getElementById('btn-reset-recording'),
      inputCheerText: document.getElementById('input-cheer-text'),
      btnSendCheer: document.getElementById('btn-send-cheer'),

      modalExchange: document.getElementById('modal-exchange'),
      btnCloseExchangeModal: document.getElementById('btn-close-exchange-modal'),
      exchangeTilesGrid: document.getElementById('exchange-tiles-grid'),
      btnConfirmExchange: document.getElementById('btn-confirm-exchange'),

      toastContainer: document.getElementById('toast-container')
    };
  }

  initViewport() {
    this.viewport = new BoardViewport({
      viewportEl: this.dom.boardViewport,
      boardContainerEl: this.dom.boardTransformContainer,
      boardGridEl: this.dom.boardGrid,
      onCellTapped: (r, c) => this.handleCellTapped(r, c),
      onZoomChanged: (scale) => {
        this.dom.zoomIndicator.innerText = `${Math.round(scale * 100)}%`;
      }
    });

    // Initial fit
    setTimeout(() => this.viewport.fitToScreen(false), 80);
  }

  initAudioRecorder() {
    this.audioRecorder = new AudioRecorder({
      maxDurationSec: 10,
      onStateChange: (state) => {
        if (state === 'recording') {
          this.dom.btnRecordMic.classList.add('recording');
          this.dom.btnRecordMic.innerText = '⏹';
          this.dom.voicePreviewContainer.classList.add('hidden');
        } else if (state === 'recorded') {
          this.dom.btnRecordMic.classList.remove('recording');
          this.dom.btnRecordMic.innerText = '🎤';
          this.dom.recordTimer.innerText = 'Audio Ready to Send!';
          this.dom.voicePreviewContainer.classList.remove('hidden');
        } else if (state === 'playing') {
          this.dom.btnPlayPreview.innerText = '⏸ Pause Preview';
        } else {
          this.dom.btnRecordMic.classList.remove('recording');
          this.dom.btnRecordMic.innerText = '🎤';
          this.dom.recordTimer.innerText = 'Tap to Record (Max 10s)';
          this.dom.voicePreviewContainer.classList.add('hidden');
          this.dom.btnPlayPreview.innerText = '▶ Play Preview';
        }
      },
      onTimeUpdate: (secRemaining) => {
        if (this.audioRecorder.state === 'recording') {
          this.dom.recordTimer.innerText = `Recording... ${secRemaining}s left`;
        }
      }
    });
  }

  // --- ZERO-DEPENDENCY SYNTHESIZED SOUND EFFECTS ---
  initAudioContext() {
    this.audioCtx = null;
    const unlock = () => {
      if (!this.audioCtx) {
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        if (AudioCtx) this.audioCtx = new AudioCtx();
      }
      if (this.audioCtx && this.audioCtx.state === 'suspended') {
        this.audioCtx.resume();
      }
      document.removeEventListener('pointerdown', unlock);
    };
    document.addEventListener('pointerdown', unlock, { once: true });
  }

  playTileSound() {
    if (!this.soundEnabled || !this.audioCtx) return;
    try {
      const now = this.audioCtx.currentTime;
      const osc = this.audioCtx.createOscillator();
      const gain = this.audioCtx.createGain();

      osc.type = 'triangle';
      osc.frequency.setValueAtTime(320, now);
      osc.frequency.exponentialRampToValueAtTime(140, now + 0.08);

      gain.gain.setValueAtTime(0.3, now);
      gain.gain.exponentialRampToValueAtTime(0.01, now + 0.08);

      osc.connect(gain);
      gain.connect(this.audioCtx.destination);
      osc.start(now);
      osc.stop(now + 0.08);
    } catch (_) {}
  }

  playSuccessSound() {
    if (!this.soundEnabled || !this.audioCtx) return;
    try {
      const notes = [523.25, 659.25, 783.99, 1046.50]; // C5, E5, G5, C6
      notes.forEach((freq, i) => {
        const osc = this.audioCtx.createOscillator();
        const gain = this.audioCtx.createGain();
        const start = this.audioCtx.currentTime + i * 0.09;

        osc.type = 'sine';
        osc.frequency.setValueAtTime(freq, start);

        gain.gain.setValueAtTime(0.22, start);
        gain.gain.exponentialRampToValueAtTime(0.001, start + 0.22);

        osc.connect(gain);
        gain.connect(this.audioCtx.destination);
        osc.start(start);
        osc.stop(start + 0.22);
      });
    } catch (_) {}
  }

  playErrorSound() {
    if (!this.soundEnabled || !this.audioCtx) return;
    try {
      const now = this.audioCtx.currentTime;
      const osc = this.audioCtx.createOscillator();
      const gain = this.audioCtx.createGain();

      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(180, now);
      osc.frequency.setValueAtTime(130, now + 0.08);

      gain.gain.setValueAtTime(0.25, now);
      gain.gain.exponentialRampToValueAtTime(0.01, now + 0.2);

      osc.connect(gain);
      gain.connect(this.audioCtx.destination);
      osc.start(now);
      osc.stop(now + 0.2);
    } catch (_) {}
  }

  playCheerSound() {
    if (!this.soundEnabled || !this.audioCtx) return;
    try {
      const chords = [659.25, 830.61, 987.77]; // E5, G#5, B5
      chords.forEach((freq) => {
        const osc = this.audioCtx.createOscillator();
        const gain = this.audioCtx.createGain();
        const now = this.audioCtx.currentTime;

        osc.type = 'triangle';
        osc.frequency.setValueAtTime(freq, now);

        gain.gain.setValueAtTime(0.2, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.4);

        osc.connect(gain);
        gain.connect(this.audioCtx.destination);
        osc.start(now);
        osc.stop(now + 0.4);
      });
    } catch (_) {}
  }

  speakAnnouncement(text, lang = 'en') {
    if (!this.soundEnabled) return;

    if (this.lastAnnouncementAudio) {
      try {
        this.lastAnnouncementAudio.pause();
      } catch (_) {}
      this.lastAnnouncementAudio = null;
    }

    // Try server neural voice endpoint
    const ttsUrl = `/api/tts?text=${encodeURIComponent(text)}&lang=${lang}`;
    const audio = new Audio(ttsUrl);
    this.lastAnnouncementAudio = audio;

    audio.play().catch(() => {
      // Fallback to Web Speech API
      if (window.speechSynthesis) {
        try {
          if (window.speechSynthesis.paused) window.speechSynthesis.resume();
          window.speechSynthesis.cancel();
          const utterance = new SpeechSynthesisUtterance(text);
          const langConf = LANG_CONFIGS[lang] || LANG_CONFIGS.en;
          utterance.lang = langConf.speechLocale;
          window.speechSynthesis.speak(utterance);
        } catch (_) {}
      }
    });
  }

  // --- SERVICE WORKER REGISTRATION ---
  registerServiceWorker() {
    if ('serviceWorker' in navigator && window.location.protocol.startsWith('http')) {
      navigator.serviceWorker.register('/mobile/service-worker.js').then((reg) => {
        console.log('[ServiceWorker] Registered with scope:', reg.scope);
      }).catch((err) => {
        console.warn('[ServiceWorker] Registration error:', err);
      });
    }
  }

  // --- EVENT BINDINGS ---
  bindEvents() {
    // Navigation
    this.dom.btnNavLobby.addEventListener('click', () => {
      if (this.currentView === 'game') {
        this.showLobbyView();
      } else if (this.currentGame) {
        this.showGameView(this.currentGame.id);
      }
    });

    this.dom.navBrandBtn.addEventListener('click', () => {
      this.showLobbyView();
    });

    // Toggle Sound
    this.dom.btnToggleSound.addEventListener('click', () => {
      this.soundEnabled = !this.soundEnabled;
      this.dom.soundIcon.innerText = this.soundEnabled ? '🔊' : '🔇';
      this.showToast(this.soundEnabled ? 'Sound Enabled' : 'Sound Muted');
    });

    // User Profile / Google Sign In
    this.dom.btnUserProfile.addEventListener('click', async () => {
      const user = await this.firebaseService.signInWithGoogle();
      this.dom.userDisplayName.innerText = user.displayName.split(' ')[0];
      this.dom.userAvatar.innerText = user.avatar || '👩‍🦰';
      this.showToast(`Signed in as ${user.displayName}`);
    });

    // Viewport HUD Controls
    this.dom.btnZoomIn.addEventListener('click', () => this.viewport.zoomIn());
    this.dom.btnZoomOut.addEventListener('click', () => this.viewport.zoomOut());
    this.dom.btnFitScreen.addEventListener('click', () => this.viewport.fitToScreen(true));

    // Lobby: Quick board ID chips
    document.querySelectorAll('.chip-btn[data-board]').forEach(btn => {
      btn.addEventListener('click', () => {
        this.dom.inputBoardId.value = btn.dataset.board;
      });
    });

    // Lobby: Mode selector
    this.dom.optModeCasual.addEventListener('click', () => {
      this.dom.optModeCasual.classList.add('selected');
      this.dom.optModeStrict.classList.remove('selected');
    });
    this.dom.optModeStrict.addEventListener('click', () => {
      this.dom.optModeStrict.classList.add('selected');
      this.dom.optModeCasual.classList.remove('selected');
    });

    // Lobby: Create or resume game
    this.dom.btnCreateGame.addEventListener('click', () => this.handleCreateGameSubmit());

    // Game: Rack Actions
    this.dom.btnRackShuffle.addEventListener('click', () => this.handleRackShuffle());
    this.dom.btnRackRecall.addEventListener('click', () => this.handleRackRecall());
    this.dom.btnRackExchange.addEventListener('click', () => this.openExchangeModal());
    this.dom.btnRackCheer.addEventListener('click', () => this.openVoiceModal());
    this.dom.btnRackSubmit.addEventListener('click', () => this.handleSubmitMove());

    // Game: Simulate Board Turn
    this.dom.btnSimBoardMove.addEventListener('click', () => this.handleSimulateBoardMove());

    // Game: Cheer Bubble click
    this.dom.cheerBubblePreview.addEventListener('click', () => this.openVoiceModal());

    // Voice Modal events
    this.dom.btnCloseVoiceModal.addEventListener('click', () => this.closeVoiceModal());
    this.dom.modalVoice.addEventListener('click', (e) => {
      if (e.target === this.dom.modalVoice) this.closeVoiceModal();
    });

    this.dom.btnRecordMic.addEventListener('click', async () => {
      if (this.audioRecorder.state === 'recording') {
        this.audioRecorder.stopRecording();
      } else {
        try {
          await this.audioRecorder.startRecording();
        } catch (err) {
          this.showToast('Microphone error: ' + err.message);
        }
      }
    });

    this.dom.btnPlayPreview.addEventListener('click', () => {
      if (this.audioRecorder.state === 'playing') {
        this.audioRecorder.pausePreview();
      } else {
        this.audioRecorder.playPreview();
      }
    });

    this.dom.btnResetRecording.addEventListener('click', () => {
      this.audioRecorder.reset();
    });

    // Preset cheer chips
    document.querySelectorAll('.preset-chip').forEach(btn => {
      btn.addEventListener('click', () => {
        this.dom.inputCheerText.value = btn.dataset.text;
      });
    });

    this.dom.btnSendCheer.addEventListener('click', () => this.handleSendCheerSubmit());

    // Exchange Modal events
    this.dom.btnCloseExchangeModal.addEventListener('click', () => this.closeExchangeModal());
    this.dom.modalExchange.addEventListener('click', (e) => {
      if (e.target === this.dom.modalExchange) this.closeExchangeModal();
    });
    this.dom.btnConfirmExchange.addEventListener('click', () => this.handleConfirmExchange());
  }

  // --- VIEW MANAGEMENT ---
  async showLobbyView() {
    this.currentView = 'lobby';
    this.dom.viewLobby.classList.remove('hidden');
    this.dom.viewGame.classList.add('hidden');
    this.dom.navLobbyText.innerText = this.currentGame ? 'Game' : 'Lobby';

    if (this.unsubscribeGameListener) {
      this.unsubscribeGameListener();
      this.unsubscribeGameListener = null;
    }

    const games = await this.firebaseService.listActiveGames();
    this.renderLobbyGames(games);

    const boards = await this.firebaseService.getPairedBoards();
    this.renderPairedBoards(boards);
  }

  async showGameView(gameId) {
    this.currentView = 'game';
    this.dom.viewLobby.classList.add('hidden');
    this.dom.viewGame.classList.remove('hidden');
    this.dom.navLobbyText.innerText = 'Lobby';

    // Clear any pending placements
    this.pendingPlacements = [];
    this.selectedRackIndex = null;

    // Listen to real-time updates for this game
    if (this.unsubscribeGameListener) {
      this.unsubscribeGameListener();
    }
    this.unsubscribeGameListener = this.firebaseService.listenToGame(gameId, (game) => {
      this.onGameUpdated(game);
    });

    const game = await this.firebaseService.getGame(gameId);
    if (game) {
      this.onGameUpdated(game);
      // Preload dictionary
      this.engine.loadDictionary(game.lang);
      setTimeout(() => this.viewport.fitToScreen(false), 100);
    }
  }

  onGameUpdated(game) {
    this.currentGame = game;
    const currentUser = this.firebaseService.currentUser;

    const myPlayer = game.players.find(p => !p.isRemote) || game.players[0];
    const boardPlayer = game.players.find(p => p.isRemote) || game.players[1];

    // Update HUD
    this.dom.hudBoardInfo.innerText = `${boardPlayer.name}'s Board (${game.boardId})`;
    this.dom.hudModePill.innerText = game.mode.toUpperCase();

    this.dom.hudPlayerName.innerText = `${myPlayer.name} (You)`;
    this.dom.hudPlayerAvatar.innerText = myPlayer.avatar || '👩‍🦰';
    this.dom.hudPlayerScore.innerText = myPlayer.score;

    this.dom.hudBoardName.innerText = boardPlayer.name;
    this.dom.hudBoardAvatar.innerText = boardPlayer.avatar || '👵';
    this.dom.hudBoardScore.innerText = boardPlayer.score;

    this.dom.hudBagCount.innerText = game.tileBag.length;

    // Active Turn highlight
    const isMyTurn = game.currentTurnPlayerId === myPlayer.id;
    if (isMyTurn) {
      this.dom.scoreCardMobile.classList.add('active-turn');
      this.dom.scoreCardBoard.classList.remove('active-turn');
      this.dom.syncStatusText.innerText = "It's your turn! Place tiles and submit.";
    } else {
      this.dom.scoreCardMobile.classList.remove('active-turn');
      this.dom.scoreCardBoard.classList.add('active-turn');
      this.dom.syncStatusText.innerText = `${boardPlayer.name} is playing at the wooden board...`;
    }

    // Latest move highlight coordinates
    const lastMove = game.moveHistory[game.moveHistory.length - 1];
    const lastPlacements = lastMove ? lastMove.placements : [];

    // Render Board
    this.viewport.renderBoard(
      game.board,
      this.pendingPlacements,
      lastPlacements,
      game.lang
    );

    // Render Rack
    this.renderRack();

    // Update Latest Cheer bubble
    if (game.cheerHistory && game.cheerHistory.length > 0) {
      const latestCheer = game.cheerHistory[game.cheerHistory.length - 1];
      this.dom.cheerPreviewText.innerText = `${latestCheer.senderName}: "${latestCheer.text || 'Sent audio note 🎙️'}"`;
    }

    // Update announcement banner
    if (lastMove) {
      this.dom.refereeText.innerText = `Latest: ${lastMove.playerName} played ${lastMove.words[0].word} (+${lastMove.totalScore} pts)`;
      this.dom.refereeBanner.className = 'referee-banner success';
    } else {
      this.dom.refereeText.innerText = 'First move must cover center star (H8).';
      this.dom.refereeBanner.className = 'referee-banner';
    }
  }

  // --- LOBBY RENDERING ---
  renderLobbyGames(games) {
    this.dom.activeGamesList.innerHTML = '';
    this.dom.badgeActiveCount.innerText = `${games.length} Game${games.length === 1 ? '' : 's'}`;

    if (games.length === 0) {
      this.dom.activeGamesList.innerHTML = `
        <div style="text-align: center; padding: 20px; color: #7A5333;">
          No active games. Start a game below to connect to a board!
        </div>
      `;
      return;
    }

    const currentUid = this.firebaseService.currentUser ? this.firebaseService.currentUser.uid : null;

    games.forEach(game => {
      const myPlayer = game.players.find(p => !p.isRemote) || game.players[0];
      const boardPlayer = game.players.find(p => p.isRemote) || game.players[1];
      const isMyTurn = game.currentTurnPlayerId === myPlayer.id;

      const card = document.createElement('div');
      card.className = `game-card ${isMyTurn ? 'your-turn' : ''}`;

      const lastMove = game.moveHistory[game.moveHistory.length - 1];
      const lastMoveText = lastMove
        ? `${lastMove.playerName} played "${lastMove.words[0].word}" (+${lastMove.totalScore})`
        : 'First turn pending';

      card.innerHTML = `
        <div class="game-card-header">
          <div class="player-info-pair">
            <span class="player-avatar">${boardPlayer.avatar || '👵'}</span>
            <div class="player-names-group">
              <span class="opponent-name">${boardPlayer.name}</span>
              <span class="board-id-tag">${game.boardId} • ${game.mode.toUpperCase()}</span>
            </div>
          </div>
          <span class="turn-pill ${isMyTurn ? 'mine' : 'waiting'}">
            ${isMyTurn ? 'Your Turn' : "Board's Turn"}
          </span>
        </div>

        <div class="game-score-row">
          <span>You: <strong class="score-display">${myPlayer.score}</strong></span>
          <span>${boardPlayer.name}: <strong class="score-display">${boardPlayer.score}</strong></span>
          <span style="color: #7A5333;">${game.tileBag.length} tiles left</span>
        </div>

        <div class="last-move-preview">
          <span>⏱️ ${lastMoveText}</span>
        </div>
      `;

      card.addEventListener('click', () => {
        this.playTileSound();
        this.showGameView(game.id);
      });

      this.dom.activeGamesList.appendChild(card);
    });
  }

  renderPairedBoards(boards) {
    this.dom.pairedBoardsList.innerHTML = '';
    boards.forEach(b => {
      const item = document.createElement('div');
      item.className = 'paired-board-item';
      item.innerHTML = `
        <div>
          <div style="font-weight: 700; color: #4A2810;">
            <span class="status-dot ${b.status}"></span>
            ${b.name}
          </div>
          <div style="font-size: 0.75rem; color: #7A5333; font-family: monospace;">ID: ${b.id} • ${b.location}</div>
        </div>
        <button type="button" class="chip-btn" style="background: #8B5A2B; color: #FFF; border: none;">
          Pair
        </button>
      `;

      item.querySelector('button').addEventListener('click', () => {
        this.dom.inputBoardId.value = b.id;
        this.dom.inputOpponentName.value = b.name.replace("'s Board", "");
        this.showToast(`Selected ${b.name}`);
      });

      this.dom.pairedBoardsList.appendChild(item);
    });
  }

  async handleCreateGameSubmit() {
    const boardId = this.dom.inputBoardId.value.trim();
    const opponentName = this.dom.inputOpponentName.value.trim();
    const lang = this.dom.selectGameLang.value;
    const mode = this.dom.optModeStrict.classList.contains('selected') ? 'strict' : 'casual';

    if (!boardId) {
      this.showToast('Please enter a valid Board ID');
      return;
    }

    try {
      this.playTileSound();
      const game = await this.firebaseService.createGame({
        boardId,
        opponentName,
        lang,
        mode
      });

      await this.firebaseService.pairBoard(boardId, `${opponentName}'s Board`);
      this.showToast(`Game started with ${opponentName}!`);
      this.showGameView(game.id);
    } catch (err) {
      this.showToast('Error creating game: ' + err.message);
    }
  }

  // --- RACK MANAGEMENT ---
  renderRack() {
    if (!this.currentGame) return;

    const myPlayer = this.currentGame.players.find(p => !p.isRemote) || this.currentGame.players[0];
    const langConf = LANG_CONFIGS[this.currentGame.lang] || LANG_CONFIGS.en;

    this.dom.rackTray.innerHTML = '';

    myPlayer.rack.forEach((tile, index) => {
      const tileEl = document.createElement('div');
      tileEl.className = 'rack-tile';

      if (tile === null) {
        tileEl.classList.add('empty-slot');
        tileEl.title = 'Empty slot';
        tileEl.addEventListener('click', () => {
          // If we have pending placements, recall the last one back to this slot
          if (this.pendingPlacements.length > 0) {
            const lastPending = this.pendingPlacements.pop();
            myPlayer.rack[index] = new Tile({
              letter: lastPending.letter,
              value: langConf.letterValues[lastPending.letter] || 1
            });
            this.playTileSound();
            this.renderRack();
            this.viewport.renderBoard(this.currentGame.board, this.pendingPlacements, [], this.currentGame.lang);
            this.validatePendingMovePreview();
          }
        });
      } else {
        if (this.selectedRackIndex === index) {
          tileEl.classList.add('selected');
        }

        const letSpan = document.createElement('span');
        letSpan.className = 'tile-letter';
        letSpan.innerText = tile.letter;

        const ptSpan = document.createElement('span');
        ptSpan.className = 'tile-points';
        ptSpan.innerText = tile.value;

        tileEl.appendChild(letSpan);
        tileEl.appendChild(ptSpan);

        tileEl.addEventListener('click', () => {
          this.playTileSound();
          if (this.selectedRackIndex === index) {
            this.selectedRackIndex = null;
          } else {
            this.selectedRackIndex = index;
          }
          this.renderRack();
        });
      }

      this.dom.rackTray.appendChild(tileEl);
    });
  }

  handleCellTapped(r, c) {
    if (!this.currentGame) return;

    const myPlayer = this.currentGame.players.find(p => !p.isRemote) || this.currentGame.players[0];
    const langConf = LANG_CONFIGS[this.currentGame.lang] || LANG_CONFIGS.en;

    // 1. Check if cell is an existing pending placement made in this turn
    const pendingIdx = this.pendingPlacements.findIndex(p => p.row === r && p.col === c);
    if (pendingIdx !== -1) {
      // Recall this single pending tile back to the rack
      const recalled = this.pendingPlacements.splice(pendingIdx, 1)[0];
      myPlayer.rack[recalled.rackIndex] = new Tile({
        letter: recalled.letter,
        value: langConf.letterValues[recalled.letter] || 1
      });

      this.playTileSound();
      this.renderRack();
      this.viewport.renderBoard(this.currentGame.board, this.pendingPlacements, [], this.currentGame.lang);
      this.validatePendingMovePreview();
      return;
    }

    // 2. Cell is permanently occupied by board tile
    if (this.currentGame.board.getCell(r, c) !== null) {
      const letter = this.currentGame.board.getCell(r, c);
      this.showToast(`Square (${r + 1}, ${c + 1}): letter ${letter}`);
      return;
    }

    // 3. Cell is empty and user has a rack tile selected
    if (this.selectedRackIndex !== null && myPlayer.rack[this.selectedRackIndex] !== null) {
      const tile = myPlayer.rack[this.selectedRackIndex];
      myPlayer.rack[this.selectedRackIndex] = null;

      this.pendingPlacements.push({
        row: r,
        col: c,
        letter: tile.letter,
        rackIndex: this.selectedRackIndex
      });

      this.selectedRackIndex = null;
      this.playTileSound();
      this.renderRack();
      this.viewport.renderBoard(this.currentGame.board, this.pendingPlacements, [], this.currentGame.lang);
      this.validatePendingMovePreview();
    }
  }

  validatePendingMovePreview() {
    if (this.pendingPlacements.length === 0) {
      this.dom.refereeBanner.className = 'referee-banner';
      this.dom.refereeText.innerText = 'Place tiles from your rack onto the board.';
      this.dom.refereeBadge.innerText = '★ Ready';
      return;
    }

    const result = this.engine.validateMove({
      board: this.currentGame.board,
      placements: this.pendingPlacements,
      lang: this.currentGame.lang
    });

    if (result.ok) {
      const wordsStr = result.words.map(w => `${w.word} (${w.score} pts)`).join(', ');
      this.dom.refereeBanner.className = 'referee-banner success';
      this.dom.refereeText.innerText = `Valid! ${wordsStr} ${result.isBingo ? '+50 BINGO!' : ''}`;
      this.dom.refereeBadge.innerText = `+${result.totalScore} pts`;
    } else {
      this.dom.refereeBanner.className = 'referee-banner error';
      this.dom.refereeText.innerText = result.error;
      this.dom.refereeBadge.innerText = 'Invalid';
    }
  }

  handleRackShuffle() {
    if (!this.currentGame) return;
    const myPlayer = this.currentGame.players.find(p => !p.isRemote) || this.currentGame.players[0];

    // Shuffle only existing non-null rack tiles
    const existing = myPlayer.rack.filter(t => t !== null);
    for (let i = existing.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      const tmp = existing[i];
      existing[i] = existing[j];
      existing[j] = tmp;
    }

    let exIdx = 0;
    for (let i = 0; i < myPlayer.rack.length; i++) {
      if (myPlayer.rack[i] !== null) {
        myPlayer.rack[i] = existing[exIdx++];
      }
    }

    this.playTileSound();
    this.renderRack();
  }

  handleRackRecall() {
    if (!this.currentGame || this.pendingPlacements.length === 0) return;
    const myPlayer = this.currentGame.players.find(p => !p.isRemote) || this.currentGame.players[0];
    const langConf = LANG_CONFIGS[this.currentGame.lang] || LANG_CONFIGS.en;

    this.pendingPlacements.forEach(p => {
      myPlayer.rack[p.rackIndex] = new Tile({
        letter: p.letter,
        value: langConf.letterValues[p.letter] || 1
      });
    });

    this.pendingPlacements = [];
    this.playTileSound();
    this.renderRack();
    this.viewport.renderBoard(this.currentGame.board, [], [], this.currentGame.lang);
    this.validatePendingMovePreview();
    this.showToast('Recalled all pending tiles to rack');
  }

  // --- SUBMIT MOVE ---
  async handleSubmitMove() {
    if (!this.currentGame) return;

    if (this.pendingPlacements.length === 0) {
      this.showToast('Please place tiles onto the board first.');
      this.playErrorSound();
      return;
    }

    const result = this.engine.validateMove({
      board: this.currentGame.board,
      placements: this.pendingPlacements,
      lang: this.currentGame.lang
    });

    if (!result.ok) {
      this.playErrorSound();
      this.showToast(result.error);
      this.dom.refereeBanner.className = 'referee-banner error';
      this.dom.refereeText.innerText = result.error;
      this.speakAnnouncement(result.error, this.currentGame.lang);
      return;
    }

    // Move is valid!
    this.playSuccessSound();

    const myPlayer = this.currentGame.players.find(p => !p.isRemote) || this.currentGame.players[0];
    const moveData = {
      playerId: myPlayer.id,
      playerName: myPlayer.name,
      placements: this.pendingPlacements.map(p => ({ row: p.row, col: p.col, letter: p.letter })),
      words: result.words,
      totalScore: result.totalScore,
      isBingo: result.isBingo
    };

    // Replenish player's rack
    this.currentGame.fillRack(myPlayer);

    // Announce move verbally
    const primaryWord = result.words[0].word;
    const spelled = primaryWord.split('').join(' - ');
    const announceMsg = `Valid move! ${spelled}. ${primaryWord}, for ${result.totalScore} points.`;
    setTimeout(() => this.speakAnnouncement(announceMsg, this.currentGame.lang), 400);

    // Submit to Firebase / Mock
    await this.firebaseService.submitMove(this.currentGame.id, moveData);

    this.pendingPlacements = [];
    this.showToast(`Played ${primaryWord} for ${result.totalScore} pts!`);

    // Board Placement Prompt
    this.dom.syncStatusText.innerText = "Move placed! Physical board automatically syncing via RFID...";

    // Auto-confirm physical sync after 3 seconds
    setTimeout(() => {
      this.firebaseService.confirmBoardRfidSync(this.currentGame.id);
      this.showToast("Physical board verified all RFID tiles!");
    }, 3200);
  }

  // --- SIMULATE BOARD MOVE ---
  async handleSimulateBoardMove() {
    if (!this.currentGame) return;

    this.showToast("Grandma is placing tiles on the physical board...");
    this.playTileSound();

    setTimeout(async () => {
      const updatedGame = await this.firebaseService.simulateBoardMove(this.currentGame.id);
      if (updatedGame) {
        this.playSuccessSound();
        const lastMove = updatedGame.moveHistory[updatedGame.moveHistory.length - 1];
        if (lastMove) {
          const announce = `${lastMove.playerName} played ${lastMove.words[0].word} for ${lastMove.totalScore} points!`;
          this.showToast(announce);
          this.speakAnnouncement(announce, updatedGame.lang);
        }
      }
    }, 1200);
  }

  // --- VOICE NOTE & CHEER MODAL ---
  openVoiceModal() {
    this.dom.modalVoice.classList.remove('hidden');
    this.dom.inputCheerText.value = '';
    this.audioRecorder.reset();
  }

  closeVoiceModal() {
    this.dom.modalVoice.classList.add('hidden');
    this.audioRecorder.reset();
  }

  async handleSendCheerSubmit() {
    if (!this.currentGame) return;

    const text = this.dom.inputCheerText.value.trim();
    const recorded = this.audioRecorder.getRecordedAudio();

    if (!text && !recorded.blob) {
      this.showToast('Please type a message or record a voice note.');
      return;
    }

    const myPlayer = this.currentGame.players.find(p => !p.isRemote) || this.currentGame.players[0];

    const cheerData = {
      senderId: myPlayer.id,
      senderName: myPlayer.name,
      text: text || 'Voice Note 🎙️',
      audioData: recorded.dataUrl,
      audioDuration: recorded.duration
    };

    await this.firebaseService.sendCheer(this.currentGame.id, cheerData);
    this.playCheerSound();
    this.closeVoiceModal();
    this.showToast('Cheer delivered to Grandma’s Board!');
  }

  // --- TILE EXCHANGE MODAL ---
  openExchangeModal() {
    if (!this.currentGame) return;
    const myPlayer = this.currentGame.players.find(p => !p.isRemote) || this.currentGame.players[0];

    this.selectedExchangeIndices.clear();
    this.dom.exchangeTilesGrid.innerHTML = '';

    myPlayer.rack.forEach((tile, index) => {
      if (tile === null) return;
      const tileCard = document.createElement('div');
      tileCard.className = 'exchange-tile-card';
      tileCard.innerText = tile.letter;

      tileCard.addEventListener('click', () => {
        if (this.selectedExchangeIndices.has(index)) {
          this.selectedExchangeIndices.delete(index);
          tileCard.classList.remove('selected');
        } else {
          this.selectedExchangeIndices.add(index);
          tileCard.classList.add('selected');
        }
      });

      this.dom.exchangeTilesGrid.appendChild(tileCard);
    });

    this.dom.modalExchange.classList.remove('hidden');
  }

  closeExchangeModal() {
    this.dom.modalExchange.classList.add('hidden');
  }

  handleConfirmExchange() {
    if (this.selectedExchangeIndices.size === 0) {
      this.showToast('Select at least one tile to swap.');
      return;
    }

    const myPlayer = this.currentGame.players.find(p => !p.isRemote) || this.currentGame.players[0];

    // Return selected tiles to bag
    this.selectedExchangeIndices.forEach(idx => {
      const t = myPlayer.rack[idx];
      if (t) {
        this.currentGame.tileBag.push(t.letter);
        myPlayer.rack[idx] = null;
      }
    });

    this.currentGame.shuffleTileBag();
    this.currentGame.fillRack(myPlayer);

    // Pass turn to opponent
    const opponent = this.currentGame.getOpponent(myPlayer.id);
    if (opponent) {
      this.currentGame.currentTurnPlayerId = opponent.id;
    }

    this.playTileSound();
    this.closeExchangeModal();
    this.renderRack();
    this.showToast(`Exchanged ${this.selectedExchangeIndices.size} tiles. Turn passed to ${opponent.name}.`);
  }

  // --- TOAST NOTIFICATIONS ---
  showToast(message, durationMs = 3000) {
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.innerText = message;
    this.dom.toastContainer.appendChild(toast);

    setTimeout(() => {
      toast.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
      setTimeout(() => toast.remove(), 300);
    }, durationMs);
  }
}

// Start app on DOMContentLoaded
window.addEventListener('DOMContentLoaded', () => {
  const app = new CrosswordApp();
  window.app = app;
  app.init();
});

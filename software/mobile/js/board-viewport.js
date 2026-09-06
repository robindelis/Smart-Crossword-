// Smart Crossword Board - Touch Gestures Board Viewport Controller
// Handles multi-touch pinch-to-zoom (0.7x - 2.5x), smooth panning, double-tap toggle zoom,
// fit-to-screen, cell coordinate mapping, and tile placements.

class BoardViewport {
  constructor({
    viewportEl,
    boardContainerEl,
    boardGridEl,
    onCellTapped = null,
    onZoomChanged = null
  }) {
    this.viewportEl = viewportEl;
    this.boardContainerEl = boardContainerEl;
    this.boardGridEl = boardGridEl;
    this.onCellTapped = onCellTapped;
    this.onZoomChanged = onZoomChanged;

    // Viewport transform state
    this.scale = 1.0;
    this.minScale = 0.65;
    this.maxScale = 2.5;
    this.translateX = 0;
    this.translateY = 0;

    // Touch gesture tracking
    this.activePointers = new Map();
    this.startDistance = 0;
    this.startScale = 1.0;
    this.startMidpoint = { x: 0, y: 0 };
    this.startTranslate = { x: 0, y: 0 };
    this.isDragging = false;
    this.dragStartPoint = { x: 0, y: 0 };
    this.lastTapTime = 0;
    this.lastTapPos = { x: 0, y: 0 };

    this.initEvents();
    this.setupBoardCells();
  }

  setupBoardCells() {
    this.boardGridEl.innerHTML = '';

    for (let r = 0; r < BOARD_SIZE; r++) {
      for (let c = 0; c < BOARD_SIZE; c++) {
        const cell = document.createElement('div');
        cell.className = 'board-cell';
        cell.dataset.row = r;
        cell.dataset.col = c;

        // Apply bonus square classes
        const bonus = BONUS_GRID[r][c];
        if (r === 7 && c === 7) {
          cell.classList.add('cell-star');
          cell.innerHTML = '<span class="cell-bonus-text">★</span>';
        } else if (bonus === BONUS_TWS) {
          cell.classList.add('cell-tws');
          cell.innerHTML = '<span class="cell-bonus-text">3W</span>';
        } else if (bonus === BONUS_DWS) {
          cell.classList.add('cell-dws');
          cell.innerHTML = '<span class="cell-bonus-text">2W</span>';
        } else if (bonus === BONUS_TLS) {
          cell.classList.add('cell-tls');
          cell.innerHTML = '<span class="cell-bonus-text">3L</span>';
        } else if (bonus === BONUS_DLS) {
          cell.classList.add('cell-dls');
          cell.innerHTML = '<span class="cell-bonus-text">2L</span>';
        }

        this.boardGridEl.appendChild(cell);
      }
    }
  }

  initEvents() {
    // Touch & Pointer event listeners
    this.viewportEl.addEventListener('pointerdown', (e) => this.handlePointerDown(e), { passive: false });
    this.viewportEl.addEventListener('pointermove', (e) => this.handlePointerMove(e), { passive: false });
    this.viewportEl.addEventListener('pointerup', (e) => this.handlePointerUp(e), { passive: false });
    this.viewportEl.addEventListener('pointercancel', (e) => this.handlePointerUp(e), { passive: false });

    // Wheel zoom for desktop testing
    this.viewportEl.addEventListener('wheel', (e) => {
      e.preventDefault();
      const zoomFactor = e.deltaY < 0 ? 1.15 : 0.85;
      this.zoomAt(e.clientX, e.clientY, this.scale * zoomFactor);
    }, { passive: false });

    // Handle resize
    window.addEventListener('resize', () => {
      this.clampTranslation();
      this.applyTransform();
    });
  }

  handlePointerDown(e) {
    e.preventDefault();
    this.activePointers.set(e.pointerId, { x: e.clientX, y: e.clientY });

    if (this.activePointers.size === 1) {
      // Single pointer: pan or tap
      this.isDragging = false;
      this.dragStartPoint = { x: e.clientX, y: e.clientY };
      this.startTranslate = { x: this.translateX, y: this.translateY };
    } else if (this.activePointers.size === 2) {
      // Two pointers: pinch-to-zoom
      const [p1, p2] = Array.from(this.activePointers.values());
      this.startDistance = Math.hypot(p2.x - p1.x, p2.y - p1.y);
      this.startScale = this.scale;
      this.startMidpoint = { x: (p1.x + p2.x) / 2, y: (p1.y + p2.y) / 2 };
      this.startTranslate = { x: this.translateX, y: this.translateY };
      this.isDragging = true;
    }
  }

  handlePointerMove(e) {
    if (!this.activePointers.has(e.pointerId)) return;
    e.preventDefault();

    this.activePointers.set(e.pointerId, { x: e.clientX, y: e.clientY });

    if (this.activePointers.size === 1) {
      const p = this.activePointers.get(e.pointerId);
      const dx = p.x - this.dragStartPoint.x;
      const dy = p.y - this.dragStartPoint.y;

      if (!this.isDragging && Math.hypot(dx, dy) > 8) {
        this.isDragging = true;
      }

      if (this.isDragging) {
        this.translateX = this.startTranslate.x + dx;
        this.translateY = this.startTranslate.y + dy;
        this.clampTranslation();
        this.applyTransform();
      }
    } else if (this.activePointers.size === 2) {
      const [p1, p2] = Array.from(this.activePointers.values());
      const currentDistance = Math.hypot(p2.x - p1.x, p2.y - p1.y);

      if (this.startDistance > 0) {
        const factor = currentDistance / this.startDistance;
        const newScale = Math.min(this.maxScale, Math.max(this.minScale, this.startScale * factor));
        
        // Midpoint zoom
        const midX = (p1.x + p2.x) / 2;
        const midY = (p1.y + p2.y) / 2;
        this.zoomAt(midX, midY, newScale);
      }
    }
  }

  handlePointerUp(e) {
    const wasTracking = this.activePointers.has(e.pointerId);
    this.activePointers.delete(e.pointerId);

    if (wasTracking && !this.isDragging && this.activePointers.size === 0) {
      // Tap detected!
      const now = Date.now();
      const tapX = e.clientX;
      const tapY = e.clientY;

      if (now - this.lastTapTime < 320 && Math.hypot(tapX - this.lastTapPos.x, tapY - this.lastTapPos.y) < 25) {
        // Double tap toggle zoom
        this.handleDoubleTap(tapX, tapY);
        this.lastTapTime = 0;
      } else {
        // Single tap on board cell
        this.lastTapTime = now;
        this.lastTapPos = { x: tapX, y: tapY };
        this.handleSingleTap(tapX, tapY);
      }
    }

    if (this.activePointers.size === 1) {
      // Switch back to 1-finger drag
      const p = Array.from(this.activePointers.values())[0];
      this.dragStartPoint = { x: p.x, y: p.y };
      this.startTranslate = { x: this.translateX, y: this.translateY };
    }
  }

  handleDoubleTap(clientX, clientY) {
    if (this.scale > 1.25) {
      // Reset to fit
      this.fitToScreen(true);
    } else {
      // Zoom in to 1.7x centered at tap
      this.zoomAt(clientX, clientY, 1.7, true);
    }
  }

  handleSingleTap(clientX, clientY) {
    const cellCoords = this.getCellAtPoint(clientX, clientY);
    if (cellCoords && this.onCellTapped) {
      this.onCellTapped(cellCoords.row, cellCoords.col);
    }
  }

  getCellAtPoint(clientX, clientY) {
    const rect = this.boardGridEl.getBoundingClientRect();
    if (
      clientX < rect.left ||
      clientX > rect.right ||
      clientY < rect.top ||
      clientY > rect.bottom
    ) {
      return null;
    }

    const cellWidth = rect.width / BOARD_SIZE;
    const cellHeight = rect.height / BOARD_SIZE;

    const col = Math.floor((clientX - rect.left) / cellWidth);
    const row = Math.floor((clientY - rect.top) / cellHeight);

    if (row >= 0 && row < BOARD_SIZE && col >= 0 && col < BOARD_SIZE) {
      return { row, col };
    }
    return null;
  }

  zoomAt(pivotX, pivotY, newScale, animate = false) {
    const targetScale = Math.min(this.maxScale, Math.max(this.minScale, newScale));
    const viewportRect = this.viewportEl.getBoundingClientRect();

    // Point relative to viewport center
    const originX = pivotX - viewportRect.left - viewportRect.width / 2;
    const originY = pivotY - viewportRect.top - viewportRect.height / 2;

    const scaleDiff = targetScale / this.scale;

    this.translateX = originX - (originX - this.translateX) * scaleDiff;
    this.translateY = originY - (originY - this.translateY) * scaleDiff;
    this.scale = targetScale;

    this.clampTranslation();
    this.applyTransform(animate);

    if (this.onZoomChanged) {
      this.onZoomChanged(this.scale);
    }
  }

  zoomIn() {
    const rect = this.viewportEl.getBoundingClientRect();
    this.zoomAt(rect.left + rect.width / 2, rect.top + rect.height / 2, this.scale * 1.3, true);
  }

  zoomOut() {
    const rect = this.viewportEl.getBoundingClientRect();
    this.zoomAt(rect.left + rect.width / 2, rect.top + rect.height / 2, this.scale / 1.3, true);
  }

  fitToScreen(animate = true) {
    const vpRect = this.viewportEl.getBoundingClientRect();
    const boardWidth = 600; // Reference board width from CSS
    const boardHeight = 600;

    const scaleX = (vpRect.width - 24) / boardWidth;
    const scaleY = (vpRect.height - 24) / boardHeight;
    const optimalScale = Math.min(scaleX, scaleY, 1.2);

    this.scale = Math.max(this.minScale, Math.min(this.maxScale, optimalScale));
    this.translateX = 0;
    this.translateY = 0;

    this.applyTransform(animate);

    if (this.onZoomChanged) {
      this.onZoomChanged(this.scale);
    }
  }

  clampTranslation() {
    const vpRect = this.viewportEl.getBoundingClientRect();
    const boardSize = 600 * this.scale;

    const maxPanX = Math.max(60, (boardSize - vpRect.width) / 2 + 100);
    const maxPanY = Math.max(60, (boardSize - vpRect.height) / 2 + 100);

    this.translateX = Math.max(-maxPanX, Math.min(maxPanX, this.translateX));
    this.translateY = Math.max(-maxPanY, Math.min(maxPanY, this.translateY));
  }

  applyTransform(animate = false) {
    if (animate) {
      this.boardContainerEl.style.transition = 'transform 0.28s cubic-bezier(0.2, 0, 0, 1)';
      setTimeout(() => {
        this.boardContainerEl.style.transition = 'none';
      }, 300);
    } else {
      this.boardContainerEl.style.transition = 'none';
    }

    this.boardContainerEl.style.transform = `translate3d(${this.translateX.toFixed(1)}px, ${this.translateY.toFixed(1)}px, 0) scale(${this.scale.toFixed(3)})`;
  }

  // Render board tiles, pending placements, and highlights
  renderBoard(board, pendingPlacements = [], lastMovePlacements = [], langCode = 'en') {
    const langConf = LANG_CONFIGS[langCode] || LANG_CONFIGS.en;
    const cells = this.boardGridEl.querySelectorAll('.board-cell');

    const pendingMap = new Map();
    for (const p of pendingPlacements) {
      pendingMap.set(`${p.row},${p.col}`, p);
    }

    const lastMoveSet = new Set(
      lastMovePlacements.map(p => `${p.row},${p.col}`)
    );

    cells.forEach(cell => {
      const r = parseInt(cell.dataset.row);
      const c = parseInt(cell.dataset.col);
      const key = `${r},${c}`;

      // Remove existing tile if any
      const existingTile = cell.querySelector('.placed-tile');
      if (existingTile) {
        existingTile.remove();
      }

      cell.classList.remove('has-tile', 'cell-last-move', 'cell-pending');

      const committedLetter = board.getCell(r, c);
      const pendingPlacement = pendingMap.get(key);

      if (pendingPlacement) {
        cell.classList.add('has-tile', 'cell-pending');
        const tileEl = this.createTileElement(
          pendingPlacement.letter,
          langConf.letterValues[pendingPlacement.letter] || 1,
          true
        );
        cell.appendChild(tileEl);
      } else if (committedLetter) {
        cell.classList.add('has-tile');
        if (lastMoveSet.has(key)) {
          cell.classList.add('cell-last-move');
        }
        const tileEl = this.createTileElement(
          committedLetter,
          langConf.letterValues[committedLetter] || 1,
          false
        );
        cell.appendChild(tileEl);
      }
    });
  }

  createTileElement(letter, points, isPending = false) {
    const tile = document.createElement('div');
    tile.className = `placed-tile ${isPending ? 'tile-pending' : 'tile-committed'}`;

    const letterSpan = document.createElement('span');
    letterSpan.className = 'tile-letter';
    letterSpan.innerText = letter;

    const pointsSpan = document.createElement('span');
    pointsSpan.className = 'tile-points';
    pointsSpan.innerText = points;

    tile.appendChild(letterSpan);
    tile.appendChild(pointsSpan);
    return tile;
  }
}

if (typeof window !== 'undefined') {
  window.BoardViewport = BoardViewport;
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { BoardViewport };
}

// Smart Crossword Board - Audio Recorder & Voice Notes
// Web MediaRecorder wrapper for 5-10s voice notes with audio level analysis,
// playback preview, and blob/base64 export.

class AudioRecorder {
  constructor({
    maxDurationSec = 10,
    onStateChange = null,
    onTimeUpdate = null,
    onAudioLevel = null
  } = {}) {
    this.maxDurationSec = maxDurationSec;
    this.onStateChange = onStateChange;
    this.onTimeUpdate = onTimeUpdate;
    this.onAudioLevel = onAudioLevel;

    this.state = 'idle'; // 'idle' | 'recording' | 'recorded' | 'playing'
    this.mediaRecorder = null;
    this.audioChunks = [];
    this.audioBlob = null;
    this.audioDataUrl = null;
    this.durationSec = 0;

    this.stream = null;
    this.audioContext = null;
    this.analyser = null;
    this.animFrameId = null;
    this.timerInterval = null;
    this.previewAudio = null;
  }

  setState(newState) {
    this.state = newState;
    if (this.onStateChange) {
      this.onStateChange(this.state);
    }
  }

  async startRecording() {
    if (this.state === 'recording') return;

    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error('Microphone access is not supported on this device/browser.');
      }

      this.stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      // Supported MIME types
      let mimeType = 'audio/webm';
      if (typeof MediaRecorder.isTypeSupported === 'function') {
        if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
          mimeType = 'audio/webm;codecs=opus';
        } else if (MediaRecorder.isTypeSupported('audio/mp4')) {
          mimeType = 'audio/mp4';
        } else if (MediaRecorder.isTypeSupported('audio/ogg')) {
          mimeType = 'audio/ogg';
        }
      }

      this.mediaRecorder = new MediaRecorder(this.stream, { mimeType });
      this.audioChunks = [];

      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          this.audioChunks.push(event.data);
        }
      };

      this.mediaRecorder.onstop = async () => {
        this.audioBlob = new Blob(this.audioChunks, { type: mimeType });
        this.audioDataUrl = await this.blobToDataUrl(this.audioBlob);
        this.cleanupStream();
        this.setState('recorded');
      };

      // Set up real-time audio visualizer
      this.setupVisualizer(this.stream);

      this.mediaRecorder.start(100);
      this.setState('recording');

      // Countdown timer
      let elapsed = 0;
      this.durationSec = 0;
      if (this.onTimeUpdate) this.onTimeUpdate(this.maxDurationSec);

      this.timerInterval = setInterval(() => {
        elapsed += 0.25;
        this.durationSec = Math.min(this.maxDurationSec, elapsed);
        const remaining = Math.max(0, Math.ceil(this.maxDurationSec - elapsed));

        if (this.onTimeUpdate) {
          this.onTimeUpdate(remaining);
        }

        if (elapsed >= this.maxDurationSec) {
          this.stopRecording();
        }
      }, 250);

    } catch (err) {
      console.warn('[AudioRecorder] Microphone error:', err);
      this.cleanupStream();
      this.setState('idle');
      throw err;
    }
  }

  setupVisualizer(stream) {
    try {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (!AudioCtx) return;

      this.audioContext = new AudioCtx();
      const source = this.audioContext.createMediaStreamSource(stream);
      this.analyser = this.audioContext.createAnalyser();
      this.analyser.fftSize = 64;
      source.connect(this.analyser);

      const bufferLength = this.analyser.frequencyBinCount;
      const dataArray = new Uint8Array(bufferLength);

      const checkLevel = () => {
        if (this.state !== 'recording') return;
        this.analyser.getByteFrequencyData(dataArray);

        let sum = 0;
        for (let i = 0; i < bufferLength; i++) {
          sum += dataArray[i];
        }
        const avg = sum / bufferLength;
        const normalized = Math.min(1.0, avg / 128);

        if (this.onAudioLevel) {
          this.onAudioLevel(normalized);
        }

        this.animFrameId = requestAnimationFrame(checkLevel);
      };

      checkLevel();
    } catch (_) {
      // Visualizer is purely decorative, fail gracefully
    }
  }

  stopRecording() {
    if (this.state !== 'recording') return;

    if (this.timerInterval) {
      clearInterval(this.timerInterval);
      this.timerInterval = null;
    }

    if (this.animFrameId) {
      cancelAnimationFrame(this.animFrameId);
      this.animFrameId = null;
    }

    if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
      this.mediaRecorder.stop();
    }
  }

  cleanupStream() {
    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop());
      this.stream = null;
    }

    if (this.audioContext) {
      try { this.audioContext.close(); } catch (_) {}
      this.audioContext = null;
    }
  }

  playPreview() {
    if (!this.audioBlob) return;

    if (this.previewAudio) {
      this.previewAudio.pause();
      this.previewAudio = null;
    }

    const url = URL.createObjectURL(this.audioBlob);
    this.previewAudio = new Audio(url);
    this.setState('playing');

    this.previewAudio.onended = () => {
      URL.revokeObjectURL(url);
      this.previewAudio = null;
      this.setState('recorded');
    };

    this.previewAudio.onerror = () => {
      this.setState('recorded');
    };

    this.previewAudio.play().catch(() => {
      this.setState('recorded');
    });
  }

  pausePreview() {
    if (this.previewAudio) {
      this.previewAudio.pause();
      this.setState('recorded');
    }
  }

  reset() {
    this.stopRecording();
    if (this.previewAudio) {
      this.previewAudio.pause();
      this.previewAudio = null;
    }
    this.audioBlob = null;
    this.audioDataUrl = null;
    this.audioChunks = [];
    this.durationSec = 0;
    this.setState('idle');
  }

  blobToDataUrl(blob) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = () => resolve(reader.result);
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  }

  getRecordedAudio() {
    return {
      blob: this.audioBlob,
      dataUrl: this.audioDataUrl,
      duration: Math.max(1, Math.round(this.durationSec))
    };
  }
}

if (typeof window !== 'undefined') {
  window.AudioRecorder = AudioRecorder;
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { AudioRecorder };
}

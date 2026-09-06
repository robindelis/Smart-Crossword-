document.addEventListener('DOMContentLoaded', () => {
  const vipForm = document.getElementById('vipForm');
  const vipEmail = document.getElementById('vipEmail');
  const interactiveGrid = document.getElementById('interactiveGrid');

  // Interactive Tile Click Demo
  if (interactiveGrid) {
    interactiveGrid.addEventListener('click', (e) => {
      const cell = e.target.closest('.grid-cell');
      if (!cell || cell.classList.contains('empty')) return;

      const letter = cell.dataset.letter;
      const score = cell.dataset.score;

      // Small bounce animation
      cell.style.transform = 'scale(1.15)';
      setTimeout(() => {
        cell.style.transform = '';
      }, 150);

      // Play soft sound simulation
      playSoftClickSound();
    });
  }

  // Handle $1 VIP Reservation Submission
  if (vipForm) {
    vipForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const email = vipEmail.value.trim();

      if (!isValidEmail(email)) {
        alert('Please enter a valid email address.');
        return;
      }

      // Store lead locally
      saveLead(email);

      // Show confirmation & next step
      showVipSuccessModal(email);
    });
  }

  function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

  function saveLead(email) {
    try {
      const leads = JSON.parse(localStorage.getItem('scb_vip_leads') || '[]');
      leads.push({ email, timestamp: new Date().toISOString() });
      localStorage.setItem('scb_vip_leads', JSON.stringify(leads));
      console.log('Lead saved locally:', email);
    } catch (err) {
      console.error('Failed to save lead:', err);
    }
  }

  function showVipSuccessModal(email) {
    const modalHtml = `
      <div id="vipModal" style="position: fixed; inset: 0; background: rgba(0,0,0,0.6); display: flex; align-items: center; justify-content: center; z-index: 1000; padding: 20px;">
        <div style="background: #FFFFFF; max-width: 480px; width: 100%; border-radius: 16px; padding: 32px; text-align: center; box-shadow: 0 20px 40px rgba(0,0,0,0.2);">
          <div style="font-size: 3rem; margin-bottom: 12px;">🎉</div>
          <h3 style="font-family: 'Lora', serif; font-size: 1.6rem; color: #1C3F32; margin-bottom: 12px;">VIP Spot Reserved!</h3>
          <p style="color: #5A6065; font-size: 0.95rem; line-height: 1.5; margin-bottom: 24px;">
            We've locked in your <strong>40% off ($199)</strong> reservation for <strong>${escapeHtml(email)}</strong>.<br/><br/>
            When our Kickstarter goes live, you will get early access 1 hour before the public to claim your numbered Founder's Edition board.
          </p>
          <button id="closeModalBtn" style="background: #1C3F32; color: #FFFFFF; padding: 12px 28px; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; font-size: 1rem;">
            Awesome, Got It!
          </button>
        </div>
      </div>
    `;

    document.body.insertAdjacentHTML('beforeend', modalHtml);
    document.getElementById('closeModalBtn').addEventListener('click', () => {
      const m = document.getElementById('vipModal');
      if (m) m.remove();
      vipForm.reset();
    });
  }

  function escapeHtml(str) {
    return str.replace(/[&<>'"]/g, 
      tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
    );
  }

  function playSoftClickSound() {
    try {
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      osc.type = 'triangle';
      osc.frequency.setValueAtTime(440, ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(110, ctx.currentTime + 0.08);

      gain.gain.setValueAtTime(0.15, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.08);

      osc.connect(gain);
      gain.connect(ctx.destination);

      osc.start();
      osc.stop(ctx.currentTime + 0.09);
    } catch (e) {
      // AudioContext might be blocked until user gesture
    }
  }
});

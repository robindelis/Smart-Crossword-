// Crossword Companion Service Worker
// Version 1.0.0

const CACHE_NAME = 'crossword-companion-v1';

const PRECACHE_ASSETS = [
  '/mobile/',
  '/mobile/index.html',
  '/mobile/manifest.json',
  '/mobile/css/mobile.css',
  '/mobile/js/models.js',
  '/mobile/js/board-viewport.js',
  '/mobile/js/game-engine-bridge.js',
  '/mobile/js/firebase-service.js',
  '/mobile/js/audio-recorder.js',
  '/mobile/js/app.js',
  '/mobile/engine.wasm',
  '/mobile/icons/icon-192.png',
  '/mobile/icons/icon-512.png',
  '/mobile/icons/icon.svg'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(PRECACHE_ASSETS).catch((err) => {
        console.warn('Pre-cache warning (some assets might be served dynamically):', err);
      });
    }).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((name) => {
          if (name !== CACHE_NAME) {
            return caches.delete(name);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // Exclude API calls or non-GET requests from cache-first
  if (event.request.method !== 'GET' || url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(event.request).catch(() => {
        return new Response(JSON.stringify({ error: 'Offline', offline: true }), {
          headers: { 'Content-Type': 'application/json' }
        });
      })
    );
    return;
  }

  // Cache-first strategy with network update in background
  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      if (cachedResponse) {
        // Fetch and update cache in background
        fetch(event.request).then((networkResponse) => {
          if (networkResponse && networkResponse.status === 200) {
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(event.request, networkResponse);
            });
          }
        }).catch(() => {/* Ignore network error when offline */});

        return cachedResponse;
      }

      return fetch(event.request).then((networkResponse) => {
        if (!networkResponse || networkResponse.status !== 200) {
          return networkResponse;
        }
        const responseToCache = networkResponse.clone();
        caches.open(CACHE_NAME).then((cache) => {
          cache.put(event.request, responseToCache);
        });
        return networkResponse;
      }).catch(() => {
        // Fallback for HTML navigation
        if (event.request.headers.get('accept') && event.request.headers.get('accept').includes('text/html')) {
          return caches.match('/mobile/index.html');
        }
      });
    })
  );
});

// Push notification event
self.addEventListener('push', (event) => {
  let data = {};
  if (event.data) {
    try {
      data = event.data.json();
    } catch (_) {
      data = { text: event.data.text() };
    }
  }

  const title = data.title || 'Smart Crossword Board';
  const options = {
    body: data.body || data.text || 'A new move was played on your board!',
    icon: '/mobile/icons/icon-192.png',
    badge: '/mobile/icons/icon-192.png',
    vibrate: [100, 50, 100],
    data: {
      url: data.url || '/mobile/',
      gameId: data.gameId
    },
    actions: [
      { action: 'open', title: 'Open Board' },
      { action: 'dismiss', title: 'Dismiss' }
    ]
  };

  event.waitUntil(self.registration.showNotification(title, options));
});

// Notification click event
self.addEventListener('notificationclick', (event) => {
  event.notification.close();

  if (event.action === 'dismiss') {
    return;
  }

  const targetUrl = (event.notification.data && event.notification.data.url) ? event.notification.data.url : '/mobile/';

  event.waitUntil(
    self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientList) => {
      for (const client of clientList) {
        if (client.url.includes('/mobile') && 'focus' in client) {
          return client.focus();
        }
      }
      if (self.clients.openWindow) {
        return self.clients.openWindow(targetUrl);
      }
    })
  );
});

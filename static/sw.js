// TREMHUB Service Worker
const CACHE_NAME = 'tremhub-v1';
const STATIC_ASSETS = [
  '/',
  '/businesses/',
  '/accounts/members/',
  '/static/css/tremhub.css',
  '/static/js/tremhub.js',
  '/static/manifest.json',
];

// Install — cache static assets
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(STATIC_ASSETS).catch(() => {
        // Ignore individual failures during install
      });
    })
  );
  self.skipWaiting();
});

// Activate — clean old caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys
          .filter(key => key !== CACHE_NAME)
          .map(key => caches.delete(key))
      )
    )
  );
  self.clients.claim();
});

// Fetch — network first, fall back to cache
self.addEventListener('fetch', event => {
  // Skip non-GET and admin/media requests
  if (
    event.request.method !== 'GET' ||
    event.request.url.includes('/admin/') ||
    event.request.url.includes('/media/')
  ) return;

  event.respondWith(
    fetch(event.request)
      .then(response => {
        // Cache successful HTML and static responses
        if (response && response.status === 200) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
        }
        return response;
      })
      .catch(() => {
        return caches.match(event.request).then(cached => {
          if (cached) return cached;
          // Offline fallback for HTML pages
          if (event.request.headers.get('accept').includes('text/html')) {
            return caches.match('/');
          }
        });
      })
  );
});

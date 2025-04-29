const CACHE_NAME = 'fitness-tracker-cache-v1';
const urlsToCache = [
  '/',
  '/static/manifest.json',
  '/static/favicon.ico',
  '/static/icon-192x192.png',
  '/static/icon-512x512.png',
  '/static/style.css',
  '/static/script.js',
];

// Включване в cache при инсталиране на service worker
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(urlsToCache);
    })
  );
});

// Използване на cache при опит за мрежово извикване
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request);
    })
  );
});

// Опресняване на cache при обновление на service worker
self.addEventListener('activate', (event) => {
  const cacheWhitelist = [CACHE_NAME];
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (!cacheWhitelist.includes(cacheName)) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

self.addEventListener('push', function(event) {
  const options = {
    body: 'Did you train today?',
    icon: '/static/favicon-32x32.png',
    badge: '/static/favicon-32x32.png',
  };
  event.waitUntil(
    self.registration.showNotification('Fitness Tracker', options)
  );
});

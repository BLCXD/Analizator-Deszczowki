

const CACHE_NAME = 'ad-push-sw-v1';

self.addEventListener('install', (event) => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(self.clients.claim());
});

self.addEventListener('push', (event) => {
  const options = {
    body: 'Nowe dane z czujnika.',
    icon: '/static/images/favicon.png',
    badge: '/static/images/favicon.png',
    vibrate: [200, 100, 200],
    data: { url: '/' },
    requireInteraction: false,
    tag: 'ad-push',
  };

  try {
    if (event.data) {
      const payload = event.data.json();
      if (payload.title) options.title = payload.title;
      if (payload.body) options.body = payload.body;
      if (payload.device_id) {
        options.data = { url: `/devices/${encodeURIComponent(payload.device_id)}` };
        options.tag = `ad-push-${payload.device_id}`;
      }
    } else {
      options.title = 'Analizator Deszczówki';
    }
  } catch (_err) {
    options.title = 'Analizator Deszczówki';
  }

  event.waitUntil(self.registration.showNotification(options.title, options));
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  const url = (event.notification.data && event.notification.data.url) || '/';
  event.waitUntil(
    self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clients) => {
      for (const client of clients) {
        if (client.url.includes(self.location.origin) && 'focus' in client) {
          return client.focus();
        }
      }
      if (self.clients.openWindow) {
        return self.clients.openWindow(url);
      }
      return Promise.resolve();
    })
  );
});

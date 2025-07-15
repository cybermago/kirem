// Em static/js/service-worker.js
self.addEventListener('push', function (event) {
    const data = event.data.json();
    const options = {
        body: data.body,
        icon: data.icon,
        badge: data.icon, // Ícone para Android
        data: {
            url: data.url // Armazena a URL para o clique
        }
    };
    event.waitUntil(
        self.registration.showNotification(data.head, options)
    );
});

self.addEventListener('notificationclick', function (event) {
    event.notification.close();
    event.waitUntil(
        clients.openWindow(event.notification.data.url)
    );
});
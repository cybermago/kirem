// Em static/js/push-notifications.js

// Função para obter o cookie CSRF
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');

// Função para converter a chave pública VAPID
function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
}

// Função principal para se inscrever
async function subscribeUser() {
    if ('serviceWorker' in navigator && 'PushManager' in window) {
        try {
            const registration = await navigator.serviceWorker.register('/static/js/service-worker.js');
            console.log('Service Worker Registrado:', registration);

            const permission = await window.Notification.requestPermission();
            if (permission !== 'granted') {
                console.log('Permissão para notificações não concedida.');
                return;
            }

            const VAPID_PUBLIC_KEY = "{{ VAPID_PUBLIC_KEY }}"; // Esta chave virá do template Django
            const applicationServerKey = urlBase64ToUint8Array(VAPID_PUBLIC_KEY);

            const subscription = await registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: applicationServerKey
            });
            console.log('Usuário inscrito:', subscription);

            // Envia a assinatura para o backend
            await fetch('/webpush/save_information', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify(subscription)
            });
            console.log('Assinatura enviada para o servidor.');

        } catch (error) {
            console.error('Falha ao se inscrever para notificações push:', error);
        }
    }
}

// Chame a função para iniciar o processo de inscrição
// Pode ser chamado no carregamento da página ou ao clicar em um botão "Ativar Notificações"
subscribeUser();
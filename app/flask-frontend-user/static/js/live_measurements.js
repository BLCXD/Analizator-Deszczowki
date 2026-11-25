(() => {
    const selector = document.getElementById('device-select');
    if (!selector) return;

    let socket = null;
    let selectedId = '';

    async function connect(deviceId) {
        selectedId = deviceId;
        if (socket) {
            socket.close();
            socket = null;
        }
        if (!deviceId) return;

        try {
            const response = await fetch('/measurements/api/stream-ticket/' + encodeURIComponent(deviceId), {
                headers: { Accept: 'application/json' },
            });
            const payload = await response.json();
            if (!response.ok) throw new Error(payload.error || 'Brak dostępu do strumienia');
            if (selectedId !== deviceId) return;

            const base = document.body.dataset.wsBase;
            if (!base) throw new Error('Brak konfiguracji podglądu na żywo');
            const url = `${base.replace(/\/$/, '')}/${encodeURIComponent(deviceId)}`;
            socket = new WebSocket(url, ['ad-stream', `ticket.${payload.ticket}`]);
            socket.onmessage = event => {
                try {
                    const reading = JSON.parse(event.data);
                    if (reading.type === 'measurement') {
                        document.dispatchEvent(new CustomEvent('ad:measurement', { detail: reading }));
                    }
                } catch {
                    console.warn('Otrzymano niepoprawne dane podglądu na żywo.');
                }
            };
            socket.onerror = () => console.warn('Podgląd na żywo jest chwilowo niedostępny.');
            socket.onclose = () => { if (socket?.readyState === WebSocket.CLOSED) socket = null; };
        } catch (error) {
            console.warn('Nie udało się uruchomić podglądu na żywo:', error.message);
        }
    }

    selector.addEventListener('change', () => connect(selector.value));
    if (selector.value) connect(selector.value);
})();

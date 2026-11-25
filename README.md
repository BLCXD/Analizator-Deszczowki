# Monorepo — projekt do sprawozdania

Repozytorium zawiera stronę oraz aplikację Analizator Deszczówki:

- `strona-main/` — strona `strona-3d`.
- `app/` — backend, panel, konfiguracja Compose i dokumentacja aplikacji.
- `raspberry/` — agent i pliki wdrożeniowe Raspberry Pi.
- `esp32/` — kod urządzenia ESP32.

Lokalny stos uruchomisz z katalogu `app/` po skopiowaniu `.env.example` do `.env` i uzupełnieniu ustawień:

```sh
cd app
cp .env.example .env
docker-compose up --build
```

Składniki produkcyjne są opisane w `app/docker-compose.production.yml`; wymagają własnych sekretów i domeny. Pliki agenta Raspberry Pi i ESP32 znajdują się w katalogach głównych repozytorium.

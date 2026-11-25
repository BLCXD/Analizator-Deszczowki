# 01_PROJECT_ANALYSIS.md
## Analiza repozytorium, wymagań, backendu i obecnego stanu projektu

## Cel sekcji
Przeanalizowanie struktury repozytorium Analizator Deszczówki (AD), zrozumienie wymagań projektu, ocena aktualnego stanu backendu oraz określenie, co musi zostać zaimplementowane w frontendzie (dashboardzie Flask) aby ukończyć działający system IoT.

## Kontekst i zależności
Ta sekcja stanowi fundament dla wszystkich kolejnych dokumentów. Nie ma zależności od innych sekcji, ale wszystkie kolejne sekcje zależą od wiedzy zawartej w tym dokumencie.

## Stan początkowy
- Katalog `flask-frontend-user` jest pusty (brak plików)
- Backend istnieje w `/home/naukolatek/Desktop/AD/new/backend` jako aplikacja FastAPI
- Istnieją dokumenty projektowe: PROJECT_CONTEXT.md, GOALS.md, PRD.md, PRD_dash.md
- Backend wykorzystuje bazę danych SQLite (test.db)
- API jest dokumentowane w kodzie (endpointy pomiarów, urządzeń, analiz)
- Istnieją podstawowe testy end-to-end i funkcjonalne

## Szczegółowy zakres implementacji
### Analiza struktury repozytorium
1. **Backend** (`/backend/app`):
   - Struktura modułowa: `api/v1`, `core`, `db`, `models`, `schemas`, `services`, `tasks`, `analysis`
   - API wersja v1 zawiera endpointy dla: autoryzacji, urządzeń, pomiarów
   - Pomiarów: tworzenie, pobieranie, najnowsze, trendy, anomalie
   - WebSocket dla streamingu danych na żywo
   - Schematy Pydantic dla walidacji danych

2. **Modele danych** (w `/backend/app/models`):
   - Urządzenia (Device)
   - Pomiarów (Measurement) 
   - Użytkowników (User)
   - Pola pomiarów: water_quality_turbidity, water_quality_ph, ec, temperature, humidity, rainfall

3. **Endpointy API dostępne dla dashboardu**:
   - `POST /api/v1/measurements/` - tworzenie nowego pomiaru
   - `GET /api/v1/measurements/` - lista pomiarów z filtracją
   - `GET /api/v1/measurements/{device_id}/latest` - najnowszy pomiar dla urządzenia
   - `GET /api/v1/measurements/{device_id}` - pomiary dla konkretnego urządzenia
   - `GET /api/v1/measurements/{device_id}/analysis/trends` - trendy pomiarów
   - `GET /api/v1/measurements/{device_id}/analysis/anomalies` - anomalie pomiarów
   - `WebSocket /api/v1/measurements/ws/{device_id}` - streaming danych na żywo

4. **Format danych pomiarowych** (z `/backend/app/schemas/measurement.py`):
   ```json
   {
     "water_quality_turbidity": float (opcjonalne, >0), // faktycznie EC
     "water_quality_ph": float (opcjonalne, 0-14),
     "temperature": float (opcjonalne),
     "rainfall_mm": float (opcjonalne),
     "rainfall_1h_mm": float (opcjonalne),
     "humidity": float (opcjonalne, 0-100),
     "raw_data": string (opcjonalne),
     "measurement_id": string (opcjonalne, dla idempotencji),
     "device_id": string (wymagane, ID zewnętrzne urządzenia)
   }
   ```

5. **Odpowiedzi API**:
   - Pomiar zawiera dodatkowe pola: `id` (int), `device_id` (int - wewnętrzne ID DB), `measurement_time` (datetime), `is_processed` (bool)

### Wymagania techniczne dla frontendzie
- Python Flask jako framework webowy
- HTML5, CSS3, JavaScript (vanilla lub minimalne biblioteki)
- Anime.js dla animacji
- Biblioteka wykresów (do wyboru: Chart.js, D3.js, lub podobna)
- Połączenie z istniejącym backendem API przez HTTP/WebSocket
- Obsługa uwierzytelniania (jeśli wymagane przez backend)
- Responsywny design

### Stan backendu i gotowość do integracji
- Backend działa i udostępnia dokumentowane endpointy
- WebSocket dostępny dla streamingu danych na żywo
- API wymaga uwierzytelniania (tokeny urządzeń lub użytkowników)
- Dane są przechowywane w SQLite bazie danych
- Istnieje podstawowa walidacja danych wejściowych

### Rzeczywiste ograniczenia i założeń
1. **Potwierdzone informacje**:
   - Backend jest implementowany w FastAPI (nie Flask, ale dostępny przez HTTP)
   - API endpointy są dokładnie zdefiniowane w kodzie
   - Format danych pomiarowych jest spójny
   - WebSocket jest implementowany dla streamingu na żywo

2. **Założenia wymagające weryfikacji**:
   - Mechanizm uwierzytelniania dla dashboardu (czy potrzebne są konta użytkowników, czy wystarczy token urządzenia?)
   - Czy backend akceptuje połączenia z dashboardu z tego samego pochodzenia (CORS)
   - Dostępność testowego urządzenia do rozwoju

3. **Nieznane informacje (do ustalenia podczas implementacji)**:
   - Dokładny format odpowiedzi uwierzytelniania
   - Czy istnieją ograniczenia rate limiting na API
   - Czy są wymagane konkretne nagłówki HTTP dla żądań
   - Format danych WebSocket (potwierdzony w kodzie: type, measurement_time, device_id, data z ph, ec, temperature)

### Konkretne zadania do wykonania w kolejnych sekcjach
1. Utworzenie aplikacji Flask z odpowiednią strukturą katalogów
2. Implementacja klienta API komunikującego się z backendem
3. Stworzenie共享 layoutu i nawigacji
4. Implementacja stron dashboardu zgodnie z wymaganiami
5. Dodanie animacji Anime.js i interakcji
6. Implementacja obsługi stanów ładowania, błędów i pustych danych
7. Zapewnienie responsywności i dostępności
8. Dodanie funkcji bezpieczeństwa i niezawodności
9. Napisanie testów jednostkowych i integracyjnych
10. Przygotowanie dokumentacji i konfiguracji wdrożeniowej

### Wymagania techniczne
- Python 3.8+
- Flask
- Requests (do komunikacji HTTP)
- python-socketio lub podobna biblioteka (dla WebSocket, jeśli potrzebna)
- Chart.js lub podobna biblioteka wykresów
- Anime.js
- Variety of development tools (pip, virtual environment)

### Wymagania wizualne
- Profesjonalny wygląd odpowiedni dla aplikacji monitoringu IoT
- Czytelna prezentacja danych pomiarowych
- Intuicyjna nawigacja
- Responsywny układ działający na desktopie i urządzeniach mobilnych
- Subtelne animacje poprawiające UX (nie zastępujące funkcjonalności)

### Pliki, które należy utworzyć lub zmodyfikowane
Wszystkie pliki będą tworzone od podstaw w katalogu `flask-frontend-user`:
- Struktura katalogów aplikacji Flask
- Pliki konfiguracyjne (app.py, config.py, requirements.txt)
- Szablony HTML
- Pliki statyczne (CSS, JavaScript)
- Komponenty i moduły JavaScript

### Integracja z pozostałymi elementami systemu
Frontend będzie:
- Konsumentem istniejącego backend API (nie będzie duplikował logiki backendu)
- Pokazywał rzeczywiste dane z bazy danych przez API
- Używał WebSocket do otrzymywania danych na żywo (jeśli dostępne)
- Nie będzie przechowywał własnej kopii danych (oprócz tymczasowego stanu UI)
- Będzie szanował architekturę systemu: czujniki → ESP32 → Raspberry Pi → backend → dashboard

### Obsługa błędów i przypadków brzegowych
- Brak połączenia z backendem
- Nieprawidłowe odpowiedzi API (błędy 4xx, 5xx)
- Puste stany (brak danych do wyświetlenia)
- Częściowe dane (niektóre pola pomiarów brakujące)
- Problemy z WebSocket (rozłączenia, próby ponownego połączenia)
- Nieprawidłowe lub przestarzałe dane
- Brak uprawnień dostępu do określonych urządzeń

### Testy wymagane do uznania sekcji za ukończoną
- Sprawdzenie, że wszystkie wymagane dokumenty projektu zostały przeczytane i zrozumiane
- Weryfikacja, że analizowano rzeczywisty kod backendu (nie wymyślano funkcjonalności)
- Potwierdzenie, że zrozumiano rzeczywiste endpointy i formaty danych
- Dokumentacja wszystkich założeń i niepewności wymagających weryfikacji podczas implementacji

### Jednoznaczne kryteria akceptacji
- Dokument zawiera dokładną analizę rzeczywistej struktury backendu
- Wymienione są wszystkie dostępne endpointy API z ich metodami, parametrami i formatami odpowiedzi
- Zidentyfikowane są luki w wiedzy wymagające wyjaśnienia podczas implementacji
- Analiza jest zgodna z rzeczywistym stanem repozytorium (nie zawiera wymyślonych funkcjonalności)

### Zależności od innych sekcji
Ta sekcja nie ma zależności, ale jest wymaganiem wstępnym dla wszystkich innych sekcji.

### Warunki zakończenia prac
Uznać sekcję za ukończoną gdy:
- Wszystkie wymienione powyżej elementy analizy zostały wykonane
- Dokument zawiera konkretne informacje o backendzie oparte na rzeczywistym kodzie
- Zidentyfikowano rzeczywiste endpointy i formaty danych
- Zanotowano wszystkie niepewności wymagające weryfikacji

### Informacje, które należy przekazać do kolejnych sekcji
- Rzeczywiste endpointy API i ich specyfikacje
- Formaty danych żądań i odpowiedzi
- Mechanizm uwierzytelniania (jeśli ustalony)
- Dostępność WebSocket do streamingu danych
- Struktura modeli danych w backendzie
- Jakiekolwiek ograniczenia lub specjalne wymagania API

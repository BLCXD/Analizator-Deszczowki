# 06_BACKEND_INTEGRATION.md
## Klient API, rzeczywiste endpointy, walidacja odpowiedzi, timeouty, obsługa błędów i mapowanie danych

## Cel sekcji
Zaimplementowanie warstwy komunikacji z backendem Analizator Deszczówki, która zapewni bezpieczne i niezawodne pobieranie oraz wysyłanie danych poprzez zdefiniowane endpointy API. Sekcja skupia się na stworzeniu klienta HTTP, obsłudze odpowiedzi, błędów oraz mapowaniu danych na formaty używane w frontendzie.

## Kontekst i zależności
Ta sekcja zależy od:
- 01_PROJECT_ANALYSIS.md (zrozumienie rzeczywistych endpointów i formatów danych)
- 04_ENVIRONMENT_AND_CONFIGURATION.md (zmienne środowiskowe i konfiguracja)
Nie ma zależności od innych sekcji implementacyjnych, ale jest wymagana dla wszystkich sekcji, które potrzebują danych z backendu (08, 09, 10, 11).

## Stan początkowy
- Katalog `flask-frontend-user` jest pusty lub zawiera tylko podstawową strukturę Flaska (zależnie od postępu w 05_FLASK_FOUNDATION.md)
- Brak istniejącego klienta API
- Brak zdefiniowanych funkcji do komunikacji z backendem
- Dostępna dokumentacja backendowa w kodzie (endpointy w `/backend/app/api/v1/`)

## Szczegółowy zakres implementacji
### 1. Klient HTTP
- Utworzenie centralnego modułu `app/services/api_client.py` odpowiedzialnego za wszystkie żądania HTTP do backendu
- Konfiguracja klienta z:
  - Bazowym URL pobranym ze zmiennej środowiskowej `API_BASE_URL` (domyślnie `http://localhost:8000`)
  - Timeoutami żądań (np. 10 sekund dla połączenia, 30 sekund dla odpowiedzi)
  - Automatycznym dodawaniem nagłówka `Authorization: Bearer <token>` po uwierzytelnieniu
  - Obsługą odświeżania tokenu (jeśli backend wymaga)
  - Rejestrowaniem żądań i odpowiedzi w trybie debugowym

### 2. Endpointy API do zaimplementowania
Na podstawie analizy backendu (`/backend/app/api/v1/`), zaimplementować funkcje dla następujących endpointów:

#### Uwierzytelnianie (`/api/v1/auth`)
- `POST /register` - rejestracja nowego użytkownika
- `POST /login` - logowanie i otrzymanie tokenu dostępu
- `GET /me` - pobranie informacji o zalogowanym użytkowniku
- `DELETE /me` - wylogowanie (usunięcie tokenu po stronie klienta)
- `POST /device/login` - logowanie urządzenia (dla ESP32, nie używane w dashboardzie)
- `POST /device/{device_id}/code` - wysyłanie kodu do urządzenia

#### Urządzenia (`/api/v1/devices`)
- `GET /` - pobranie listy wszystkich urządzeń użytkownika
- `GET /{device_id}` - pobranie szczegółów jednego urządzenia
- `POST /` - utworzenie nowego urządzenia
- `PUT /{device_id}` - aktualizacja urządzenia
- `DELETE /{device_id}` - usunięcie urządzenia
- `POST /{device_id}/heartbeat` - symulacja heartbeat (opcjonalnie)
- `POST /pair` - parowanie nowego urządzenia
- `POST /auth` - uwierzytelnianie urządzenia przez kod

#### Pomiaru (`/api/v1/measurements`)
- `GET /` - pobranie listy pomiarów (z filtrowaniem przez device_id, czas, limit)
- `GET /{device_id}/latest` - pobranie najnowszego pomiaru dla urządzenia
- `GET /{device_id}` - pobranie wszystkich pomiarów dla konkretnego urządzenia
- `POST /` - utworzenie nowego pomiaru (zazwyczaj przez ESP32, nie bezpośrednio w dashboardzie)
- `GET /{device_id}/analysis/trends` - analiza trendów pomiarów
- `GET /{device_id}/analysis/anomalies` - wykrywanie anomalii w pomiarach

### 3. Walidacja odpowiedzi
- Sprawdzenie kodów statusu HTTP i rzucanie odpowiednich wyjątków
- Walidacja struktury JSON odpowiedzi przeciwko zdefiniowanym schematom (używając biblioteki takich jak `pydantic` lub ręczna walidacja)
- Obsługa odpowiedzi pól opcjonalnych i wartości null
- Konwersja dat ISO 8601 na obiekty `datetime` JavaScript (lub odpowiedniki w Pythonie dla szablonów)

### 4. Obsługa błędów
- Obsługa błędów sieciowych (timeout, brak połączenia)
- Obsługa błędów HTTP 4xx (np. 401 Nieautoryzowany, 403 Zabroniono, 404 Nie znaleziono, 422 Nieprzetwarzalny encja)
- Obsługa błędów HTTP 5xx (błędy serwera)
- Centralizacja obsługi błędów w module API Client
- Propagowanie błędów do warstwy prezentacji poprzez zwracanie obiektów błędów lub rzucanie wyjątków
- Obsługa przypadku, gdy backend jest niedostępny (pokazanie komunikatu użytkownikowi)

### 5. Mapowanie danych
- Mapowanie odpowiedzi backendowych na formaty używane w komponentach frontendowych
- Przykłady mapowań:
  - Measurement: mapowanie pól takich jak `timestamp`, `ph`, `turbidity`, `flow_rate`, `temperature` na odpowiednie typy
  - Device: mapowanie `id`, `name`, `location`, `status`, `last_seen`
  - Auth: mapowanie tokenu i danych użytkownika
- Konwersja jednostek (jeśli backend zwraca w innych jednostkach niż oczekiwane w frontendzie)
- Formatowanie danych do wyświetlania (np. daty, liczby)

### 6. Bezpieczeństwo
- Przechowywanie tokenu dostępu w bezpieczny sposób (np. w sesji Flaska, nie w localStorage ze względu na ryzyko XSS - ale uwaga: Flask tradycyjnie używa sesji po stronie serwera, więc token może być przechowywany w sesji serwerowej)
- W tym projekcie (Flask z renderowaniem po stronie serwera) zaleca się przechowywanie tokenu w sesji serwerowej.
- Implementacja odświeżania tokenu (jeśli backend wspiera odświeżanie)
- Wylogowanie poprzez wyczyszczenie sesji

## Konkretne zadania do wykonania
1. Utworzyć katalog `app/services/` jeśli nie istnieje
2. Utworzyć plik `app/services/api_client.py` z klasą `APIClient`
3. Zaimplementować metody dla każdego z endpointów wymienionych powyżej
4. Dodajić obsługę błędów i timeoutów
5. Zaimplementować funkcje pomocnicze do mapowania danych
6. Utworzyć plik `app/services/auth_service.py` zarządzający uwierzytelnianiem (opcjonalnie, można zintegrować z APIClient)
7. Zaktualizować konfigurację w `app/config.py` lub podobnym, aby zawierała ustawienia API
8. Napisać jednostkowe testy dla modułu API Client (zobacz sekcję 17)

## Wymagania techniczne
- Biblioteka `requests` do wykonywania żądań HTTP (lub `httpx` jeśli preferujemy asynchroniczność, ale Flask tradycyjnie jest synchroniczny)
- Biblioteka `python-dotenv` do ładowania zmiennych środowiskowych (jeśli jeszcze nie używana)
- Biblioteka do walidacji danych (np. `pydantic` lub `marshmallow`) - opcjonalnie, można zrobić ręczną walidację
- Zmienne środowiskowe:
  - `API_BASE_URL`: podstawowy URL backendowego API
  - `API_TIMEOUT_CONNECT`: timeout połączenia (sekundy)
  - `API_TIMEOUT_READ`: timeout odczytu (sekundy)

## Wymagania wizualne
Brak bezpośrednich wymagań wizualnych dla tej sekcji.

## Pliki, które należy utworzyć lub zmodyfikować
- `app/services/api_client.py` - nowy plik
- `app/services/auth_service.py` - nowy plik (opcjonalnie)
- `app/config.py` - modyfikacja (jeśli istnieje) lub utworzenie nowego pliku konfiguracji
- `.env` - dodanie przykładowych zmiennych środowiskowych (jeśli jeszcze nie istnieje)
- `requirements.txt` - dodanie wymaganych bibliotek

## Integrację z pozostałymi elementami systemu
- Moduł API Client będzie używany przez:
  - Sekcję 07 (Shared Layout) do sprawdzania stanu uwierzytelniania w nagłówku
  - Sekcję 08 (Dashboard Overview) do pobierania aktualnych pomiarów
  - Sekcję 09 (Measurements and History) do pobierania listy pomiarów
  - Sekcję 10 (Charts and Analytics) do pobierania danych do wykresów
  - Sekcję 11 (Device Status) do pobierania informacji o urządzeniach
  - Sekcję 12 (Settings) do aktualizacji ustawień użytkownika i urządzeń
  - Sekcję 16 (Security) do weryfikacji tokenu i obsługi wylogowania

## Obsługę błędów i przypadków brzegowych
- Brak połączenia z backendem: pokazanie komunikatu o problemach z połączeniem i możliwość ponowienia próby
- Nieprawidłowe dane w odpowiedzi: logowanie błędu i pokazanie komunikatu o problemie technicznym
- Token wygasł lub nieważny: automatyczne przekierowanie do strony logowania
- Odpowiedź z kodem 429 (Too Many Requests): implementacja prostego mechanizmu retry z opóźnieniem
- Częściowe dane w odpowiedzi: radzenie sobie z brakującymi polami poprzez wartości domyślne lub puste
- Duże zestawy danych: implementacja paginacji lub lazy loading w zależności od potrzeb

## Testy wymagane do uznania sekcji za ukończoną
- Jednostkowe testy dla modułu `api_client.py` symulujące różne odpowiedzi API (sukces, błędy 4xx, 5xx, timeout)
- Testy integracyjne sprawdzające rzeczywistą komunikację z backendem (jeśli dostępny w środowisku testowym)
- Testy obsługi błędów sieciowych
- Testy walidacji danych i mapowania

## Jednoznaczne kryteria akceptacji
- Klient API pomyślnie łączy się z backendem i pobiera dane z wszystkich wymienionych endpointów
- Odpowiedzi są poprawnie walidowane i mapowane na używane w frontendzie formaty danych
- Błędy są obsługiwane w sposób zgodny z zasadami sekcji 16 (Security and Reliability)
- Token uwierzytelniania jest prawidłowo przesyłany w nagłówkach żądań
- Moduł jest łatwy w użyciu przez inne części aplikacji poprzez prosty interfejs API

## Zależności od innych sekcji
- Zależna od: 01_PROJECT_ANALYSIS.md, 04_ENVIRONMENT_AND_CONFIGURATION.md
- Wymagana przez: 07_SHARED_LAYOUT_AND_NAVIGATION.md, 08_DASHBOARD_OVERVIEW.md, 09_MEASUREMENTS_AND_HISTORY.md, 10_CHARTS_AND_ANALYTICS.md, 11_DEVICE_STATUS_AND_DIAGNOSTICS.md, 12_SETTINGS_AND_ADDITIONAL_FEATURES.md

## Warunki zakończenia prac
- Plik `app/services/api_client.py` jest w pełni zaimplementowany i przetestowany
- Wszystkie funkcje klienta API są pokryte testem jednostkowym z symulowanymi odpowiedziami
- Dokumentacja w kodzie jest wystarczająca dla innych programistów
- Sekcja może być uznana za ukończoną po pozytywnej weryfikacji przez lead developer lub poprzez automated tests

## Informacje, które należy przekazać do kolejnych sekcji
- Interfejs modułu `APIClient` (dostępne metody i ich sygnatury)
- Formaty danych zwracane przez funkcje API (po mapowaniu)
- Sposób obsługi błędów i wyjątków
- Informacje o konfiguracji (zmienne środowiskowe)
- Przykłady użycia klienta API w kontrolerach lub widokach

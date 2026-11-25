# 17_UNIT_AND_INTEGRATION_TESTS.md
## Testy jednostkowe, integracyjne, mockowanie API i weryfikacja obsługi błędów

## Cel sekcji
Zaimplementowanie kompleksowej strategii testowania dla aplikacji Flask dashboardu, obejmującej testy jednostkowe poszczególnych komponentów, testy integracyjne sprawdzające współpracę modułów oraz symulację różnych scenariuszy včetně błędów i warunków brzegowych. Sekcja zapewnia, że kod jest niezawodny, łatwy w utrzymaniu i że zmiany nie wprowadzają regresji.

## Kontekst i zależności
Ta sekcja zależy od:
- 01_PROJECT_ANALYSIS.md (zrozumienie wymagań projektu)
- 02_ARCHITECTURE.md (wzorzec architektoniczny)
- 03_DESIGN_SYSTEM.md (do testowania komponentów UI)
- 04_ENVIRONMENT_AND_CONFIGURATION.md (do konfiguracji środowiska testowego)
- Wszystkie poprzednie sekcje implementacyjne (05-16) ponieważ testujemy ich implementację
Nie ma zależności od innych sekcji implementacyjnych, ale jest wymagana przed uznaniem jakiejkolwiek sekcji za ukończoną poprzez testy.

## Stan początkowy
- Katalog `flask-frontend-user` zawiera podstawową strukturę Flaska
- Brak istniejącego katalogu testów
- Brak zdefiniowanej strategii testowania
- Brak skonfigurowanych narzędzi testowych

## Szczegółowy zakres implementacji
### 1. Strategia testowania
- **Testy jednostkowe**: testowanie najmniejszych jednostek kodu (funkcje, metody klas) w izolacji
- **Testy integracyjne**: testowanie współpracy między modułami (np. kontroler → usługa → klient API)
- **Testy end-to-end** (opcjonalnie, zobacz sekcję 18): testowanie całych przepływów użytkownika
- **Mockowanie**: symulowanie zależności zewnętrznych (backend API, bazy danych, usługi zewnętrzne)
- **Testy parametrizowane**: testowanie tej samej logiki z różnymi danymi wejściowymi
- **Testy przypadków brzegowych**: testowanie niezwykłych lub ekstremalnych sytuacji

### 2. Struktura katalogu testów
- Utworzenie katalogu `tests/` w głównym katalogu projektu
- Struktura katalogu:
  ```
  tests/
  ├── unit/                 # Testy jednostkowe
  │   ├── test_api_client.py
  │   ├── test_auth_service.py
  │   ├── test_controllers/
  │   ├── test_services/
  │   └── test_utils/
  ├── integration/          # Testy integracyjne
  │   ├── test_dashboard_flow.py
  │   ├── test_device_management.py
  │   └── test_auth_flow.py
  ├── fixtures/             # Dane testowe i funkcje pomocnicze
  │   ├── mock_data.py
  │   └── conftest.py
  └── utils/                # Funkcje pomocnicze do testów
      └── test_helpers.py
  ```

### 3. Narzędzia i biblioteki testowe
- **Pytest** - główny framework testowy dla Pythona
- **Pytest-mock** lub **unittest.mock** - do mockowania zależności
- **Pytest-fixtures** - do zarządzania danymi testowymi
- **Pytest-cov** - do mierzenia pokrycia kodu testami
- **Pytest-html** - do generowania raportów HTML z wynikami testów
- **Factory Boy** lub podobna - do generowania obiektów testowych
- **Requests-mock** lub **HTTMock** - do mockowania żądań HTTP do backendu

### 4. Testy jednostkowe
Testy jednostkowe będą tworzone dla:
- **Modułu API Client** (sekcja 06):
  - Testowanie metod pobierania danych z różnymi odpowiedziami (sukces, błędy 4xx, 5xx)
  - Testowanie mechanizmu timeoutów
  - Testowanie mechanizmu ponawiania
  - Testowanie walidacji odpowiedzi
  - Testowanie mapowania danych
- **Usług i helperów**:
  - Testowanie funkcji formatowania danych
  - Testowanie funkcji walidacji wejścia
  - Testowanie funkcji pomocniczych UI
- **Kontrolerów**:
  - Testowanie logiki kontrolerów bez zależności od Flaska (gdzie to możliwe)
  - Testowanie dekoratorów i middleware
- **Komponentów i funkcji pomocniczych**:
  - Testowanie funkcji pomocniczych szablonów (Jeśli używamy własnych filtrów Jinja2)

### 5. Testy integracyjne
Testy integracyjne będą tworzone dla:
- **Przepływów uwierzytelniania**:
  - Testowanie pełnego cyklu logowania → dostęp do chronionych zasobów → wylogowanie
  - Testowanie obsługi wygasłych tokenów
  - Testowanie obsługi błędów uwierzytelniania
- **Integracji z backendem**:
  - Testowanie pobierania listy urządzeń i pomiarów
  - Testowanie tworzenia aktualizowania i usuwania urządzeń
  - Testowanie pobierania danych pomiarowych z filtrami
  - Testowanie obsługi błędów połączenia z backendem
- **Przepływów specyficznych dla funkcjonalności**:
  - Testowanie przepływu tworzenia nowego urządzenia od wypełnienia formularza po zapis w backendzie
  - Testowanie przepływu filtrowania danych pomiarowych
  - Testowanie przepływu ładowania i renderowania wykresów
- **Integracji warstw**:
  - Testowanie kontrolerów → usług → klient API
  - Testowanie usług → klient API → przetwarzanie odpowiedzi

### 6. Mockowanie API i zależności zewnętrznych
- **Mockowanie klienta API**:
  - Symulowanie różnych odpowiedzi HTTP (200, 401, 404, 500, timeout)
  - Symulowanie różnych formatów danych JSON
  - Symulowanie opóźnień w odpowiedziach
- **Mockowanie zależności wewnętrznych**:
  - Mockowanie usług przy testowaniu kontrolerów
  - Mockowanie kontrolerów przy testowaniu usług (rzadziej)
- **Użycie fixture'ów**:
  - Fixtures dla danych testowych urządzeń
  - Fixtures dla danych testowych pomiarów
  - Fixtures dla danych testowych użytkowników
  - Fixtures dla konfiguracji aplikacji

### 7. Testowanie obsługi błędów
- **Błędy połączenia**:
  - Symulowanie braku połączenia z backendem
  - Symulowanie timeoutów połączenia
  - Symulowanie nieprawidłowych odpowiedzi (nie JSON)
- **Błędy HTTP**:
  - Symulowanie błędów 400, 401, 403, 404, 422, 500, 502, 503
  - Testowanie odpowiednich komunikatów użytkownikowi
  - Testowanie mechanizmów ponawiania (gdzie stosowane)
- **Błędy walidacji**:
  - Testowanie formularzy z nieprawidłowymi danymi
  - Testowanie komunikatów walidacji przy polach
  - Testowanie obsługi braku wymaganych pól
- **Błędy stanu aplikacji**:
  - Testowanie stanów ładowania, pustych danych, błędów
  - Testowanie przejść między stanami

### 8. Środowisko i konfiguracja testów
- **Konfiguracja środowiska testowego**:
  - Oddzielna konfiguracja dla testów (różne zmienne środowiskowe)
  - Użycie fikcyjnych wartości dla kluczy tajnych i tokenów
  - Konfiguracja aplikacji w trybie testowym
- **Izolation testów**:
  - Każdy test powinien być niezależny
  - Czyszczenie stanu między testami (baza danych, pliki, etc.)
  - Unikanie skutków ubocznych między testami
- **Raportowanie i pokrycie**:
  - Generowanie raportów z wynikami testów
  - Mierzenie pokrycia kodu testami
  - Ustawianie minimalnego progu pokrycia (np. 80% dla krytycznych ścieżek)

### 9. Continuous Integration (opcjonalnie)
- Przygotowanie do integracji z systemami CI (GitHub Actions, GitLab CI, etc.)
- Skrypty uruchamiające testy w izolowanym środowisku
- Buforowanie зависимостей dla szybszych uruchomień
- Artefakty testowe (logi, raporty, zrzuty ekranu)

## Konkretne zadania do wykonania
1. Utworzyć strukturę katalogu testów jak opisano powyżej
2. Utworzyć plik konfiguracyjny pytest (`pytest.ini` lub `pyproject.toml`)
3. Zainstalować wymagane biblioteki testowe i dodać je do `requirements-dev.txt` lub podobnego
4. Utworzyć przykładowe fixture'i dla danych testowych
5. Napisać testy jednostkowe dla modułu API Client (sekcja 06)
6. Napisać testy jednostkowe dla usług i funkcji pomocniczych
7. Napisać testy jednostkowe dla kontrolerów (gdzie to możliwe bez pełnego kontekstu Flaska)
8. Napisać testy integracyjne dla przepływów uwierzytelniania
9. Napisać testy integracyjne dla integracji z backendem
10. Napisać testy integracyjne dla konkretnych przepływów funkcjonalności
11. Zaimplementować mechanizm mockowania żądań HTTP do backendu
12. Napisać testy przypadków brzegowych i obsługi błędów
13. Skonfigurować mierzenie pokrycia kodu testami
14. Utworzyć skrypt uruchamiający wszystkie testy z odpowiednimi opcjami
15. Dodawać odpowiednie komentarze w kodzie testowym wskające co jest testowane
16. Regularnie uruchamiać testy podczas rozwoju aby zapobiec regresjom

## Wymagania techniczne
- Pytest jako główny framework testowy
- Biblioteki do mockowania (pytest-mock, unittest.mock, requests-mock)
- Biblioteki do generowania danych testowych (Factory Boy, faker lub własna implementacja)
- Biblioteki do pomiaru pokrycia (pytest-cov)
- Opcjonalnie: biblioteki do raportowania (pytest-html)
- Zmienne środowiskowe dla konfiguracji testowej:
  - `FLASK_ENV=testing`
  - `TESTING=True`
  - `SECRET_KEY=test-secret-key-for-testing-purposes-only`
  - `WTF_CSRF_ENABLED=False` (wyłącz CSRF w testach dla łatwiejszego testowania formularzy)
  - `API_BASE_URL=http://mock-backend:8000` (lub podobny do mockowania)
  - `API_TIMEOUT_CONNECT=1`
  - `API_TIMEOUT_READ=1`

## Wymagania wizualne
Brak bezpośrednich wymagań wizualnych dla tej sekcji.

## Pliki, które należy utworzyć lub zmodyfikować
- `pytest.ini` lub `pyproject.toml` - konfiguracja pytest
- `requirements-dev.txt` - dodatkowe wymagania dla rozwoju i testów
- `tests/unit/test_api_client.py` - testy jednostkowe dla klienta API
- `tests/unit/test_auth_service.py` - testy jednostkowe dla usługi uwierzytelniania (jeśli istnieje)
- `tests/unit/test_controllers/` - katalog z testami jednostkowymi kontrolerów
- `tests/unit/test_services/` - katalog z testami jednostkowymi usług
- `tests/unit/test_utils/` - katalog z testami jednostkowymi funkcji pomocniczych
- `tests/integration/test_auth_flow.py` - testy integracyjne dla przepływu uwierzytelniania
- `tests/integration/test_dashboard_flow.py` - testy integracyjne dla przepływu dashboardu
- `tests/integration/test_device_management.py` - testy integracyjne dla zarządzania urządzeniami
- `tests/fixtures/mock_data.py` - mockowane dane testowe
- `tests/fixtures/conftest.py` - konfiguracja fixture'ów pytest
- `tests/utils/test_helpers.py` - funkcje pomocnicze do testów

## Integrację z pozostałymi elementami systemu
- Testy będą weryfikować poprawność implementacji wszystkich poprzednich sekcji:
  - Sekcję 05 (Flask Foundation) - podstawowa funkcjonalność aplikacji
  - Sekcję 06 (Backend Integration) - komunikacja z backendem
  - Sekcję 07 (Shared Layout) - renderowanie layoutu i komponentów
  - Sekcję 08 (Dashboard Overview) - funkcjonalność strony głównej
  - Sekcję 09 (Measurements and History) - funkcjonalność historii pomiarów
  - Sekcję 10 (Charts and Analytics) - funkcjonalność wykresów i analizy
  - Sekcję 11 (Device Status and Diagnostics) - funkcjonalność statusu urządzeń
  - Sekcję 12 (Settings and Additional Features) - funkcjonalność ustawień
  - Sekcję 13 (AnimeJS and Interactions) - obecność i działanie animacji (testy integracyjne)
  - Sekcję 14 (Loading, Empty, Error States) - poprawne wyświetlanie stanów
  - Sekcję 15 (Responsiveness and Accessibility) - odpowiedzialność i dostępność (testy integracyjne)
  - Sekcję 16 (Security and Reliability) - środki bezpieczeństwa i niezawodności

## Obsługę błędów i przypadków brzegowych
- Testy które zależą od zewnętrznych zasobów: użycie mocków aby uniknąć zależności od dostępności backendu podczas testów
- Testy które są czasochłonne: oznaczenie jako wolne i możliwość wykluczenia przy szybkim uruchamianiu
- Testy które wymagają określonej konfiguracji: użycie fixture'ów które konfigurują środowisko odpowiednio
- Testy które mogą mieć skutki uboczne: zapewnienie czyszczenia po teście
- Konflikt między szybkością a dokładnością testów: balans między kompleksowym testowaniem a czasem uruchamiania

## Testy wymagane do uznania sekcji za ukończoną
- Co najmniej jeden test jednostkowy dla każdego krytycznego modułu (API Client, usługi uwierzytelniania, główne kontrolery)
- Co najmniej jeden test integracyjny dla każdego głównego przepływu funkcjonalności (uwierzytelnianie, zarządzanie urządzeniami, pobieranie pomiarów)
- Testy przypadków brzegowych dla obsługi błędów (połączenie, timeouty, nieprawidłowe odpowiedzi)
- Testy które sprawdzają obecność i działanie wymaganych mechanizmów (CSRF, walidacja, escapowanie)
- Testy które można uruchomić w izolowanym środowisku bez dostępu do rzeczywistego backendu

## Jednoznaczne kryteria akceptacji
- Struktura katalogu testów jest utworzona i zawiera przykładowe testy
- Testy jednostkowe są tworzone dla krytycznych modułów i usług
- Testy integracyjne są tworzone dla głównych przepływów funkcjonalności
- Testy obsługi błędów są tworzone dla różnych scenariuszy awarii
- Testy można uruchomić za pomocą jednej komendy (np. `pytest`)
- Sekcja może być uznana za ukończoną po pozytywnej weryfikacji przez lead developer lub poprzez automated tests

## Zależności od innych sekcji
- Zależna od: wszystkie poprzednie sekcje (01-16) ponieważ testujemy ich implementację
- Wymagana przez: sekcja 18 (Browser Testing and Visual QA) która może budować na tych testach
- Jednak przed uznaniem jakiejkolwiek sekcji implementacyjnej (05-16) za ukończoną, należy mieć odpowiednie testy z tej sekcji

## Warunki zakończenia prac
- Struktura katalogu testów jest utworzona
- Testy jednostkowe są napisane dla krytycznych komponentów
- Testy integracyjne są napisane dla głównych przepływów funkcjonalności
- Testy można uruchomić i przechodzą w izolowanym środowisku
- Sekcja może być uznana za ukończoną po pozytywnej weryfikacji przez lead developer lub poprzez automated tests

## Informacje, które należy przekazać do kolejnych sekcji
- Struktura katalogu testów i sposób organizacji testów
- Przykłady użycia fixture'ów i mocków
- Przykłady testów jednostkowych dla różnych typów komponentów
- Przykłady testów integracyjnych dla różnych przepływów funkcjonalności
- Informacje o uruchamianiu testów (komenda, opcje, środowisko)
- Informacje o mierzeniu pokrycia kodu testami
- Przykłady testów przypadków brzegowych i obsługi błędów

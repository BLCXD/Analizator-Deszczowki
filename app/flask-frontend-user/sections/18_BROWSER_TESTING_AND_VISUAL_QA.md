# 18_BROWSER_TESTING_AND_VISUAL_QA.md
## Testy przeglądarkowe, Playwright, weryfikacja UI, konsola, błędy HTTP i poprawki wizualne

## Cel sekcji
Zaimplementowanie kompleksowego testowania przeglądarkowego i weryfikacji jakości wizualnej dla aplikacji Flask dashboardu, obejmującego testy end-to-end symulujące rzeczywiste zachowanie użytkownika, weryfikację interfejsu użytkownika, sprawdzanie błędów w konsoli oraz testy regresji wizualnej. Sekcja zapewnia, że aplikacja działa poprawnie w rzeczywistych przeglądarkach i spełnia wymagania dotyczące wyglądu i interakcji.

## Kontekst i zależności
Ta sekcja zależy od:
- 01_PROJECT_ANALYSIS.md (zrozumienie wymagań projektu)
- 02_ARCHITECTURE.md (wzorzec architektoniczny)
- 03_DESIGN_SYSTEM.md (do weryfikacji zgodności z design systemem)
- 04_ENVIRONMENT_AND_CONFIGURATION.md (do konfiguracji środowiska testowego)
- Wszystkie poprzednie sekcje implementacyjne (05-17) ponieważ testujemy ich implementację w przeglądarce
- Sekcja 17 (Unit and Integration Tests) jako uzupełnienie - testy przeglądarkowe skupiają się na aspektach których nie można łatwo przetestować jednostkowo
Nie ma zależności od innych sekcji implementacyjnych, ale jest wymagana przed uznaniem jakiejkolwiek sekcji implementacyjnej za ukończoną poprzez weryfikację w przeglądarce.

## Stan początkowy
- Katalog `flask-frontend-user` zawiera podstawową strukturę Flaska
- Brak istniejącego katalogu testów przeglądarkowych
- Brak zdefiniowanej strategii testowania przeglądarkowego
- Brak skonfigurowanych narzędzi do testowania przeglądarkowego

## Szczegółowy zakres implementacji
### 1. Strategia testowania przeglądarkowego
- **Testy end-to-end (E2E)**: symulowanie rzeczywistych ścieżek użytkownika przez całą aplikację
- **Testy interakcji komponentów**: weryfikacja zachowania poszczególnych komponentów UI
- **Testy regresji wizualnej**: porównywanie zrzutów ekranu w celu wykrycia niezamierzonych zmian w wyglądzie
- **Testy dostępności**: weryfikacja zgodności ze standardami dostępności w rzeczywistym środowisku
- **Testy wydajności**: mierzenie czasu ładowania i interakcji
- **Testy konsoli**: sprawdzanie braków błędów JavaScript i ostrzeżeń
- **Testy sieci**: weryfikacja poprawnych żądań HTTP i obsługi odpowiedzi

### 2. Wybór narzędzi do testowania przeglądarkowego
Zaleca się użycie **Playwright** ze względu na:
- Szybkie i niezawodne wykonywanie testów
- Wsparcie dla wielu przeglądarek (Chromium, Firefox, WebKit)
- Wbudowane możliwości śledzenia i debugowania
- Dostępność API do przechwytywania konsoli i żądań sieciowych
- Dobra integracja z systemami CI

Alternatywy:
- Cypress (dobry ale ograniczone wsparcie dla wielu przeglądarek)
- Selenium (bardziej rozwinięty ale wolniejszy i bardziej skomplikowany w konfiguracji)
- Puppeteer (dobry dla Chromium ale ograniczony dla innych przeglądarek)

### 3. Struktura katalogu testów przeglądarkowych
- Utworzenie katalogu `tests/e2e/` lub `tests/browser/` w głównym katalogu projektu
- Struktura katalogu:
  ```
  tests/e2e/
  ├── pages/                 # Page Object Model - reprezentacje stron
  │   ├── login_page.py
  │   ├── dashboard_page.py
  │   ├── measurements_page.py
  │   ├── analytics_page.py
  │   ├── devices_page.py
  │   └── settings_page.py
  ├── tests/                 # Rzeczywiste testy
  │   ├── test_auth_flow.py
  │   ├── test_dashboard_navigation.py
  │   ├── test_measurements_filtering.py
  │   ├── test_device_management.py
  │   ├── test_analytics_interactions.py
  │   └── test_settings_updates.py
  ├── fixtures/              # Dane testowe i funkcje pomocnicze
  │   ├── test_credentials.py
  │   └── test_data.py
  └── utils/                 # Funkcje pomocnicze do testów
      ├── browser_helpers.py
      └── assert_helpers.py
  ```

### 4. Page Object Model (POM)
- Implementacja wzorca Page Object Model dla lepszej utrzymywalności testów
- Każda strona lub znaczący komponent ma swoją klasę Page Object
- Klasy Page Object encapsulują:
  - Selektory elementów
  - Metody interakcji (kliknięcie, wypełnianie formularzy, etc.)
  - Metody weryfikacji (sprawdzanie obecności tekstu, wartości, etc.)
- Korzyści: zmniejszenie duplikacji kodu, łatwiejsza aktualizacja przy zmianach UI

### 5. Konkretne scenariusze testowe
Testy end-to-end będą obejmować:

#### Przepływ uwierzytelniania
- Testowanie pełnego cyklu: odwiedzenie strony logowania → wypełnienie formularza → przesłanie → weryfikacja przekierowania → dostęp do chronionych stron → wylogowanie
- Testowanie przypadków błędów: nieprawidłowe hasło, nieistniejący użytkownik, wygasła sesja
- Testowanie funkcji "pamiętaj mnie" jeśli implementowana

#### Nawigacja i podstawowa funkcjonalność
- Testowanie że wszystkie elementy nawigacji prowadzą do odpowiednich stron
- Testowanie że aktywny element nawigacji jest prawidłowo wyróżniony
- Testowanie responsywności na różnych szerokościach ekranu (symulowanie różnych urządzeń)
- Testowanie nawigacji klawiaturą (Tab, Enter, Escape)

#### Funkcjonalność dashboardu (sekcja 08)
- Testowanie że strona główna ładuje się poprawnie
- Testowanie wyświetlania informacji o użytkowniku
- Testowanie wyświetlania listy urządzeń z pomiarami
- Testowanie wskaźnika połączenia z backendem
- Testowanie odświeżania danych (jeśli implementowane)
- Testowanie przejść do szczegółowych stron (urządzenia, pomiary, analizy)

#### Historia pomiarów i filtrowanie (sekcja 09)
- Testowanie otwierania strony historii pomiarów
- Testowanie wyboru urządzenia z rozwijanej listy
- Testowanie wyboru zakresu czasu (presety i niestandardowy)
- Testowanie zmiany liczby rekordów na stronie
- Testowanie zastosowania filtrów i weryfikacja wyników
- Testowanie sortowania przez kliknięcie na nagłówki kolumn
- Testowanie paginacji (zmiana strony)
- Testowanie eksportu danych jeśli implementowany

#### Wykresy i analityka (sekcja 10)
- Testowanie otwierania strony analizy
- Testowanie wyboru urządzenia, zakresu czasu, typu wykresu
- Testowanie wyboru parametrów do wyświetlenia
- Testowanie aktualizacji wykresów przy zmianie parametrów
- Testowanie interakcji z wykresami (tooltipy, zoom, pan jeśli implementowane)
- Testowanie odpowiedzi wykresów na zmianę rozmiaru okna (responsywność)

#### Status urządzeń (sekcja 11)
- Testowanie otwierania strony listy urządzeń
- Testowanie wyświetlania wszystkich urządzeń użytkownika
- Testowanie przejścia do szczegółów urządzenia
- Testowanie wyświetlania szczegółowych informacji o urządzeniu
- Testowanie wyświetlania danych sensorycznych i statusów
- Testowanie mini-wykresów lub wskaźników trendów jeśli implementowane

#### Ustawienia (sekcja 12)
- Testowanie otwierania strony ustawień
- Testowanie edycji profilu użytkownika
- Testowanie zmiany hasła
- Testowanie dodawania, edytowania i usuwania urządzeń
- Testowanie konfiguracji powiadomień jeśli implementowane
- Testowanie zmiany jednostek i formatów jeśli implementowane

### 6. Weryfikacja UI i konsoli
- **Sprawdzanie błędów JavaScript**:
  - Przechwytywanie i logowanie wszystkich błędów window.onerror
  - Przechwytywanie i logowanie ostrzeżeń konsoli
  - Testy nie powinny przechodzić jeśli występują nieoczekiwane błędy JS
- **Weryfikacja elementów UI**:
  - Sprawdzanie że oczekiwane elementy są obecne na stronie
  - Sprawdzanie że elementy mają prawidłowe teksty, wartości, atrybuty
  - Sprawdzanie stanu elementów (włączone/wyłączone, wybrane/nie wybrane)
  - Sprawdzanie widoczności elementów (ukryte/pokazane zgodnie z warunkami)
- **Weryfikacja treści**:
  - Sprawdzanie że oczekiwane teksty są obecne
  - Sprawdzanie że liczby i daty są prawidłowo sformatowane
  - Sprawdzanie że wartości mieszczą się w oczekiwanych zakresach

### 7. Testy regresji wizualnej
- **Porównywanie zrzutów ekranu**:
  - Pobieranie zrzutów ekranu całych stron lub konkretnych elementów
  - Porównywanie z bazowymi zrzutami ekranu (zatwierdzonymi wersjami)
  - Zgłaszanie różnic które przekraczają określony próg
- **Strategia podejścia**:
  - Zrzuty ekranu kluczowych stron po każdej istotnej zmianie
  - Zrzuty ekranu komponentów które są szczególnie podatne na zmiany
  - Użycie narzędzi takich jak Percy, Applitools lub własnej implementacji basada na porównywaniu pikseli
- **Rozważania**:
  - Ignorowanie dynamicznych treści (timery, liczniki, losowe dane)
  - Skupienie się na stałych elementach układu i stylizacji
  - Dostosowanie progów różnic dla różnych typów zmian

### 8. Testy dostępności w przeglądarce
- **Nawigacja klawiaturą**:
  - Testowanie możliwości nawigacji przez całą stronę za pomocą jedynie klawisza Tab
  - Testowanie logicznej kolejności fokusa
  - Testowanie widoczności fokusa (focus ring)
  - Testowanie obsługi klawiszy Enter, Space, Escape, strzałek
- **Czytniki ekranu** (opcjonalnie, jeśli dostępne narzędzia):
  - Testowanie z użyciem narzędzi symulujących czytniki ekranu
  - Weryfikacja że etykiety ARIA są prawidłowo odczytywane
  - Weryfikacja że struktura strony jest logicznie przekazywana
- **Kontrast kolorów**:
  - Testowanie automatyczne lub ręczne kontrastu kolorów
  - Weryfikacja że spełnia wymagania WCAG 2.1 AA

### 9. Testy wydajności
- **Mierzenie czasu ładowania**:
  - Czas od nawigacji do strony do momentu gdy jest gotowa do interakcji
  - Czas ładowania krytycznych zasobów (CSS, JS, czcionki)
  - Czas do pierwszego znaczącego malowania (FCP)
  - Czas do pełnej interaktywności (TTI)
- **Mierzenie czasu interakcji**:
  - Czas reakcji na kliknięcie przycisku
  - Czas aktualizacji wykresów po zmianie parametru
  - Czas ładowania danych przy zmianie filtrów
- **Monitorowanie zasobów**:
  - Liczba żądań HTTP
  - Rozmiar przesyłanych danych
  - Wykorzystanie pamięci (jeśli możliwe do zmierzenia)

### 10. Testy sieci i żądań HTTP
- **Weryfikacja żądań**:
  - Sprawdzanie że wszystkie wymagane żądania są wysyłane
  - Sprawdzanie że żądania używają prawidłowych metod (GET, POST, etc.)
  - Sprawdzanie że żądania mają prawidłowe URL'i i parametry
  - Sprawdzanie że żądania mają wymagane headers (Authorization, Content-Type)
- **Weryfikacja odpowiedzi**:
  - Sprawdzanie że odpowiedzi mają prawidłowe kody statusu
  - Sprawdzanie że odpowiedzi mają prawidłowy format (JSON)
  - Sprawdzanie że odpowiedzi zawierają oczekiwane dane
  - Sprawdzanie że błędne odpowiedzi są prawidłowo obsługiwane
- **Symulowanie warunków sieciowych**:
  - Testowanie przy różnych prędkościach połączenia (3G, 4G, offline)
  - Testowanie zachowania przy utracie połączenia
  - Testowanie mechanizmów ponawiania (jeśli implementowane)

## Konkretne zadania do wykonania
1. Utworzyć strukturę katalogu testów przeglądarkowych jak opisano powyżej
2. Utworzyć plik konfiguracyjny Playwright (`playwright.config.py` lub `playwright.config.ts`)
3. Zainstalować wymagane biblioteki testowe i dodać je do `requirements-dev.txt` lub podobnego
4. Utworzyć przykładowe fixture'i dla danych testowych i poświadczeń
5. Zaimplementować Page Object Model dla kluczowych stron aplikacji
6. Napisać testy end-to-end dla przepływu uwierzytelniania
7. Napisać testy end-to-end dla nawigacji i podstawowej funkcjonalności
8. Napisać testy end-to-end dla historii pomiarów i filtrowania
9. Napisać testy end-to-end dla wykresów i analityki
10. Napisać testy end-to-end dla statusu urządzeń
11. Napisać testy end-to-end dla ustawień
12. Zaimplementować mechanizm przechwytywania i weryfikacji błędów konsoli
13. Zaimplementować podstawowe testy regresji wizualnej (porównywanie zrzutów ekranu)
14. Zaimplementować testy dostępności (nawigacja klawiaturą, fokus)
15. Zaimplementować podstawowe testy wydajności (mierzenie czasu ładowania)
16. Zaimplementować testy sieci (weryfikacja żądań i odpowiedzi HTTP)
17. Skonfigurować uruchamianie testów na wielu przeglądarkach (Chromium, Firefox, WebKit)
18. Utworzyć skrypt uruchamiający wszystkie testy przeglądarkowe z odpowiednimi opcjami
19. Dodawać odpowiednie komentarze w kodzie testowym wskające co jest testowane
20. Regularnie uruchamiać testy podczas rozwoju aby zapobiec regresjom

## Wymagania techniczne
- Playwright jako główny framework testowy przeglądarkowy
- Biblioteka do assertions (Playwright ma wbudowane expect, lub można użyć własnej)
- Opcjonalnie: biblioteki do regresji wizualnej (Percy, Applitools, porownywanie obrazków)
- Opcjonalnie: biblioteki do testowania dostępności (axe-core, pa11y lub podobne)
- Zmienne środowiskowe dla konfiguracji testowej:
  - `BASE_URL=http://localhost:5000` (lub podobny URL aplikacji)
  - `TEST_USER_EMAIL=test@example.com`
  - `TEST_USER_PASSWORD=testpassword123`
  - `HEADLESS=true` (uruchamiać przeglądarkę w trybie headless dla CI)
  - `BROWSER=chromium` (lub firefox, webkit, lub wszystkie)
  - `TRIALS=3` (liczba prób dla niestabilnych testów)
  - `VISUAL_BASELINE=./visual_baselines/` (ścieżka do bazowych zrzutów ekranu)

## Wymagania wizualne
Brak bezpośrednich wymagań wizualnych dla tej sekcji (ona sama weryfikuje wymagania wizualne innych sekcji).

## Pliki, które należy utworzyć lub zmodyfikować
- `playwright.config.py` lub `playwright.config.ts` - konfiguracja Playwright
- `requirements-dev.txt` - dodatkowe wymagania dla rozwoju i testów
- `tests/e2e/pages/login_page.py` - Page Object dla strony logowania
- `tests/e2e/pages/dashboard_page.py` - Page Object dla strony głównej
- `tests/e2e/pages/measurements_page.py` - Page Object dla strony historii pomiarów
- `tests/e2e/pages/analytics_page.py` - Page Object dla strony analizy
- `tests/e2e/pages/devices_page.py` - Page Object dla strony urządzeń
- `tests/e2e/pages/settings_page.py` - Page Object dla strony ustawień
- `tests/e2e/tests/test_auth_flow.py` - testy end-to-end dla uwierzytelniania
- `tests/e2e/tests/test_dashboard_navigation.py` - testy end-to-end dla nawigacji
- `tests/e2e/tests/test_measurements_filtering.py` - testy end-to-end dla filtrowania pomiarów
- `tests/e2e/tests/test_device_management.py` - testy end-to-end dla zarządzania urządzeniami
- `tests/e2e/tests/test_analytics_interactions.py` - testy end-to-end dla interakcji z wykresami
- `tests/e2e/tests/test_settings_updates.py` - testy end-to-end dla aktualizacji ustawień
- `tests/e2e/fixtures/test_credentials.py` - poświadczenia testowe
- `tests/e2e/fixtures/test_data.py` - przykładowe dane testowe
- `tests/e2e/utils/browser_helpers.py` - funkcje pomocnicze dla testów przeglądarkowych
- `tests/e2e/utils/assert_helpers.py` - funkcje pomocnicze do asercji

## Integrację z pozostałymi elementami systemu
- Testy będą weryfikować poprawność implementacji wszystkich poprzednich sekcji w rzeczywistym środowisku przeglądarkowym:
  - Sekcję 05 (Flask Foundation) - podstawowa funkcjonalność aplikacji w przeglądarce
  - Sekcję 06 (Backend Integration) - komunikacja z backendem poprzez rzeczywiste żądania HTTP
  - Sekcję 07 (Shared Layout) - renderowanie layoutu i komponentów w przeglądarce
  - Sekcję 08 (Dashboard Overview) - funkcjonalność strony głównej z interakcją użytkownika
  - Sekcję 09 (Measurements and History) - funkcjonalność historii pomiarów z filtrowaniem i sortowaniem
  - Sekcję 10 (Charts and Analytics) - funkcjonalność wykresów i analizy z interakcją
  - Sekcję 11 (Device Status and Diagnostics) - funkcjonalność statusu urządzeń z widokiem szczegółów
  - Sekcję 12 (Settings and Additional Features) - funkcjonalność ustawień z edycją danych
  - Sekcję 13 (AnimeJS and Interactions) - obecność i działanie animacji
  - Sekcję 14 (Loading, Empty, Error States) - poprawne wyświetlanie stanów ładowania, pustych danych i błędów
  - Sekcję 15 (Responsiveness and Accessibility) - odpowiedzialność i dostępność w rzeczywistym środowisku
  - Sekcję 16 (Security and Reliability) - środki bezpieczeństwa i niezawodności (uwierzytelnianie, CSRF, etc.)

## Obsługę błędów i przypadków brzegowych
- Testy które zależą od zewnętrznych zasobów: użycie mocków lub kontrolowanego środowiska testowego aby uniknąć zależności od dostępności backendu podczas testów
- Testy które są czasochłonne: oznaczenie jako wolne i możliwość wykluczenia przy szybkim uruchamianiu
- Testy które wymagają określonej konfiguracji: użycie fixture'ów które konfigurują środowisko odpowiednio
- Testy które mogą mieć skutki uboczne: zapewnienie czyszczenia po teście (np. usuwanie utworzonych urządzeń)
- Konflikt między realizmem a kontrolą testową: balans między testowaniem rzeczywistych scenariuszy a zapewnieniem powtarzalności
- Problemy z niezdeterminizmem (np. animacje, czasy): użycie odpowiednich czasów oczekiwania i warunków

## Testy wymagane do uznania sekcji za ukończoną
- Co najmniej jeden test end-to-end dla każdego głównego przepływu funkcjonalności (uwierzytelnianie, nawigacja, zarządzanie urządzeniami, pomiary, analizy, ustawienia)
- Testy które sprawdzają brak błędów JavaScript w konsoli podczas typowych interakcji
- Testy które weryfikują podstawową responsywność na różnych szerokościach ekranu
- Testy które weryfikują dostępność klawiaturową (nawigacja za pomocą jedynie Tab)
- Testy które weryfikują że żądania HTTP są wysyłane z prawidłowymi parametrami i headers
- Testy które można uruchomić w izolowanym środowisku z kontrolowanym backendem (lub mockami)

## Jednoznaczne kryteria akceptacji
- Struktura katalogu testów przeglądarkowych jest utworzona i zawiera przykładowe testy
- Testy end-to-end są tworzone dla głównych przepływów funkcjonalności aplikacji
- Testy weryfikują brak błędów JavaScript w konsoli
- Testy weryfikują podstawową responsywność i dostępność
- Testy można uruchomić za pomocą jednej komendy (np. `playwright test`)
- Sekcja może być uznana za ukończoną po pozytywnej weryfikacji przez lead developer lub poprzez automated tests

## Zależności od innych sekcji
- Zależna od: wszystkie poprzednie sekcje (01-17) ponieważ testujemy ich implementację w przeglądarce
- Wymagana przez: sekcja 19 (Deployment and Docker) która może wymagać uruchomienia testów przed wdrożeniem
- Jednak przed uznaniem jakiejkolwiek sekcji implementacyjnej (05-16) za ukończoną, należy mieć odpowiednie testy jednostkowe z sekcji 17 oraz testy przeglądarkowe z tej sekcji

## Warunki zakończenia prac
- Struktura katalogu testów przeglądarkowych jest utworzona
- Page Object Model jest zaimplementowany dla kluczowych stron
- Testy end-to-end są napisane dla głównych przepływów funkcjonalności
- Testy weryfikują brak błędów JavaScript, podstawową responsywność i dostępność
- Testy można uruchomić i przechodzą w kontrolowanym środowisku
- Sekcja może być uznana za ukończoną po pozytywnej weryfikacji przez lead developer lub poprzez automated tests

## Informacje, które należy przekazać do kolejnych sekcji
- Struktura katalogu testów przeglądarkowych i sposób organizacji testów
- Przykłady implementacji Page Object Model dla różnych typów stron
- Przykłady testów end-to-end dla różnych przepływów funkcjonalności
- Informacje o uruchamianiu testów (komenda, opcje, środowisko, przeglądarki)
- Informacje o przechwytywaniu i weryfikacji błędów konsoli
- Informacje o podstawowych testach regresji wizualnej
- Informacje o testach dostępności (nawigacja klawiaturą, fokus)
- Informacje o testach wydajności (mierzenie czasu ładowania i interakcji)
- Informacje o testach sieci (weryfikacja żądań i odpowiedzi HTTP)

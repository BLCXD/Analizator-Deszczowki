# 11_DEVICE_STATUS_AND_DIAGNOSTICS.md
## Status urządzeń, diagnostyka i informacje o systemie, wyłącznie w zakresie wspieranym przez backend

## Cel sekcji
Zaimplementowanie strony wyświetlającej szczegółowy status i diagnostykę poszczególnych urządzeń oraz informacje o systemie. Strona pozwala na monitorowanie zdrowia urządzeń, przeglądanie ich konfiguracji oraz diagnozowanie problemów.

## Kontekst i zależności
Ta sekcja zależy od:
- 01_PROJECT_ANALYSIS.md (zrozumienie formatów danych urządzeń i diagnostyki)
- 02_ARCHITECTURE.md (wzorzec architektoniczny)
- 03_DESIGN_SYSTEM.md (stylizacja komponentów statusu)
- 04_ENVIRONMENT_AND_CONFIGURATION.md (konfiguracja)
- 05_FLASK_FOUNDATION.md (routing i struktura)
- 06_BACKEND_INTEGRATION.md (pobieranie danych o urządzeniach)
- 07_SHARED_LAYOUT_AND_NAVIGATION.md (layout i nawigacja)
Nie ma zależności od innych sekcji implementacyjnych, ale może korzystać z komponentów z sekcji 10 (wykresy) do wyświetlania historii pomiarów urządzenia.

## Stan początkowy
- Katalog `flask-frontend-user` zawiera podstawową strukturę Flaska, szablony layoutu i klienta API
- Brak istniejącej strony statusu urządzeń
- Brak komponentów wyświetlających szczegółowe informacje o urządzeniach

## Szczegółowy zakres implementacji
### 1. Struktura strony
- Utworzenie kontrolera Flask dla statusu urządzeń w `app/controllers/devices.py` lub bezpośrednio w `app/routes.py`
- Utworzenie szablonu HTML `app/templates/devices/index.html` dla listy urządzeń
- Utworzenie szablonu HTML `app/templates/devices/[device_id].html` lub `app/templates/devices/detail.html` dla szczegółów konkretnego urządzenia
- Strony będą wykorzystywać layout bazowy z sekcji 07

### 2. Lista urządzeń (overview)
Strona listy urządzeń będzie zawierać:
- Tabela lub siatka kart przedstawiająca wszystkie urządzenia użytkownika
- Dla każdego urządzenia pokazujemy:
  - Nazwa urządzenia
  - Lokalizacja
  - Status połączenia (online/offline, ostatni kontakt)
  - Siła sygnału (jeśli dostępny)
  - Ostatni pomiar (timestamp i wartości podstawowe)
  - Liczba błędów lub ostrzeżeń (jeśli dostępne)
- Akcje dla każdego urządzenia:
  - Szczegóły (przejście do strony szczegółów urządzenia)
  - Konfiguracja (przejście do sekcji 12 dla tego urządzenia)
  - Usuń (z potwierdzeniem)
- Przycisk "Dodaj nowe urządzenie" (przejście do sekcji 12)

### 3. Szczegóły urządzenia
Strona szczegółów konkretnego urządzenia będzie zawierać:

#### Podstawowe informacje
- Nazwa urządzenia
- Lokalizacja
- ID urządzenia
- Data utworzenia
- Data ostatniej aktywności
- Informacje o firmware (wersja, czas ostatniej aktualizacji)

#### Status połączenia
- Czy urządzenie jest online/offline
- Timestamp ostatniego kontaktu
- Średni czas odpowiedzi (jeśli mierzony)
- Liczba nieudanych prób połączenia (jeśli dostępna)

#### Dane sensoryczne
- Aktualne odczyty wszystkich czujników (pH, mętność, przepływ, temperatura)
- Status każdego czujnika (OK, kalibracja wymagana, błąd)
- Wskaźniki stanu (kolorowe kółka lub paski)
- Jeśli brak danych: informacja o tym kiedy ostatnio otrzymano pomiary

#### Historia i trendy
- Mini-wykresy pokazujące ostatnie 24 godziny dla każdego parametru (można wykorzystać komponent z sekcji 10)
- Wskaźniki trendów (rosnący, malejący, stabilny)
- Informacje o kalibracji (data ostatniej kalibracji, kiedy następna zalecana)

#### Diagnostyka i logs
- Jeśli backend udostępnia:
  - Logi urządzenia (ostatnie N wpisów)
  - Kody błędów i ich opis
  - Informacje o restarcie urządzenia
  - Statystyki przesyłania danych (procent udanych transmisji)
- Jeśli backend nie udostępnia szczegółowej diagnostyki: pokazanie podstawowych informacji i link do dokumentacji urządzenia

#### Konserwacja
- Informacje o wymaganej konserwacji
- Przyciski do działań konserwacyjnych (jeśli wspierane przez backend):
  - Kalibracja
  - Restart
  - Aktualizacja firmware
  - Reset do ustawień fabrycznych

### 4. Informacje o systemie
- Sekcja pokazująca informacje o systemie backendowym (jeśli dostępne):
  - Wersja oprogramowania
  - Czas pracy systemu
  - Zużycie zasobów (CPU, pamięć, dysk)
  - Liczba połączonych urządzeń
  - Liczba przetworzonych pomiarów dzisiaj
  - Alerty systemowe lub powiadomienia o konserwacji

### 5. Pobieranie danych
- Wykorzystanie klienta API z sekcji 06 do pobierania:
  - Lista urządzeń: `GET /api/v1/devices/`
  - Szczegóły urządzenia: `GET /api/v1/devices/{device_id}`
  - Aktualny pomiar urządzenia: `GET /api/v1/measurements/{device_id}/latest`
  - Historia pomiarów urządzenia: `GET /api/v1/measurements/{device_id}` z ograniczonym zakresem czasu
  - Informacje o systemie: zależnie od dostępnych endpointów (sprawdzić w backendzie)
  - Diagnostyka urządzenia: zależnie od dostępnych endpointów
- Implementacja mechanizmu odświeżania danych dla stron szczegółowych (np. co 30 sekund)
- Obsługa stanu ładowania podczas pobierania danych (komponent z sekcji 14)
- Obsługa błędów podczas pobierania danych (komunikaty użytkownikowi)

### 6. Formatowanie i wyświetlanie danych
- Formatowanie timestampów do czytelnej postaci
- Kolorowanie statusów (zielony = OK, żółty = ostrzeżenie, czerwony = błąd)
- Wyświetlanie jednostek zgodnie z konfiguracją
- Skracanie długich tekstów z dodaniem podpowiedzi przy pełnej treści
- Grupowanie powiązanych informacji w sekcjach z wyraźnymi nagłówkami

### 7. Responsywność
- Lista urządzeń: siatka kart która dostosowuje liczbę kolumn do szerokości ekranu
- Strona szczegółów urządzenia: sekcje układające się pionowo na małych ekranach
- Na bardzo małych ekranach: niektóre sekcje mogą być ukryte za zakładkami lub akordeonami

## Konkretne zadania do wykonania
1. Utworzyć kontroler/route dla listy urządzeń (np. `@app.route('/devices')`)
2. Utworzyć kontroler/route dla szczegółów urządzenia (np. `@app.route('/devices/<device_id>')`)
3. Utworzyć szablon HTML dla listy urządzeń
4. Utworzyć szablon HTML dla szczegółów urządzenia
5. Zaimplementować logikę pobierania danych z backendu przy użyciu klienta API
6. Zaimplementować komponenty UI dla wyświetlania statusu, danych sensorycznych i diagnostyki
7. Zaimplementować mini-wykresy lub wskaźniki trendów (można wykorzystać proste SVG lub komponent z sekcji 10)
8. Zaimplementować stan ładowania i obsługę błędów
9. Zaimplementować mechanizm odświeżania danych dla stron szczegółowych
10. Zaimplementować responsywny układ stron
11. Dodawać odpowiednie klasy CSS zgodnie z design systemem
12. Napisać testy jednostkowe i integracyjne dla kontrolerów i szablonów (zobacz sekcje 17 i 18)

## Wymagania techniczne
- Dostęp do klienta API z sekcji 06
- Jinja2 dla renderowania szablonów
- Brak dodatkowych bibliotek wymaganych dla podstawowej funkcjonalności
- Opcjonalnie: biblioteka do formatowania dat (np. `python-dateutil`)
- Opcjonalnie: prosta biblioteka do wykresów lub możliwość tworzenia SVG dla mini-wykresów

## Wymagania wizualne
- Strona powinna być przejrzysta mimo dużej ilości informacji
- Informacje powinny być pogrupowane w logiczne sekcje
- Statusy powinny być wyraźnie widoczne poprzez kolory i ikony
- Najważniejsze informacje (aktualne odczyty, status połączenia) powinny być na górze
- Komponenty UI (przyciski, przełączniki, pola input) zgodne z design systemem
- Ikony lub wizualne wskaźniki stanów (opcjonalnie, jeśli wspierane przez design system)

## Pliki, które należy utworzyć lub zmodyfikować
- `app/routes.py` lub podobny - dodanie route dla urządzeń
- `app/controllers/devices.py` - nowy plik kontrolera (opcjonalnie)
- `app/templates/devices/index.html` - nowy plik szablonu dla listy urządzeń
- `app/templates/devices/detail.html` - nowy plik szablonu dla szczegółów urządzenia
- Komponenty UI do wykorzystania w szablonach (można utworzyć w `app/templates/components/` lub wykorzystać istniejące z sekcji 07)
- Pliki statyczne (CSS/JS) jeśli potrzebne dla konkretnych efektów na tej stronie

## Integrację z pozostałymi elementami systemu
- Strony statusu urządzeń będą wykorzystywać:
  - Layout bazowy z sekcji 07
  - Komponenty UI z sekcji 07 i 14 (loading, empty state, error)
  - Klient API z sekcji 06 do pobierania danych
  - Mechanizm uwierzytelniania (sprawdzenie czy użytkownik jest zalogowany)
  - Nawigację z sekcji 07 (aktywny element w menu)
  - Animacje przejść z sekcji 13 (opcjonalnie)
  - Responsywność z sekcji 15
  - Obsługę błędów z sekcji 14 i 16
  - Mini-wykresy mogą wykorzystywać komponenty lub logikę z sekcji 10
  - Informacje mogą być wykorzystywane przez sekcję 08 (Dashboard Overview) do pokazywania podsumowania urządzeń

## Obsługę błędów i przypadków brzegowych
- Brak urządzeń przypisanych do użytkownika: pokazanie komunikatu zachęcającego do dodania pierwszego urządzenia
- Błąd połączenia z backendem: pokazanie komunikatu o problemach z połączeniem i możliwość ponowienia próby
- Urządzenie nie znaleźć (nieprawidłowy device_id): pokazanie komunikatu 404 i przekierowanie do listy urządzeń
- Nieprawidłowe lub niekompletne dane od backendu: logowanie błędu i pokazanie komunikatu o problemie technicznym
- Brak danych sensorycznych: pokazanie komunikatu "Brak danych" zamiast pustych wykresów
- Problemy z odświeżaniem danych: mechanizm zapobiegający częstym żądaniami (np. debouncing)
- Dostęp do szczegółów urządzenia którego nie posiada użytkownik: przekierowanie z komunikatem o braku uprawnień

## Testy wymagane do uznania sekcji za ukończoną
- Testy jednostkowe dla kontrolerów/logiki pobierania i formatowania danych
- Testy integracyjne sprawdzające renderowanie listy urządzeń i szczegółów urządzenia z różnymi danymi wejściowymi
- Testy sprawdzające obsługę przypadków brzegowych (brak danych, błąd połączenia, nieprawidłowe ID, itp.)
- Testy responsywności (sprawdzenie układu na różnych szerokościach ekranu)
- Testy dostępności (sprawdzenie semantycznego HTML, etykiet ARIA, nawigacji klawiaturą)

## Jednoznaczne kryteria akceptacji
- Strona listy urządzeń jest dostępna po zalogowaniu pod odpowiednim URL (np. `/devices`)
- Strona szczegółów urządzenia jest dostępna po zalogowaniu pod odpowiednim URL (np. `/devices/<device_id>`)
- Strony wykorzystują layout bazowy z sekcji 07
- Strona listy urządzeń wyświetla wszystkie urządzenia użytkownika z ich podstawowymi informacjami
- Strona szczegółów urządzenia wyświetla kompleksowe informacje o wybranym urządzeniu
- Strony prawidłowo pobierają i wyświetlają dane z backendu
- Strony są responsywne i działają na szerokościach od 320px do 1920px
- Strony prawidłowo obsługują stany ładowania, puste dane i błędy
- Strony są łatwe w użyciu poprzez intuicyjny interfejs i nawigację

## Zależności od innych sekcji
- Zależna od: wszystkie poprzednie sekcje (01-10)
- Wymagana przez: sekcje które mogą potrzebować informacji o urządzeniach (np. sekcja 08 do podsumowania na dashboardzie)

## Warunki zakończenia prac
- Strona listy urządzeń i strona szczegółów urządzenia są w pełni zaimplementowane i zintegrowane z layoutem
- Wszystkie komponenty stron są stworzone i działają poprawnie
- Strony prawidłowo pobierają, filtrują i wyświetlają dane z backendu
- Sekcja może być uznana za ukończoną po pozytywnej weryfikacji przez lead developer lub poprzez automated tests

## Informacje, które należy przekazać do kolejnych sekcji
- Przykłady użycia klienta API do pobierania danych o urządzeniach
- Formaty danych zwracane przez funkcje API (po mapowaniu z sekcji 06)
- Wzorce tworzenia komponentów wyświetlających status urządzenia i dane sensoryczne
- Informacje o klasach CSS i identyfikatorach używanych w stronach (dla stylizacji w sekcji 03)
- Przykłady implementacji stanu ładowania i obsługi błędów
- Przykłady implementacji komponentów UI dla listy urządzeń i szczegółów urządzenia
- Przykłady implementacji mini-wykresów lub wskaźników trendów

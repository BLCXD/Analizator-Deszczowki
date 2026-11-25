# 09_MEASUREMENTS_AND_HISTORY.md
## Historia pomiarów, tabele, filtrowanie, zakresy czasu i szczegóły dostępnych rekordów

## Cel sekcji
Zaimplementowanie strony wyświetlającej historię pomiarów z możliwością filtrowania, sortowania i paginacji. Strona pozwala na szczegółowe przeglądanie pomiarów dla wybranych urządzeń i przedziałów czasowych.

## Kontekst i zależności
Ta sekcja zależy od:
- 01_PROJECT_ANALYSIS.md (zrozumienie formatów danych pomiarowych)
- 02_ARCHITECTURE.md (wzorzec architektoniczny)
- 03_DESIGN_SYSTEM.md (stylizacja tabel i komponentów)
- 04_ENVIRONMENT_AND_CONFIGURATION.md (konfiguracja)
- 05_FLASK_FOUNDATION.md (routing i struktura)
- 06_BACKEND_INTEGRATION.md (pobieranie danych pomiarowych)
- 07_SHARED_LAYOUT_AND_NAVIGATION.md (layout i nawigacja)
Nie ma zależności od innych sekcji implementacyjnych, ale jest wymagana dla sekcji, które mogą potrzebować szczegółowych danych pomiarowych (np. wykresy w sekcji 10 mogą wykorzystywać te same dane).

## Stan początkowy
- Katalog `flask-frontend-user` zawiera podstawową strukturę Flaska, szablony layoutu i klienta API
- Brak istniejącej strony historii pomiarów
- Brak komponentów tabeli lub paginacji

## Szczegółowy zakres implementacji
### 1. Struktura strony
- Utworzenie kontrolera Flask dla historii pomiarów w `app/controllers/measurements.py` lub bezpośrednio w `app/routes.py`
- Utworzenie szablonu HTML `app/templates/measurements/index.html` lub `app/templates/measurements.html`
- Strona będzie wykorzystywać layout bazowy z sekcji 07

### 2. Komponenty strony
Strona historii pomiarów będzie zawierać następujące sekcje:

#### Panel sterowania filtrem
- Wybór urządzenia (rozwijana lista wszystkich urządzeń użytkownika + opcja "Wszystkie urządzenia")
- Zakres czasu:
  - Gotowe preset'y: Ostatnia godzina, Ostatnie 6 godzin, Ostatnie 24 godziny, Ostatni tydzień, Ostatni miesiąc
  - Niestandardowy zakres: kalendarz data początkowa i końcowa
- Liczba rekordów na stronie (paginacja): 10, 25, 50, 100
- Przycisk "Zastosuj filtr" i "Resetuj filtr"
- Opcjonalnie: eksport do CSV/JSON

#### Tabela pomiarów
- Nagłówki kolumn:
  - Timestamp (data i czas pomiaru)
  - Urządzenie (nazwa i lokalizacja)
  - pH (wartość i jednostka)
  - Mętność (wartość i jednostka)
  - Przepływ (wartość i jednostka)
  - Temperatura (wartość i jednostka)
  - Status (np. OK, poza normą, błąd)
- Wiersze danych pomiarowych
- Sortowanie kolumn (kliknięcie na nagłówek)
- Paginacja na dole tabeli (informacja o liczbie stron i aktualnej stronie)
- Opcjonalnie: wiersz podsumowujący (średnie, min, max dla wybranego zakresu)

#### Panel podsumowania statystyk
- Dla wybranego zakresu czasu i urządzenia pokaż:
  - Średnie, minimalne, maksymalne wartości dla każdego parametru
  - Liczba pomiarów w zakresie
  - Procent pomiarów poza normą (jeśli normy są zdefiniowane)
  - Wykres sparkline lub mini-wykres trendu (opcjonalnie, można wykorzystać komponent z sekcji 10)

### 3. Pobieranie danych
- Wykorzystanie klienta API z sekcji 06 do pobierania:
  - Lista urządzeń: `GET /api/v1/devices/` (do wypełnienia rozwijanej listy)
  - Pomiarów z filtrami: `GET /api/v1/measurements/` z parametrami:
    - `device_id` (opcjonalnie)
    - `skip` i `limit` (dla paginacji)
    - `start_time` i `end_time` (lub tylko jeden z nich, zależnie od implementacji backendowej)
- Implementacja mechanizmu odświeżania danych przy zmianie filtrów
- Obsługa stanu ładowania podczas pobierania danych (komponent z sekcji 14)
- Obsługa błędów podczas pobierania danych (komunikaty użytkownikowi)

### 4. Formatowanie i wyświetlanie danych
- Formatowanie timestampów do czytelnej postaci (np. "2024-01-15 14:30:22")
- Kolorowanie wartości pomiarów w zależności od tego czy są w normie (patrz sekcja 08 dla podobnej logiki)
- Wyświetlanie jednostek zgodnie z konfiguracją (np. pH bez jednostki, mętność w NTU, przepływ w L/min, temperatura w °C)
- Jeśli brak danych dla wybranych filtrów: pokazanie komunikatu "Brak danych spełniających kryteria"
- Jeśli liczba rekordów jest duża: zapewnienie płynnej pracy poprzez paginację po stronie backendu

### 5. Responsywność
- Tabela przewijalna poziomo na małych ekranach (lub przekształcenie w karty)
- Panel filtrów może zmieniać układ z poziomego na pionowy na małych ekranach
- Panel podsumowania statystyk może być ukryty lub pokazywany jako akordeon na małych ekranach

## Konkretne zadania do wykonania
1. Utworzyć kontroler/route dla historii pomiarów (np. `@app.route('/measurements')`)
2. Utworzyć szablon HTML dla strony historii pomiarów
3. Zaimplementować logikę pobierania danych z backendu przy użyciu klienta API z filtrami
4. Zaimplementować komponent UI dla filtra (urządzenie, zakres czasu, limit)
5. Zaimplementować komponent tabeli z sortowaniem i paginacją
6. Zaimplementować komponent panelu podsumowania statystyk
7. Zaimplementować stan ładowania i obsługę błędów
8. Zaimplementować mechanizm aktualizacji danych przy zmianie filtrów
9. Zaimplementować responsywny układ strony
10. Dodawać odpowiednie klasy CSS zgodnie z design systemem
11. Napisać testy jednostkowe i integracyjne dla kontrolera i szablonu (zobacz sekcje 17 i 18)

## Wymagania techniczne
- Dostęp do klienta API z sekcji 06
- Jinja2 dla renderowania szablonów
- Brak dodatkowych bibliotek wymaganych dla podstawowej funkcjonalności (sortowanie i paginacja można zaimplementować ręcznie lub poprzez proste logikę w kontrolerze)
- Opcjonalnie: biblioteka do obsługi dat (np. `python-dateutil`)

## Wymagania wizualne
- Strona powinna być przejrzysta mimo dużej ilości danych
- Filtry powinny być wyraźnie widoczne i łatwe w użyciu
- Tabela powinna mieć wyraźne oddzielenie wierszy (linie lub różne kolory tła)
- Nagłówki tabeli powinny być wyróżnione
- Komponenty UI (przyciski, rozwijane listy, pola input) zgodne z design systemem
- Ikony lub wizualne wskaźniki stanów (opcjonalnie, jeśli wspierane przez design system)

## Pliki, które należy utworzyć lub zmodyfikować
- `app/routes.py` lub podobny - dodanie route dla historii pomiarów
- `app/controllers/measurements.py` - nowy plik kontrolera (opcjonalnie)
- `app/templates/measurements/index.html` - nowy plik szablonu
- Komponenty UI do wykorzystania w szablonie (można utworzyć w `app/templates/components/` lub wykorzystać istniejące z sekcji 07)
- Pliki statyczne (CSS/JS) jeśli potrzebne dla konkretnych efektów na tej stronie (np. obsługa sortowania kliknięciem)

## Integrację z pozostałymi elementami systemu
- Strona historii pomiarów będzie wykorzystywać:
  - Layout bazowy z sekcji 07
  - Komponenty UI z sekcji 07 i 14 (loading, empty state, error)
  - Klient API z sekcji 06 do pobierania danych
  - Mechanizm uwierzytelniania (sprawdzenie czy użytkownik jest zalogowany)
  - Nawigację z sekcji 07 (aktywny element w menu)
  - Animacje przejść z sekcji 13 (opcjonalnie)
  - Responsywność z sekcji 15
  - Obsługę błędów z sekcji 14 i 16
  - Dane mogą być wykorzystywane przez sekcję 10 (Wykresy i analityka) do tworzenia wykresów dla wybranego zakresu

## Obsługę błędów i przypadków brzegowych
- Brak urządzeń przypisanych do użytkownika: pokazanie komunikatu zachęcającego do dodania pierwszego urządzenia i wyłączenie filtru urządzenia
- Błąd połączenia z backendem: pokazanie komunikatu o problemach z połączeniem i możliwość ponowienia próby
- Nieprawidłowy zakres czasu (data początkowa po końcowej): walidacja i komunikatu użytkownikowi
- Zbyt duży zakres czasu powodujący dużą liczbę rekordów: ostrzeżenie i sugerowanie mniejszego zakresu lub zwiększenia paginacji
- Dane w nieoczekiwanym formacie: logowanie błędu i pokazanie komunikatu o problemie technicznym
- Brak danych dla wybranych filtrów: pokazanie komunikatu "Brak danych"
- Problemy z paginacją (np. żądanie strony poza zakresem): automatyczne korekty do pierwszej lub ostatniej strony

## Testy wymagane do uznania sekcji za ukończoną
- Testy jednostkowe dla kontrolera/logiki pobierania, filtrowania, sortowania i paginacji danych
- Testy integracyjne sprawdzające renderowanie strony historii z różnymi danymi wejściowymi
- Testy sprawdzające obsługę przypadków brzegowych (brak danych, błąd połączenia, nieprawidłowe filtry, itp.)
- Testy responsywności (sprawdzenie układu na różnych szerokościach ekranu)
- Testy dostępności (sprawdzenie semantycznego HTML, etykiet ARIA, nawigacji klawiaturą w tabeli)

## Jednoznaczne kryteria akceptacji
- Strona historii pomiarów jest dostępna po zalogowaniu pod odpowiednim URL (np. `/measurements`)
- Strona wykorzystuje layout bazowy z sekcji 07
- Strona pozwala na wybór urządzenia, zakres czasu i liczbę rekordów na stronie
- Strona pobiera i wyświetla dane pomiarowe z backendu zgodnie z wybranymi filtrami
- Strona pozwala na sortowanie danych przez kliknięcie na nagłówki kolumn
- Strona prawidłowo obsługuje paginację (zmiana strony aktualizuje wyświetlane dane)
- Strona jest responsywna i działa na szerokościach od 320px do 1920px
- Strona prawidłowo obsługuje stany ładowania, puste dane i błędy
- Strona jest łatwa w użyciu poprzez intuicyjny interfejs i nawigację

## Zależności od innych sekcji
- Zależna od: wszystkie poprzednie sekcje (01-08)
- Wymagana przez: sekcje które mogą potrzebować szczegółowych danych pomiarowych (np. sekcja 10 do wykresów szczegółowych)

## Warunki zakończenia prac
- Strona historii pomiarów jest w pełni zaimplementowana i zintegrowana z layoutem
- Wszystkie komponenty strony są stworzone i działają poprawnie
- Strona prawidłowo pobiera, filtruje, sortuje i paginuje dane z backendu
- Sekcja może być uznana za ukończoną po pozytywnej weryfikacji przez lead developer lub poprzez automated tests

## Informacje, które należy przekazać do kolejnych sekcji
- Przykłady użycia klienta API do pobierania danych pomiarowych z filtrami
- Formaty danych zwracane przez funkcje API (po mapowaniu z sekcji 06)
- Wzorce tworzenia komponentów tabeli z sortowaniem i paginacją
- Informacje o klasach CSS i identyfikatorach używanych w stronie (dla stylizacji w sekcji 03)
- Przykłady implementacji stanu ładowania i obsługi błędów
- Przykłady implementacji komponentów UI dla filtrów (urządzenie, zakres czasu, limit)

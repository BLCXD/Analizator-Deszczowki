# 10_CHARTS_AND_ANALYTICS.md
## Wykresy, analiza zmian w czasie, tooltipy, osie, jednostki i wizualizacja rzeczywistych danych

## Cel sekcji
Zaimplementowanie strony z wykresami i analizą danych pomiarowych w czasie. Strona pozwala na wizualizację trendów, porównywanie różnych parametrów oraz analizę danych historycznych za pomocą interaktywnych wykresów.

## Kontekst i zależności
Ta sekcja zależy od:
- 01_PROJECT_ANALYSIS.md (zrozumienie formatów danych pomiarowych)
- 02_ARCHITECTURE.md (wzorzec architektoniczny)
- 03_DESIGN_SYSTEM.md (kolory wykresów, stylizacja)
- 04_ENVIRONMENT_AND_CONFIGURATION.md (konfiguracja)
- 05_FLASK_FOUNDATION.md (routing i struktura)
- 06_BACKEND_INTEGRATION.md (pobieranie danych pomiarowych)
- 07_SHARED_LAYOUT_AND_NAVIGATION.md (layout i nawigacja)
- 09_MEASUREMENTS_AND_HISTORY.md (opcjonalnie, może korzystać z podobnych filtrów)
Nie ma zależności od innych sekcji implementacyjnych, ale jest wymagana dla sekcji, które mogą potrzebować wizualizacji danych (np. sekcja 11 do szczegółowej analizy urządzeń).

## Stan początkowy
- Katalog `flask-frontend-user` zawiera podstawową strukturę Flaska, szablony layoutu i klienta API
- Brak istniejącej strony z wykresami
- Brak zintegrowanej biblioteki wykresów

## Szczegółowy zakres implementacji
### 1. Wybór biblioteki wykresów
Na podstawie wymagań projektu (Anime.js dla animacji) oraz potrzeby wykresów czasowych, zaleca się użycie:
- **Chart.js** - popularna biblioteka wykresów z dobrym wsparciem dla wykresów liniowych, słupkowych i czasowych
- Lub **ApexCharts** - nowoczesna biblioteka z wbudowanymi animacjami i dobrym wsparciem dla wykresów finansowych/czasowych
- Lub **Plotly.js** - zaawansowana biblioteka z interaktywnymi wykresami

Jednak aby uniknąć zbędnych zależności i wykorzystać już wspomniane Anime.js, można rozważyć:
- Proste wykresy SVG z animacjami Anime.js (dla podstawowych potrzeb)
- Lub minimalną integrację z jedną z powyższych bibliotek

Zanim wybierzemy bibliotekę, należy sprawdzić:
- Czy istnieją już jakiekolwiek biblioteki wykresów w package.json lub requirements.txt
- Jakie są rzeczywiste wymagania dotyczącej interaktywności i funkcjonalności wykresów

### 2. Struktura strony
- Utworzenie kontrolera Flask dla wykresów i analizy w `app/controllers/analytics.py` lub bezpośrednio w `app/routes.py`
- Utworzenie szablonu HTML `app/templates/analytics/index.html` lub `app/templates/analytics.html`
- Strona będzie wykorzystywać layout bazowy z sekcji 07

### 3. Komponenty strony
Strona wykresów i analizy będzie zawierać następujące sekcje:

#### Panel kontrolny (podobny do sekcji 09)
- Wybór urządzenia (rozwijana lista wszystkich urządzeń użytkownika)
- Zakres czasu:
  - Gotowe preset'y: Ostatnia godzina, Ostatnie 6 godzin, Ostatnie 24 godziny, Ostatni tydzień, Ostatni miesiąc, Ostatnie 3 miesiące, Ostatni rok
  - Niestandardowy zakres: kalendarz data początkowa i końcowa
- Typ wykresu:
  - Wykres liniowy (domyślny)
  - Wykres słupkowy
  - Wykres punktowy (scatter)
  - Wykres obszarowy
- Parametry do wyświetlenia (checkboxes):
  - pH
  - Mętność
  - Przepływ
  - Temperatura
- Przycisk "Zaktualizuj wykresy"
- Opcjonalnie: zapisywanie własnych widoków

#### Wykresy główne
- Jeden lub więcej wykresów pokazujących wybrane parametry w czasie
- Możliwość pokazywania wielu parametrów na jednym wykresie (z różnymi osiami Y jeśli potrzebne)
- Tooltipy pokazujące dokładne wartości przy najechaniu kursorem
- Możliwość powiększania/przybliżania (zoom i pan)
- Linia trendu lub średniej kroczącej (opcjonalnie)

#### Wykresy dodatkowe / analizy
- Histogramy rozkładu wartości
- Wykres pudełkowy (box plot) pokazujący kwartyle
- Analiza korelacji między parametrami
- Wykres rozproszenia (scatter matrix) między różnymi parametrami
- Analiza sezonowości (jeśli wystarczająco dużo danych)

#### Panel statystyk
- Dla wybranego zakresu czasu i urządzenia pokaż:
  - Średnie, odchylenie standardowe
  - Minimalne, maksymalne wartości
  - Liczba pomiarów
  - Procent danych poza normą
  - Wskaźnik jakości danych (liczba braków danych, etc.)

### 4. Pobieranie danych
- Wykorzystanie klienta API z sekcji 06 do pobierania:
  - Lista urządzeń: `GET /api/v1/devices/`
  - Pomiarów z filtrami: `GET /api/v1/measurements/` z parametrami takimi jak w sekcji 09
  - Analizy trendów: `GET /api/v1/measurements/{device_id}/analysis/trends` (jeśli dostępne w backendzie)
  - Analizy anomalii: `GET /api/v1/measurements/{device_id}/analysis/anomalies` (jeśli dostępne w backendzie)
- Implementacja mechanizmu buforowania danych (opcjonalnie) aby nie pobierać tych samych danych wielokrotnie
- Obsługa stanu ładowania podczas pobierania danych (komponent z sekcji 14)
- Obsługa błędów podczas pobierania danych (komunikaty użytkownikowi)

### 5. Implementacja wykresów
W zależności od wybranej biblioteki:
- Inicjalizacja wykresu po załadowaniu danych
- Aktualizacja wykresu przy zmianie danych lub parametrów
- Obsługa zdarzeń (kliknięcie, najechanie, zoom)
- Formatowanie tooltipów i osi
- Responsywność wykresów (zmiana rozmiaru przy zmianie rozmiaru okna)
- Animacje przy ładowaniu danych lub zmianie wykresu (wykorzystanie Anime.js gdzie to możliwe)

### 6. Formatowanie i wyświetlanie danych
- Formatowanie timestampów na osi X
- Formatowanie wartości na osiach Y zgodnie z jednostkami
- Kolorowanie serii zgodnie z design systemem (pH - jeden kolor, mętność - drugi, etc.)
- Konfiguracja tooltipów aby pokazywały nazwę parametru, wartość, jednostkę i timestamp
- Dodawanie linii referencyjnych dla norm (jeśli zdefiniowane)

### 7. Responsywność
- Wykresy dostosowujące się do rozmiaru kontenera
- Panel kontrolny może zmieniać układ z poziomego na pionowy na małych ekranach
- Na bardzo małych ekranach: pokazywanie tylko jednego wykresu na raz z przełącznikiem między parametrami

## Konkretne zadania do wykonania
1. Wybrać i zintegrować bibliotekę wykresów (Chart.js, ApexCharts, Plotly.js lub własne rozwiązanie z Anime.js)
2. Utworzyć kontroler/route dla analizy i wykresów (np. `@app.route('/analytics')`)
3. Utworzyć szablon HTML dla strony wykresów
4. Zaimplementować logikę pobierania danych z backendu przy użyciu klienta API z filtrami
5. Zaimplementować komponent UI dla panelu kontrolnego (urządzenie, zakres czasu, typ wykresu, parametry)
6. Zaimplementować renderowanie wykresów przy użyciu wybranej biblioteki
7. Zaimplementować interaktywność wykresów (tooltipy, zoom, pan)
8. Zaimplementować stan ładowania i obsługę błędów
9. Zaimplementować mechanizm aktualizacji wykresów przy zmianie parametrów
10. Zaimplementować responsywny układ strony i wykresów
11. Dodawać odpowiednie klasy CSS zgodnie z design systemem
12. Jeśli wykorzystujemy Anime.js, dodać odpowiednie animacje przy ładowaniu danych lub zmianie wykresów
13. Napisać testy jednostkowe i integracyjne dla kontrolera i szablonu (zobacz sekcje 17 i 18)

## Wymagania techniczne
- Biblioteka wykresów (Chart.js, ApexCharts, Plotly.js lub podobna)
- Dostęp do klienta API z sekcji 06
- Jinja2 dla renderowania szablonów
- Opcjonalnie: biblioteka do obsługi dat (np. `python-dateutil`)
- Jeśli wykorzystujemy Anime.js: już dostępna w projekcie (do potwierdzenia w sekcji 03)

## Wymagania wizualne
- Wykresy powinny być czytelne i estetyczne
- Kolory serii powinny być zgodne z design systemem i wystarczająco kontrastowe
- Tooltipy powinny być wyraźne i nie zasłaniać ważnych części wykresu
- Osi wykresów powinny być wyraźnie oznaczone z jednostkami
- Legendy powinny być łatwe do odczytania
- Wykresy powinny mieć odpowiednie odstępy i marginesy
- Jeśli używamy animacji: powinny być subtelne i nie rozpraszające uwagi

## Pliki, które należy utworzyć lub zmodyfikować
- `app/routes.py` lub podobny - dodanie route dla analizy i wykresów
- `app/controllers/analytics.py` - nowy plik kontrolera (opcjonalnie)
- `app/templates/analytics/index.html` - nowy plik szablonu
- Komponenty UI do wykorzystania w szablonie (panel kontrolny, kontenery na wykresy)
- Pliki statyczne (CSS/JS) dla biblioteki wykresów i ewentualnych własnych stylizacji
- Jeśli wykorzystujemy własne rozwiązanie z Anime.js: pliki JavaScript z logiką wykresów

## Integrację z pozostałymi elementami systemu
- Strona wykresów i analizy będzie wykorzystywać:
  - Layout bazowy z sekcji 07
  - Komponenty UI z sekcji 07 i 14 (loading, empty state, error)
  - Klient API z sekcji 06 do pobierania danych
  - Mechanizm uwierzytelniania (sprawdzenie czy użytkownik jest zalogowany)
  - Nawigację z sekcji 07 (aktywny element w menu)
  - Animacje przejść z sekcji 13 (opcjonalnie)
  - Responsywność z sekcji 15
  - Anime.js z sekcji 13 (do animacji wykresów, jeśli wybrano tę opcję)
  - Obsługę błędów z sekcji 14 i 16
  - Dane mogą być wykorzystywane przez sekcję 11 (Device Status) do pokazywania podstawowych wykresów na kartach urządzeń

## Obsługę błędów i przypadków brzegowych
- Brak urządzeń przypisanych do użytkownika: pokazanie komunikatu zachęcającego do dodania pierwszego urządzenia
- Błąd połączenia z backendem: pokazanie komunikatu o problemach z połączeniem i możliwość ponowienia próby
- Brak danych dla wybranych filtrów: pokazanie komunikatu "Brak danych" zamiast pustego wykresu
- Nieprawidłowy zakres czasu: walidacja i komunikatu użytkownikowi
- Zbyt duża liczba punktów danych: implementacja próbkowania lub agregacji (np. średnie godzinowe) aby wykres pozostał responsywny
- Dane w nieoczekiwanym formacie: logowanie błędu i pokazanie komunikatu o problemie technicznym
- Problemy z biblioteką wykresów: łapnięcie wyjątków i pokazanie komunikatu użytkownikowi

## Testy wymagane do uznania sekcji za ukończoną
- Testy jednostkowe dla kontrolera/logiki pobierania i przygotowania danych do wykresów
- Testy integracyjne sprawdzające renderowanie strony wykresów z różnymi danymi wejściowymi
- Testy sprawdzające obsługę przypadków brzegowych (brak danych, błąd połączenia, nieprawidłowe parametry, itp.)
- Testy responsywności (sprawdzenie zachowania wykresów na różnych szerokościach ekranu)
- Testy interaktywności (sprawdzenie tooltipów, zoom, pan - jeśli możliwe do zautomatyzowania)
- Testy dostępności (sprawdzenie etykiet ARIA dla wykresów, nawigacji klawiaturą)

## Jednoznaczne kryteria akceptacji
- Strona analizy i wykresów jest dostępna po zalogowaniu pod odpowiednim URL (np. `/analytics`)
- Strona wykorzystuje layout bazowy z sekcji 07
- Strona pozwala na wybór urządzenia, zakres czasu, typu wykresu i parametrów do wyświetlenia
- Strona pobiera i wyświetla dane pomiarowe z backendu w formie interaktywnych wykresów
- Wykresy są responsywne i dostosowują się do rozmiaru kontenera
- Strona prawidłowo obsługuje stany ładowania, puste dane i błędy
- Strona jest łatwa w użyciu poprzez intuicyjny interfejs i nawigację

## Zależności od innych sekcji
- Zależna od: wszystkie poprzednie sekcje (01-09)
- Wymagana przez: sekcje które mogą potrzebować wizualizacji danych (np. sekcja 11 do szczegółowej analizy urządzeń)

## Warunki zakończenia prac
- Strona analizy i wykresów jest w pełni zaimplementowana i zintegrowana z layoutem
- Wykresy są poprawnie renderowane i interaktywne
- Wszystkie komponenty strony są stworzone i działają poprawnie
- Sekcja może być uznana za ukończoną po pozytywnej weryfikacji przez lead developer lub poprzez automated tests

## Informacje, które należy przekazać do kolejnych sekcji
- Przykłady użycia klienta API do pobierania danych pomiarowych z filtrami
- Formaty danych zwracane przez funkcje API (po mapowaniu z sekcji 06)
- Wzorce przygotowywania danych do wykresów (konwersja timestampów, agrupowanie, etc.)
- Informacje o klasach CSS i identyfikatorach używanych w stronie (dla stylizacji w sekcji 03)
- Przykłady implementacji stanu ładowania i obsługi błędów
- Przykłady implementacji komponentów UI dla panelu kontrolnego
- Informacje o zintegrowanej bibliotece wykresów i sposobie jej użycia
- Jeśli wykorzystujemy Anime.js do animacji: przykłady animacji wykresów

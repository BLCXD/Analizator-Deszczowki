# 08_DASHBOARD_OVERVIEW.md
## Główny dashboard, aktualne pomiary, stan systemu, ostatnia aktualizacja i podsumowanie danych

## Cel sekcji
Zaimplementowanie głównej strony dashboardu, która przedstawia aktualne pomiary z wszystkich urządzeń użytkownika, stan systemu, informacje o ostatniej aktualizacji oraz podsumowanie najważniejszych danych. Strona ta będzie stroną główną po zalogowaniu użytkownika.

## Kontekst i zależności
Ta sekcja zależy od:
- 01_PROJECT_ANALYSIS.md (zrozumienie wymagań i danych)
- 02_ARCHITECTURE.md (wzorzec architektoniczny)
- 03_DESIGN_SYSTEM.md (stylizacja komponentów)
- 04_ENVIRONMENT_AND_CONFIGURATION.md (konfiguracja)
- 05_FLASK_FOUNDATION.md (routing i struktura)
- 06_BACKEND_INTEGRATION.md (pobieranie danych)
- 07_SHARED_LAYOUT_AND_NAVIGATION.md (layout i nawigacja)
Nie ma zależności od innych sekcji implementacyjnych, ale jest wymagana dla sekcji, które mogą wyświetlać podobne podsumowania (np. strony szczegółowe urządzeń).

## Stan początkowy
- Katalog `flask-frontend-user` zawiera podstawową strukturę Flaska, szablony layoutu i klienta API
- Brak istniejącej strony głównej dashboardu
- Brak komponentów wyświetlających aktualne pomiary

## Szczegółowy zakres implementacji
### 1. Struktura strony
- Utworzenie kontrolera Flask dla głównej strony w `app/controllers/dashboard.py` lub bezpośrednio w `app/routes.py`
- Utworzenie szablonu HTML `app/templates/dashboard/index.html` lub `app/templates/dashboard.html`
- Strona będzie wykorzystywać layout bazowy z sekcji 07

### 2. Komponenty strony głównej
Strona główna dashboardu będzie zawierać następujące sekcje:

#### Panel powitalny
- Powitanie użytkownika po imieniu (jeśli dostępne)
- Data i czas ostatniej aktualizacji danych
- Status połączenia z backendem (zielony/czerwony kółko + tekst)

#### Podsumowanie urządzeń
- Liczba łącznie urządzeń przypisanych do użytkownika
- Liczba urządzeń aktywnych (wysyłających dane w ostatnich X minutach)
- Liczba urządzeń z problemami (brak danych, błąd połączenia)
- Wykres słupkowy lub ikony przedstawiające stan urządzeń (opcjonalnie, w zależności od miejsca)

#### Aktualne pomiary
- Tabela lub siatka kafelków przedstawiających najnowsze pomiary z każdego urządzenia
- Dla każdego urządzenia pokazujemy:
  - Nazwa urządzenia
  - Lokalizacja (jeśli dostępna)
  - Timestamp najnowszego pomiaru
  - Wartości pomiarów: pH, mętność, przepływ, temperatura (jednostki zgodnie z konfiguracją)
  - Wskaźnik stanu pomiaru (np. kolor tła kafelka wskazujący czy wartości są w normie)
- Jeśli brak danych dla urządzenia: pokazanie komunikatu "Brak danych" lub "Ostatni pomiar: [data]"
- Jeśli urządzenie jest offline: pokazanie ostrzeżenia o braku połączenia

#### Podsumowanie systemu
- Informacje o stanie systemu (jeśli dostępne przez backend):
  - Czas pracy systemu
  - Zużycie zasobów (opcjonalnie)
  - Liczba przetworzonych pomiarów dzisiaj
  - Alerty systemowe (opcjonalnie)
- Jeśli backend nie udostępnia szczegółowych informacji o systemu: pokazanie podstawowych informacji o połączeniu

#### Szybkie akcje
- Przyciski do najczęściej wykonywanych działań:
  - "Dodaj nowe urządzenie" (przekierowanie do sekcji 12)
  - "Zobacz wszystkie pomiary" (przekierowanie do sekcji 09)
  - "Zobacz analizę i wykresy" (przekierowanie do sekcji 10)
  - "Ustawienia" (przekierowanie do sekcji 12)

### 3. Pobieranie danych
- Wykorzystanie klienta API z sekcji 06 do pobierania:
  - Lista urządzeń: `GET /api/v1/devices/`
  - Najnowsze pomiary dla wszystkich urządzeń: można pobrać indywidualnie dla każdego urządzenia przez `GET /api/v1/measurements/{device_id}/latest` lub zoptymalizować poprzez jedno wywołanie jeśli backend wspiera
  - Informacje o stanie systemu: zależnie od dostępnych endpointów (sprawdzić w backendzie)
- Implementacja mechanizmu odświeżania danych (np. co 30 sekund) lub odświeżanie przy interakcji użytkownika
- Obsługa stanu ładowania podczas pobierania danych (komponent z sekcji 14)
- Obsługa błędów podczas pobierania danych (komunikaty użytkownikowi)

### 4. Formatowanie i wyświetlanie danych
- Formatowanie timestampów do czytelnej postaci (np. "5 min temu", "dzisiaj 14:30")
- Kolorowanie wartości pomiarów w zależności od tego czy są w normie:
  - Zielony: wartości w normie
  - Żółty: wartości poza normą ale nie krytyczne
  - Czerwony: wartości krytyczne wymagające uwagi
- Normy mogą być stałe lub konfigurowalne (do ustalenia czy backend udostępnia takie informacje)
- Skracanie długich nazw urządzeń lub lokalizacji z dodaniem podpowiedzi przy pełnej nazwie

### 5. Responsywność
- Układ siatkowy lub flexboxowy który dostosowuje się do szerokości ekranu:
  - Na dużych ekranach: wiele kolumn z kafelkami urządzeń
  - Na średnich ekranach: dwie kolumny
  - Na małych ekranach: jedna kolumna (kafelki pełnej szerokości)
- Panel podsumowania może zmieniać układ z poziomego na pionowy na małych ekranach

## Konkretne zadania do wykonania
1. Utworzyć kontroler/dashboard route dla strony głównej (np. `@app.route('/')` lub `@app.route('/dashboard')`)
2. Utworzyć szablon HTML dla strony głównej dashboardu
3. Zaimplementować logikę pobierania danych z backendu przy użyciu klienta API
4. Zaimplementować formatowanie danych do wyświetlania (daty, wartości, stany)
5. Utworzyć komponenty UI dla wyświetlania kafelków urządzeń i podsumowań
6. Zaimplementować stan ładowania i obsługę błędów
7. Zaimplementować mechanizm odświeżania danych (opcjonalnie, można zacząć od ręcznego odświeżania)
8. Zaimplementować responsywny układ strony
9. Dodawać odpowiednie klasy CSS zgodnie z design systemem
10. Napisać testy jednostkowe i integracyjne dla kontrolera i szablonu (zobacz sekcje 17 i 18)

## Wymagania techniczne
- Dostęp do klienta API z sekcji 06
- Jinja2 dla renderowania szablonów
- Brak dodatkowych bibliotek wymaganych dla podstawowej funkcjonalności
- Opcjonalnie: biblioteka do formatowania dat (np. `python-dateutil` lub wbudowane możliwości Jinja)

## Wymagania wizualne
- Strona główna powinna być przejrzysta i nie przytłaczająca informacjami
- Najważniejsze informacje (stan urządzeń, aktualne pomiary) powinny być wyraźnie widoczne
- Użycie kolorów zgodnie z design systemem do wskazywania stanów
- Odpowiednie odstępy i wyrównanie zgodne z siatką zdefiniowaną w design systemie
- Czcionki i rozmiary tekstu zgodne z typografią z design systemu
- Ikony lub wizualne wskaźniki stanów (opcjonalnie, jeśli wspierane przez design system)

## Pliki, które należy utworzyć lub zmodyfikować
- `app/routes.py` lub podobny - dodanie route dla strony głównej
- `app/controllers/dashboard.py` - nowy plik kontrolera (opcjonalnie, można umieścić w routes)
- `app/templates/dashboard/index.html` - nowy plik szablonu
- `app/templates/dashboard.html` - alternatywna lokalizacja szablonu
- Komponenty UI do wykorzystania w szablonie (można utworzyć w `app/templates/components/` lub wykorzystać istniejące z sekcji 07)
- Pliki statyczne (CSS/JS) jeśli potrzebne dla konkretnych efektów na tej stronie

## Integrację z pozostałymi elementami systemu
- Strona główna będzie wykorzystywać:
  - Layout bazowy z sekcji 07
  - Komponenty UI z sekcji 07 i 14 (loading, empty state, error)
  - Klient API z sekcji 06 do pobierania danych
  - Mechanizm uwierzytelniania (sprawdzenie czy użytkownik jest zalogowany)
  - Nawigację z sekcji 07 (aktywny element w menu)
  - Animacje przejść z sekcji 13 (opcjonalnie)
  - Responsywność z sekcji 15
  - Obsługę błędów z sekcji 14 i 16

## Obsługę błędów i przypadków brzegowych
- Brak urządzeń przypisanych do użytkownika: pokazanie komunikatu zachęcającego do dodania pierwszego urządzenia
- Brak danych pomiarowych: pokazanie komunikatów "Brak danych" dla każdego urządzenia lub ogólnego komunikatu
- Błąd połączenia z backendem: pokazanie komunikatu o problemach z połączeniem i możliwość ponowienia próby
- Częściowe dane (nie udało się pobrać danych dla niektórych urządzeń): pokazanie dostępnych danych z ostrzeżeniem o braku danych dla niektórych urządzeń
- Dane w nieoczekiwanym formacie: logowanie błędu i pokazanie komunikatu o problemie technicznym
- Duża liczba urządzeń: implementacja paginacji lub lazy loading dla listy urządzeń (jeśli konieczne)
- Bardzo stare dane: ostrzeżenie że dane mogą być nieaktualne

## Testy wymagane do uznania sekcji za ukończoną
- Testy jednostkowe dla kontrolera/logiki pobierania i formatowania danych
- Testy integracyjne sprawdzające renderowanie strony głównej z różnymi danymi wejściowymi
- Testy sprawdzające obsługę przypadków brzegowych (brak danych, błąd połączenia, itp.)
- Testy responsywności (sprawdzenie układu na różnych szerokościach ekranu)
- Testy dostępności (sprawdzenie semantycznego HTML, etykiet ARIA)

## Jednoznaczne kryteria akceptacji
- Strona główna jest dostępna po zalogowaniu pod odpowiednim URL (np. `/` lub `/dashboard`)
- Strona wykorzystuje layout bazowy z sekcji 07
- Strona wyświetla powitanie użytkownika i informacje o zalogowaniu
- Strona pokazuje listę urządzeń użytkownika z ich najnowszymi pomiarami
- Strona pokazuje stan połączenia z backendem i czas ostatniej aktualizacji
- Strona jest responsywna i działa na szerokościach od 320px do 1920px
- Strona prawidłowo obsługuje stany ładowania, puste dane i błędy
- Strona jest łatwa w użyciu poprzez intuicyjny interfejs i nawigację

## Zależności od innych sekcji
- Zależna od: wszystkie poprzednie sekcje (01-07)
- Wymagana przez: sekcje które mogą wyświetlać podobne podsumowania (opcjonalnie, nie jest ścisłą zależnością dla dalszych sekcji)

## Warunki zakończenia prac
- Strona główna dashboardu jest w pełni zaimplementowana i zintegrowana z layoutem
- Wszystkie komponenty strony są stworzone i działają poprawnie
- Strona prawidłowo pobiera i wyświetla dane z backendu
- Sekcja może być uznana za ukończoną po pozytywnej weryfikacji przez lead developer lub poprzez automated tests

## Informacje, które należy przekazać do kolejnych sekcji
- Przykłady użycia klienta API do pobierania konkretnych typów danych
- Formaty danych zwracane przez funkcje API (po mapowaniu z sekcji 06)
- Wzorce tworzenia komponentów wyświetlających dane pomiarowe
- Informacje o klasach CSS i identyfikatorach używanych w stronie (dla stylizacji w sekcji 03)
- Przykłady implementacji stanu ładowania i obsługi błędów

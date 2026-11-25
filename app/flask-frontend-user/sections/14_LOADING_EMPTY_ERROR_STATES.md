# 14_LOADING_EMPTY_ERROR_STATES.md
## Stany ładowania, brak danych, błędy, nieaktualne pomiary i niedostępność backendu

## Cel sekcji
Zaimplementowanie spójnych stanów interfejsu użytkownika dla różnych sytuacji które mogą wystąpić podczas pracy aplikacji: ładowania danych, braku danych, błędów połączenia lub przetwarzania, nieaktualnych danych oraz niedostępności usług backendowych. Sekcja zapewnia, że użytkownik jest zawsze informowany o stanie systemu i może odpowiednio reagować.

## Kontekst i zależności
Ta sekcja zależy od:
- 01_PROJECT_ANALYSIS.md (zrozumienie wymagań projektu)
- 02_ARCHITECTURE.md (wzorzec architektoniczny)
- 03_DESIGN_SYSTEM.md (kolory, typografia, stylizacja komponentów)
- 04_ENVIRONMENT_AND_CONFIGURATION.md (konfiguracja)
- 05_FLASK_FOUNDATION.md (struktura aplikacji)
- 06_BACKEND_INTEGRATION.md (do identyfikowania kiedy występują stany)
- 07_SHARED_LAYOUT_AND_NAVIGATION.md (gdzie komponenty będą używane)
- 13_ANIMEJS_AND_INTERACTIONS.md (opcjonalnie, dla animowanych stanów)
Nie ma zależności od innych sekcji implementacyjnych, ale jest wykorzystywana przez wszystkie sekcje które pobierają dane lub wykonują akcje wymagające komunikacji z backendem.

## Stan początkowy
- Katalog `flask-frontend-user` zawiera podstawową strukturę Flaska, szablony layoutu i klienta API
- Brak zdefiniowanych komponentów stanów ładowania, pustych danych lub błędów
- Brak spójnego podejścia do obsługi różnych stanów aplikacji

## Szczegółowy zakres implementacji
### 1. Stany ładowania
Komponenty wskazujące że aplikacja jest w trakcie wykonywania akcji (pobieranie danych, zapisywanie, etc.)

#### Wskaźnik ładowania strony
- Full-screen overlay lub pasek u góry strony podczas początkowego ładowania
- Lub wskaźnik w miejscu gdzie ładowane są konkretne dane

#### Wskaźnik ładowania zawartości
- Spinning indicator lub pasek postępu w miejscu gdzie ładowane są dane
- Skeleton UI - placeholdery które imitują układ końcowej zawartości podczas ładowania
- Tekst informujący co jest ładowane (np. "Ładowanie pomiarów...", "Pobieranie listy urządzeń...")

#### Wskaźnik ładowania akcji
- Animowany przycisk który pokazuje stan ładowania podczas wykonywania akcji (np. zapisywanie ustawień)
- Tekst przycisku zmienia się na "Zapisywanie..." lub pokazuje spinner obok tekstu

### 2. Stany braku danych
Komponenty wskazujące że nie ma danych do wyświetlenia w danym kontekście

#### Ogólny stan braku danych
- Ilustracja lub ikona wskazująca brak danych
- Tekst wyjaśniający dlaczego brak danych (np. "Brak pomiarów do wyświetlenia")
- Opcjonalnie: przycisk do działania które może doprowadzić do pojawienia się danych (np. "Dodaj pierwsze urządzenie")

#### Specyficzne stany braku danych
- Brak urządzeń: komunikat zachęcający do dodania pierwszego urządzenia
- Brak pomiarów dla wybranego urządzenia/czasu: informacja że brak danych w wybranym zakresie
- Brak wyników wyszukiwania/filtrowania: informacja że brak rekordów spełniających kryteria

### 3. Stany błędów
Komponenty wskazujące że wystąpił błąd podczas wykonywania akcji

#### Błędy połączenia
- Brak połączenia z backendem
- Timeout połączenia
- Problemy z siecią
- Komponent powinien jasno wskazywać że problem jest po stronie połączenia

#### Błędy przetwarzania
- Błąd 400 (złe żądanie) - np. nieprawidłowe dane wejściowe
- Błąd 401 (nieautoryzowany) - problem z uwierzytelnianiem
- Błąd 403 (zabroniono) - brak uprawnień
- Błąd 404 (nie znaleziono) - zasób nie istnieje
- Błąd 422 (nieprzetwarzalny encja) - błąd walidacji
- Błąd 5xx (błąd serwera) - problem po stronie backendu

#### Błędy walidacji formularzy
- Wskazanie konkretnych pól które zawierają błędne dane
- Tekst wyjaśniający co jest nie tak
- Opcjonalnie: sugestia jak poprawić błąd

### 4. Stany nieaktualnych danych
Komponenty wskazujące że dostępne dane mogą być nieaktualne lub przestarzałe

#### Wskaźnik świeżości danych
- Czas od ostatniej aktualizacji danych
- Kolorowy wskaźnik (zielony = świeże, żółty = lekko przestarzałe, czerwony = bardzo przestarzałe)
- Tekst informujący kiedy dane były ostatnio aktualizowane
- Przycisk do ręcznego odświeżania danych

#### Ostrzeżenie o nieaktualnych danych
- Pokazywane gdy dane są starsze niż określony próg (np. 5 minut)
- Może być wyświetlane jako banner lub toast notification

### 5. Stany niedostępności backendu
Komponenty wskazujące że backend jest całkowicie niedostępny lub w trybie maintenance

#### Tryb offline
- Informacja że aplikacja nie może połączyć się z backendem
- Możliwość wykonywania ograniczonych działań offline (jeśli implementowane)
- Przycisk do ponowienia próby połączenia

#### Konserwacja systemu
- Informacja że system jest w trakcie konserwacji
- Szacowany czas zakończenia konserwacji (jeśli dostępny)
- Możliwość pozostawienia powiadomienia gdy system wróci do działania

## Konkretne zadania do wykonania
1. Utworzyć katalog `app/templates/components/` jeśli nie istnieje
2. Utworzyć komponent stanu ładowania: `app/templates/components/loading.html`
3. Utworzyć komponent stanu braku danych: `app/templates/components/empty_state.html`
4. Utworzyć komponent stanu błędu: `app/templates/components/error.html`
5. Utworzyć komponent stanu nieaktualnych danych: `app/templates/components/stale_data.html` (opcjonalnie)
6. Utworzyć komponent stanu niedostępności backendu: `app/templates/components/offline.html` (opcjonalnie)
7. Zaimplementować warianty komponentów dla różnych rozmiarów i kontekstów (np. mały wskaźnik ładowania dla przycisku, pełny ekran dla strony)
8. Zaimplementować mechanizm pokazywania/ukrywania komponentów w szablonach (zmienna kontrolująca stan)
9. Zaimplementować animowane wersje komponentów wykorzystując Anime.js z sekcji 13 (opcjonalnie)
10. Zaimplementować toast notifications lub flash messages dla transientnych komunikatów
11. Dodawać odpowiednie klasy CSS zgodnie z design systemem
12. Napisać testy jednostkowe i integracyjne sprawdzające renderowanie komponentów w różnych stanach (zobacz sekcje 17 i 18)

## Wymagania techniczne
- Jinja2 dla renderowania szablonów komponentów
- Dostęp do zmiennych kontrolujących stan w szablonach (przekazywane z kontrolerów)
- Opcjonalnie: biblioteka do toast notifications (lub własna implementacja)
- Jeśli wykorzystujemy animacje: już zintegrowana Anime.js z sekcji 13

## Wymagania wizualne
- Stany ładowania:
  - Subtelne animowane wskaźniki (spinning, pulsing bars)
  - Kolory zgodne z design systemem (najczęściej kolory akcentu lub neutralne)
  - Rozmiar odpowiedni do kontekstu (mały dla przycisków, większy dla sekcji)

- Stany braku danych:
  - Ilustracje lub ikony w stylu linii (line art) lub flat design
  - Tekst w przyjaznym, pomocnym tonie
  - Opcjonalny przycisk działania zgodny z design systemem

- Stany błędów:
  - Kolor ostrzegawczy (czerwony lub pomarańczowy zgodnie z design systemem)
  - Ikona wykrzyknika lub ostrzeżenia
  - Jasny, zrozumiały opis problemu
  - Opcjonalnie: przycisk do ponowienia próby lub działania naprawczego

- Stany nieaktualnych danych:
  - Kolor ostrzegawczy (żółty lub pomarańczowy)
  - Ikona zegara lub ostrzeżenia
  - Jasny komunikat o tym że dane mogą być nieaktualne
  - Przycisk do odświeżania danych

- Stany niedostępności backendu:
  - Kolor błędowy (czerwony)
  - Ikona chmurki z przekreśleniem lub podobna
  - Jasna informacja o problemie z połączeniem
  - Przycisk do ponowienia próby połączenia

## Pliki, które należy utworzyć lub zmodyfikować
- `app/templates/components/loading.html` - nowy plik
- `app/templates/components/empty_state.html` - nowy plik
- `app/templates/components/error.html` - nowy plik
- `app/templates/components/stale_data.html` - nowy plik (opcjonalnie)
- `app/templates/components/offline.html` - nowy plik (opcjonalnie)
- Warianty komponentów: `loading-small.html`, `loading-page.html`, `empty-state-smaller.html` etc. (opcjonalnie)
- Szablony stron - dodanie miejsc gdzie komponenty będą używane
- Pliki statyczne (CSS/JS) jeśli potrzebne dla konkretnych efektów lub animacji

## Integrację z pozostałymi elementami systemu
- Komponenty stanów będą wykorzystywane przez:
  - Sekcję 07 (Shared Layout) - e.g. wskaźnik ładowania w nagłówku
  - Sekcję 08 (Dashboard Overview) - stany ładowania dla pomiarów urządzeń
  - Sekcję 09 (Measurements and History) - stany ładowania, puste dane, błędy dla tabeli
  - Sekcję 10 (Charts and Analytics) - stany ładowania dla danych wykresów
  - Sekcję 11 (Device Status and Diagnostics) - stany ładowania dla danych urządzenia
  - Sekcję 12 (Settings and Additional Features) - stany ładowania dla ustawień
  - Sekcję 13 (AnimeJS and Interactions) - do animacji pojawiania się komponentów
  - Sekcję 15 (Responsiveness and Accessibility) - zapewnienie że komponenty są dostępne
  - Sekcję 16 (Security and Reliability) - konkretne typy błędów (auth, timeout, etc.)

## Obsługę błędów i przypadków brzegowych
- Konflikt stanów: priorytetyzacja (np. błąd połączenia ma wyższy priorytet niż stan ładowania)
- Częste przejścia między stanami: mechanizm debouncing aby uniknąć migania
- Brak danych w stanie ładowania: pokazanie stanu ładowania aż do określenia czy są dane
- Błąd podczas ładowania: przejście ze stanu ładowania do stanu błędu
- Odzyskanie po błędzie: możliwość przejścia z stanu błędu z powrotem do ładowania po ponowieniu próby
- Bardzo długie ładowanie: możliwość pokazania dodatkowych informacji lub sugestii
- Ekran bardzo mały: adaptacja komponentów stanów do małej powierzchni

## Testy wymagane do uznania sekcji za ukończoną
- Testy jednostkowe dla szablonów komponentów (sprawdzenie że renderują się poprawnie z różnymi zmiennymi)
- Testy integracyjne sprawdzające komponenty w kontekście rzeczywistych stron
- Testy sprawdzające przejścia między różnymi stanami (ładowanie → sukces, ładowanie → błąd, etc.)
- Testy responsywności (sprawdzenie jak komponenty wyglądają na różnych szerokościach ekranu)
- Testy dostępności (sprawdzenie etykiet ARIA, kontrastu kolorów, nawigacji klawiaturą)
- Testy animacji (jeśli wykorzystujemy animowane komponenty)

## Jednoznaczne kryteria akceptacji
- Komponent stanu ładowania jest łatwy w użyciu poprzez prosty includowanie w szablonach
- Komponent stanu braku danych dostarcza użyteczne informacje i opcjonalnie sugeruje działanie
- Komponent stanu błędu jasno komunikuje problem i możliwe kroki naprawcze
- Komponenty są responsywne i działają na szerokościach od 320px do 1920px
- Komponenty są dostępne (wystarczający kontrast, semantyczny HTML, etykiety ARIA gdzie odpowiednie)
- Komponenty można łatwo stylizować zgodnie z design systemem poprzez klasy CSS
- Sekcja może być uznana za ukończoną po pozytywnej weryfikacji przez lead developer lub poprzez automated tests

## Zależności od innych sekcji
- Zależna od: wszystkie poprzednie sekcje (01-13) ponieważ może być wykorzystywana w dowolnym miejscu w interfejsie
- Wymagana przez: sekcje które pobierają dane lub wykonują akcje wymagające komunikacji z backendem (08, 09, 10, 11, 12)

## Warunki zakończenia prac
- Wszystkie wymagane komponenty stanów są stworzone i zintegrowane z szablonami
- Komponenty są łatwe w użyciu przez deweloperów poprzez prosty mechanizm includowania
- Komponenty są responsywne i dostępne
- Sekcja może być uznana za ukończoną po pozytywnej weryfikacji przez lead developer lub poprzez automated tests

## Informacje, które należy przekazać do kolejnych sekcji
- Interfejs komponentów stanów (jak je includować i jakie zmienne przyjmują)
- Przykłady użycia każdego typu komponentu w różnych kontekstach
- Informacje o klasach CSS i identyfikatorach używanych w komponentach
- Przykłady implementacji mechanizmu pokazywania/ukrywania komponentów
- Informacje o dostępnych wariantach komponentów (rozmiary, style)
- Jeśli wykorzystujemy animacje: przykłady animowanych wersji komponentów

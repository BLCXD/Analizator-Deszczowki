# 13_ANIMEJS_AND_INTERACTIONS.md
## Animacje Anime.js, przejścia, interakcje, dostępność i obsługa prefers-reduced-motion

## Cel sekcji
Zaimplementowanie subtelnych i celowych animacji przy użyciu biblioteki Anime.js oraz innych interakcji użytkownika, które poprawiają doświadczenie użytkownika bez rozpraszania uwagi ani utrudniania dostępu. Sekcja zapewnia, że animacje są używane odpowiednio i szanują preferencje użytkownika dotyczące redukcji ruchu.

## Kontekst i zależności
Ta sekcja zależy od:
- 01_PROJECT_ANALYSIS.md (zrozumienie wymagań projektu)
- 02_ARCHITECTURE.md (wzorzec architektoniczny)
- 03_DESIGN_SYSTEM.md (zasady animacji i przejść w design systemie)
- 04_ENVIRONMENT_AND_CONFIGURATION.md (konfiguracja)
- 05_FLASK_FOUNDATION.md (struktura aplikacji)
- 07_SHARED_LAYOUT_AND_NAVIGATION.md (layout i komponenty które mogą być animowane)
Nie ma zależności od innych sekcji implementacyjnych, ale może być wykorzystywana przez wszystkie sekcje które zawierają elementy interfejsu użytkownika.

## Stan początkowy
- Katalog `flask-frontend-user` zawiera podstawową strukturę Flaska, szablony layoutu i klienta API
- Brak zintegrowanej biblioteki Anime.js
- Brak zdefiniowanych animacji lub interakcji

## Szczegółowy zakres implementacji
### 1. Integracja Anime.js
- Dodanie biblioteki Anime.js do projektu poprzez:
  - Pobranie z CDN (np. `<script src="https://cdn.jsdelivr.net/npm/animejs@3.2.1/lib/anime.min.js"></script>`)
  - Lub instalacja poprzez npm/yarn i włączenie do bundla jeśli używamy narzędzi do budowania frontendowego
- Utworzenie pliku `app/static/js/anime.js` lub podobnego dla własnych funkcji pomocniczych
- Dodanie inicjalizacji Anime.js w szablonach lub osobnym pliku JavaScript

### 2. Zasady użycia animacji
Animacje będą używane zgodnie z następującymi zasadami:
- **Celowość**: każda animacja musi mieć jasny cel (wskazanie zmiany stanu, przyciągnięcie uwagi do ważnego elementu, zapewnienie feedbacku)
- **Subtelność**: animacje będą subtelne i nie rozpraszające uwagi od głównej treści
- **Wydajność**: animacje będą zoptymalizowane aby nie obniżać wydajności, szczególnie na słabszych urządzeniach
- **Dostępność**: animacje będą szanować preferencję `prefers-reduced-motion` i mogą być wyłączone
- **Nie zastępowanie funkcjonalności**: animacje nie będą zastępować rzeczywistej funkcjonalności ani nie będą jedynym sposobem przekazania informacji

### 3. Konkretne animacje i interakcje
Do zaimplementowania w zależności od potrzeb poszczególnych sekcji:

#### Przejścia między stronami
- Subtelne fade-in/fade-out przy ładowaniu nowej strony (z wykorzystaniem Turbo lub podobnego jeśli dostępnego, lub własna implementacja z użyciem historii przeglądarki)
- Lub proste przejścia opacity przy montowaniu komponentów (jeśli używamy podejścia opartego na składnikach w Flasku)

#### Stan ładowania
- Animowane wskaźniki ładowania (spinning, pulsing bars)
- Animated skeleton screens podczas ładowania danych
- Pulse lub shimmer efekty na elementach które są w trakcie ładowania

#### Interakcje z przyciskami
- Subtelne scale lub przyciemnianie przy najechaniu kursorem
- Efekt "wciśnięcia" przy kliknięciu
- Animated loading state wewnątrz przycisku podczas wykonywania akcji

#### Formularze i pola input
- Animated underline przy fokusu na polu input
- Transition przy pojawianiu się błędów walidacji
- Animated checkbox i radio button przy zmianie stanu
- Animated select dropdown przy rozwijaniu i zwijaniu

#### Karty i komponenty
- Subtelne uniesienie lub shadow change przy najechaniu na kartę
- Animated reveal przy pokazowywaniu ukrytej informacji
- Toggle animation dla akordeonów i rozwijanych sekcji

#### Powiadomienia i alerts
- Animated wjazd i wyjazd (slide lub fade)
- Pulse lub shake przy ważnych powiadomieniach (błędy krytyczne)
- Animated progress bar w powiadomieniach o postępie

#### Wykresy i wykresy danych (sekcja 10)
- Animated wykresy przy ładowaniu danych (linia rysuje się, słupki wyrastają)
- Animated transitions przy zmianie danych lub parametrów
- Animated tooltipy przy pojawianiu się i znikaniu
- Animated punkt podkreślony przy najechaniu na punkt danych

#### Dashboard i przegląd urządzeń (sekcje 08, 11)
- Animated liczniki przy zmianie wartości
- Animated ikony statusu przy zmianie stanu urządzenia
- Animated wykresy sparkline na kartach urządzeń

### 4. Obsługa prefers-reduced-motion
- Szanowanie preferencji użytkownika ustawionej w systemie operacyjnym lub przeglądarce
- Implementacja mechanizmu wykrywania `prefers-reduced-motion` poprzez:
  - CSS media query: `@media (prefers-reduced-motion: reduce)`
  - JavaScript: `window.matchMedia('(prefers-reduced-motion: reduce)')`
- Quando preferencja jest ustawiona na reduce:
  - Wyłączenie wszystkich nieistotnych animacji
  - Zachowanie jedynie animacji które są krytyczne dla zrozumienia interfejsu (np. błędnego stanu wymagającego uwagi)
  - Zachowanie natychmiastowych przejść stanowych bez animacji

### 5. Dostępność interakcji
- Wszystkie interaktywne elementy muszą być obsługiwalne klawiaturą
- Animacje nie mogą utrudniać obsługi klawiaturą ani czytników ekranu
- Skupienie fokus musi być logiczne i przewidywalne
- Nie można wykorzystywać wyłącznie animacji do przekazania krytycznej informacji (musi być także przekazana w innej formie)

### 6. Wydajność animacji
- Używanie właściwości które można animować w sposób efektywny (transform, opacity)
- Unikanie animacji które powodują reflow lub repaint całej strony
- Używanie `will-change` ostrożnie tylko dla elementów które rzeczywiście będą animowane
- Limitowanie liczby jednocześnie animowanych elementów
- Używanie `requestAnimationFrame` gdzie to możliwe dla własnych animacji

## Konkretne zadania do wykonania
1. Zintegrować bibliotekę Anime.js z projektem (poprzez CDN lub lokalną kopię)
2. Utworzyć plik `app/static/js/anime-helpers.js` z funkcjami pomocniczymi dla typowych animacji
3. Utworzyć plik `app/static/css/animations.css` z klasami CSS dla typowych animacji (opcjonalnie, można wszystko zrobić w JavaScript)
4. Zaimplementować mechanizm wykrywania i szanowania `prefers-reduced-motion`
5. Zaimplementować animowane wskaźniki ładowania (do wykorzystania w sekcji 14)
6. Zaimplementować animacje przycisków i formularzy
7. Zaimplementować animacje przejść między stanami (pokazywanie/ukrywanie komponentów)
8. Zaimplementować animacje dla powiadomienia i alertów (do wykorzystania w sekcji 14)
9. Zaimplementować podstawowe animacje wykresów jeśli wykorzystujemy proste rozwiązanie lub potrzebujemy dodatkowych efektów
10. Zaimplementować animacje kart urządzeń i komponentów statusu
11. Dodawać odpowiednie komentarze w kodzie wskazujące gdzie animacje są używane i dlaczego
12. Napisać testy jednostkowe i integracyjne sprawdzające obecność i prawidłowe działanie animacji (zobacz sekcje 17 i 18)

## Wymagania techniczne
- Biblioteka Anime.js (wersja 3.x lub nowsza)
- Miejsce na przechowywanie własnych funkcji pomocniczych (pliki JS w `app/static/js/`)
- Opcjonalnie: własne klasy CSS dla animacji (pliki CSS w `app/static/css/`)
- Brak dodatkowych bibliotek wymaganych jeśli używamy samego Anime.js

## Wymagania wizualne
- Animacje będą subtelne i profesjonalne
- Czas trwania animacji: zazwyczaj między 150ms a 400ms dla większości efektów
- Funkcje przyspieszenia: głównie `ease-in-out` lub `ease-out` dla naturalnego ruchu
- Kolory animowanych elementów będą zgodne z design systemem
- Animacje nie będą zmieniać layoutu strony w sposób który mógłby spowodować przesunięcie innych elementów

## Pliki, które należy utworzyć lub zmodyfikować
- `app/static/js/anime.js` lub podobny - biblioteka Anime.js (poprzez CDN nie wymaga lokalnego pliku)
- `app/static/js/anime-helpers.js` - nowy plik z funkcjami pomocniczymi
- `app/static/css/animations.css` - nowy plik z klasami CSS dla animacji (opcjonalnie)
- Szablony HTML - dodanie odwołań do plików JS i CSS
- Konkretne komponenty - dodanie klas i atrybutów potrzebnych do animacji
- `app/templates/base.html` - dodanie skryptów Anime.js i własnych funkcji

## Integrację z pozostałymi elementami systemu
- Animacje mogą być wykorzystywane przez:
  - Sekcję 07 (Shared Layout) - animacje nagłówka, menu nawigacyjnego
  - Sekcję 08 (Dashboard Overview) - animacje liczników, kafelków urządzeń
  - Sekcję 09 (Measurements and History) - animacje tabeli, filtrów, przycisków
  - Sekcję 10 (Charts and Analytics) - animacje wykresów, tooltipów, kontrolek
  - Sekcję 11 (Device Status and Diagnostics) - animacje kart urządzeń, statusów, mini-wykresów
  - Sekcję 12 (Settings and Additional Features) - animacje formularzy, przełączników, przycisków
  - Sekcję 14 (Loading, Empty, Error States) - animowane wskaźniki ładowania, pojawianie się komunikatów
  - Sekcję 15 (Responsiveness and Accessibility) - zapewnienie że animacje nie utrudniają dostępu
  - Sekcję 16 (Security and Reliability) - animacje związane z logowaniem, błędami uwierzytelniania

## Obsługę błędów i przypadków brzegowych
- Biblioteka Anime.js nie ładuje się: graceful degradation - interfejs działa bez animacji
- Błąd w kodzie animacji: łapnięcie wyjątków i kontynuowanie bez animacji dla danego elementu
- Animacje powodujące problemy wydajnościowe: możliwość wyłączenia przez zmienną konfiguracyjną lub automatyczne wykrywanie słabej wydajności
- Konflikt z innymi bibliotekami JavaScript: izolacja i przestrzenie nazw dla własnych funkcji
- Użytkownik wyłączył JavaScript: podstawowa funkcjonalność bez animacji (jakiekolwiek krytyczne informacje przekazane również bez JS)

## Testy wymagane do uznania sekcji za ukończoną
- Testy jednostkowe dla własnych funkcji pomocniczych Anime.js
- Testy integracyjne sprawdzające czy animacje są wykonywane gdzie powinny (np. przyciski mają efekt najechania)
- Testy sprawdzające szanowanie `prefers-reduced-motion` (animacje wyłączone gdy preferencja ustawiona)
- Testy dostępności (sprawdzenie że animacje nie utrudniają nawigacji klawiaturą ani czytników ekranu)
- Testy wydajnościowe (sprawdzenie że animacje nie powodują znaczących spadków FPS)

## Jednoznaczne kryteria akceptacji
- Biblioteka Anime.js jest poprawnie zintegrowana z projektem
- Animacje są używane celowo i subtelnie w całej aplikacji
- Animacje szanują preferencję `prefers-reduced-motion` użytkownika
- Wszystkie animowane elementy są dostępne klawiaturą i nie utrudniają używania czytników ekranu
- Animacje nie obniżają znacząco wydajności aplikacji
- Sekcja może być uznana za ukończoną po pozytywnej weryfikacji przez lead developer lub poprzez automated tests

## Zależności od innych sekcji
- Zależna od: wszystkie poprzednie sekcje (01-12) ponieważ może być wykorzystywana w dowolnym miejscu w interfejsie
- Wymagana przez: żadna sekcja nie jest ścisłe zależna od tej sekcji (animacje są ulepszeniem, nie wymogiem funkcjonalnym)
- Jednak sekcje 08, 09, 10, 11, 12, 14 prawdopodobnie będą wykorzystywać animacje opisane w tej sekcji

## Warunki zakończenia prac
- Biblioteka Anime.js jest zintegrowana i gotowa do użycia
- Własne funkcje pomocnicze są stworzone i dokumentowane
- Przykładowe animacje są zaimplementowane w kluczowych miejscach interfejsu
- Mechanizm obsługi `prefers-reduced-motion` działa poprawnie
- Sekcja może być uznana za ukończoną po pozytywnej weryfikacji przez lead developer lub poprzez automated tests

## Informacje, które należy przekazać do kolejnych sekcji
- Interfejs własnych funkcji pomocniczych Anime.js (dostępne funkcje i ich sygnatury)
- Informacje o tym jak wykryć i szanować preferencję `prefers-reduced-motion`
- Przykłady użycia animacji dla typowych elementów interfejsu (przyciski, pola input, karty, powiadomienia)
- Informacje o klasach CSS i identyfikatorach używanych dla animacji
- Wskazówki dotyczące wydajności i najlepszych praktyk użycia Anime.js w tym projekcie

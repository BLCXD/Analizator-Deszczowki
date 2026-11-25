# 03_DESIGN_SYSTEM.md
## Kompletny system wizualny, kolory, typografia, odstępy, komponenty, responsywność i zasady spójności

## Cel sekcji
Zdefiniowanie kompletnego systemu wizualnego dla dashboardu Analizator Deszczówki, który zapewni spójny, profesjonalny wygląd aplikacji zgodny z jej celem jako narzędzia do monitorowania infrastruktury IoT.

## Kontekst i zależności
Ta sekcja zależy od:
- 01_PROJECT_ANALYSIS.md (zrozumienie wymagań projektu i backendu)
- 02_ARCHITECTURE.md (względem struktury aplikacji, gdzie komponenty UI będą implementowane)

Nie ma zależności od innych sekcji projektowych, ale wszystkie kolejne sekcje implementacyjne dotyczące UI będą się odnosić do tego systemu projektowego.

## Stan początkowy
- Brak istniejącego systemu projektowego w repozytorium
- Brak zdefiniowanej palety kolorów, typografii ani komponentów
- Dostępne są umiejętności: design-system, design-taste-frontend, ui-styling, ui-ux-pro-max
- Projekt ma być profesjonalnym produktem do monitorowania infrastruktury, nie generycznym szablonem

## Szczegółowy zakres implementacji
### Filozofia projektowa
Dashboard AD ma być:
- **Profesjonalny i funkcjonalny** - każdy element musi mieć uzasadnienie operacyjne
- **Czytelny i przejrzysty** - priorytetem jest łatwe odczytywanie krytycznych danych
- **Zaufany** - wizualnie komunikuje stabilność i niezawodność systemu
- **Skalowalny** - łatwe dodawanie nowych komponentów i funkcji
- **Dostępny** - projektowany z uwzględnieniem zasad dostępności (do weryfikacji zgodności z WCAG 2.1 AA)
- **Responsywny** - działa na różnych rozmiarach ekranów od mobilnych do desktopowych

### Paleta kolorów
Paleta kolorów została określona zgodnie z wymaganiami dla aplikacji monitoringu wody i infrastruktury:

#### Kolory podstawowe (Primary) - wymagana paleta
- **Główne tło** (`#0F1419`) - główny kolor tła aplikacji
- **Panele i powierzchnie** (`#393E44`) - kolor pomocniczy dla kart, paneli i powierzchni komponentów
- **Tekst i dane pomiarowe** (`#D4F4FF`) - główny kolor tekstu, wartości pomiarowych i ważnych danych
- **Akcent** (`#E49D22`) - oszczędnie stosowany kolor akcentowy dla ważnych wskazań i interakcji

#### Dodatkowe kolory stanowe (zachowane dla funkcjonalności)
- **Sukces** (`#4CAF50`) - pozytywne stany, prawidłowe wartości, bezpieczne zakresy
- **Ostrzeżenie** (`#FFC107`) - ostrzeżenia, wartości zbliżające się do progów
- **Błąd** (`#F44336`) - błędy, krytyczne stany, przekroczenie progów krytycznych
- **Informacja** (`#00BFA6`) - informacyjne komunikaty

#### Kolory neutralne (Neutrals)
- **Tekst główny**: var(--color-text-primary) - podstawowy kolor tekstu na ciemnym tle
- **Tekst pomocniczy**: var(--color-text-secondary) - mniej ważne informacje, etykiety
- **Tekst wyłączony**: var(--color-text-disabled) - nieaktywne elementy
- **Obramowanie**: var(--color-border) - subtelne oddzielenie komponentów
- **Tło kart**: var(--color-surface) - lekko jaśniejsze niż główne tło dla wyraźnego rozróżnienia

#### Kolory stanu (State Colors)
Używane do wskazywania statusu komponentów i danych:
- **Sukces** (`#4CAF50`) - wszystko działa prawidłowo
- **Ostrzeżenie** (`#FFC107`) - wymaga uwagi, ale nie jest krytyczne
- **Błąd** (`#F44336`) - wymaga natychmiastowej interwencji
- **Informacja** (`#00BFA6`) - informacyjne komunikaty
- **Ładowanie** (`#00BFA6`) - animowany podczas ładowania danych

#### Wykresy i wizualizacje danych
- **Oś i linie siatki** (var(--color-border) z opacity 0.3) - subtelne, nieodwracające uwagi od danych
- **Linia danych** (var(--color-accent)) - główna linia wykresu
- **Linia progowa** (var(--color-status-warning) dla ostrzeżenia, var(--color-status-error) dla krytycznego) - linie wskazujące skonfigurowane progi
- **Wypełnienie pod wykresem** (var(--color-accent) z opacity 0.1) - subtelne wypełnienie dla lepszej czytelności
- **Punkty danych** (var(--color-text-primary) z obramowaniem var(--color-accent)) - wyraźne punkty na wykresach liniowych
- **Słupek wykresu słupkowego** (var(--color-accent)) - standardowy kolor słupków
- **Słupek ostrzegawczy** (var(--color-status-warning)) - słupki wskazujące na wartości wymagające uwagi
- **Słupek krytyczny** (var(--color-status-error)) - słupki wskazujące na krytyczne wartości

### Typografia
Typografia została wybrana dla maksymalnej czytelności przy jednoczesnym zachowaniu nowoczesnego, profesjonalnego wyglądu:

#### Czcionki
- **Nagłówki**: `Inter`, `-apple-system`, `BlinkMacSystemFont`, `sans-serif`
- **Tekst główny**: `Inter`, `-apple-system`, `BlinkMacSystemFont`, `sans-serif`
- **Cyfry i wartości pomiarowe**: `Inter`, `-apple-system`, `BlinkMacSystemFont`, `sans-serif` (z feature settings dla lepszej renderacji cyfr)

#### Rozmiary i wagi
- **Nagłówek główny (h1)**: 2.5rem (40px), weight 700
- **Nagłówek sekcji (h2)**: 2rem (32px), weight 600
- **Nagłówek karty (h3)**: 1.5rem (24px), weight 600
- **Tekst podstawowy**: 1rem (16px), weight 400
- **Tekst pomocniczy**: 0.875rem (14px), weight 400
- **Etykiety**: 0.75rem (12px), weight 500, text-transform: uppercase
- **Wartości pomiarowe (duże)**: 2.25rem (36px), weight 700
- **Wartości pomiarowe (średnie)**: 1.5rem (24px), weight 600
- **Wartości pomiarowe (małe)**: 1rem (16px), weight 500

#### Wysokość linii i odstępy literowe
- **Wysokość linii**: 1.5 dla tekstu głównego, 1.2 dla nagłówków
- **Odstępy literowe**: 
  - Nagłówki: -0.5px
  - Tekst główny: 0
  - Wielkie litery/etykiety: 0.5px

### Odstępy i siatka
System odstępy oparty jest na 8-point grid dla konsekwentnego wyrównania i skalowania:

#### Podstawowa jednostka
- **Podstawowa jednostka odstępu**: 8px
- **Skala odstępów**: 
  - 0px
  - 4px (0.5 jednostki)
  - 8px (1 jednostka) - podstawowa
  - 12px (1.5 jednostek)
  - 16px (2 jednostki)
  - 24px (3 jednostki)
  - 32px (4 jednostki)
  - 40px (5 jednostek)
  - 48px (6 jednostek)
  - 56px (7 jednostek)
  - 64px (8 jednostek)
  - 80px (10 jednostek)
  - 96px (12 jednostek)
  - 128px (16 jednostek)

#### Marginesy i padding
- **Padding kontenera głównego**: 24px (mobilnie), 32px (tablet), 48px (desktop)
- **Margines między sekcjami**: 32px
- **Padding kart**: 24px
- **Padding wewnętrzny komponentów**: 8px-24px w zależności od typu
- **Odstęp między elementami w linii**: 8px-16px
- **Odstęp między liniami**: 16px-24px

#### Promienie narożników
- **Standardowy promień**: 8px
- **Zaokrąglone karty**: 12px
- **Pełne zaokrąglenie**: 50% (dla awatary, przycisków okrągłych)
- **Brak zaokrąglenia**: 0px (dla niektórych elementów strukturalnych)

### Komponenty interfejsu
Zestaw wielokrotnego użytku komponentów zaprojektowanych specjalnie dla potrzeb monitoringu IoT:

#### 1. Karty metryczne (Metric Cards)
Główny sposób prezentacji kluczowych wskaźników:
- **Struktura**: 
  - Nagłówek (etykieta parametru, np. "pH wody")
  - Wartość główna (duża cyfra z jednostką)
  - Status (mały wskaźnik kolorowy + tekst)
  - Dodatkowy kontekst (opcjonalnie: trend, zmiana, czas ostatniej aktualizacji)
- **Warianty**:
  - Standardowa karta metryczna
  - Karta z mini-wykresem sparkline
  - Karta z ostrzeżeniem/aleretem
  - Karta podsumowująca grupę powiązanych parametrów
- **Stany**: domyślny, ładowanie, błąd, ostrzeżenie, sukces

#### 2. Pasek nawigacji (Navigation)
- **Poziomy pasek górny** (alternatywa dla bocznego na małych ekranach):
  - Logo/nazwa aplikacji
  - Selektor instalacji/zbiornika (jeśli多个)
  - Globalne akcje (powiadomienia, ustawienia, profil)
  - Tryb jasny/ciemny
- **Boczny pasek nawigacyjny** (dla tabletów i desktopów):
  - Logo aplikacji
  - Pozycje menu z ikonami i etykietami
  - Aktywna pozycja wyraźnie wyróżniona
  - Sekcja konta użytkownika na dole

#### 3. Komponent wykresu (Chart Component)
Ujednolicony komponent do prezentacji danych czasowych:
- **Typy wykresów**: liniowy, słupkowy, obszarowy
- **Funkcjonalności**:
  - Tooltip z dokładnymi wartościami i timestampem
  - Przełączanie parametrów
  - Wybór zakresu czasu (1h, 24h, 7d, 30d, custom)
  - Liny progów ostrzegawczych/krytycznych
  - Oznaczanie luk w danych
  - Animacje przejść między stanami
  - Responsywność (przekształca się w odpowiedni format dla mobilnych)
- **Stanów**: ładowanie, dane dostępne, błąd, puste dane

#### 4. Wskaźnik statusu (Status Indicator)
Mały komponent do prezentacji stanu systemu/urządzenia:
- **Warianty**:
  - Kołowy (punkt statusu)
  - Prostokątny z etykietą
  - Pasek postępu
- **Kolory**: zgodnie z paletą stanów
- **Rozmiary**: małe (8px), średnie (12px), duże (16px)
- **Animacje**: pulsujące dla ładowania, miganie dla krytycznych błędów

#### 5. Panel alertów (Alert Panel)
Komponent do prezentacji powiadomień i alertów:
- **Typy alertów**: informacja, ostrzeżenie, błąd, sukces
- **Struktura**:
  - Ikona typu alertu
  - Tytuł alertu
  - Opis szczegółowy
  - Timestamp
  - Akcje (oznacz jako przeczytane, przejdź do szczegółów, rozwiąż)
- **Pozycjonowanie**: stały w prawym dolnym rogu (dostępny przez bell icon w nagłówku)
- **Animacje**: wjazd z dołu, automatyczne znikanie po czasie (dla niekrytycznych)

#### 6. Przyciski (Buttons)
Komponenty akcji z odpowiednią wagą wizualną:
- **Warianty**:
  - Primary (akcja główna): tło akcentowe, tekst jasny
  - Secondary (akcja pomocnicza): obramowanie akcentowe, tekst akcentowe, przezroczyste tło
  - Danger (akcja destrukcyjna): tło czerwone, tekst jasny
  - Link (minimalna akcja): tylko tekst akcentowy, podkreślenie przy hoverze
- **Rozmiary**: małe, średnie, duże
- **Stany**: domyślny, hover, aktywny, wyłączony, ładowanie
- **Promień narożników**: 4px-8px w zależności od wariantu
- **Animacje**: subtelne przejścia stanu, efekty naciskania

#### 7. Formularze i pola wejściowe (Form Components)
Komponenty do wprowadzania danych i konfiguracji:
- **Pola tekstowe**: z etykietą, placeholderem, walidacją
- **Pola wyboru**: select, radio buttons, checkboxes
- **Przełączniki**: toggle switches dla opcji binarnych
- **Selektory daty i czasu**: dostosowane do potrzeb konfiguracji
- **Selektor zakresu**: do wyboru okresów czasu dla wykresów
- **Walidacja**: wizualna informacja o błędach (czerwone obramowanie, tekst pomocniczy)
- **Stany**: domyślny, fokus, błąd, wyłączony

#### 8. Powiadomienia i toasty (Notification Components)
Niezablokowujące informacje o zdarzeniach systemu:
- **Toast**: tymczasowe powiadomienie w prawym górnym rogu
- **Snackbar**: działanie wymagające potwierdzenia z opcją cofnięcia
- **Modal**: blokujące okno dialogowe dla krytycznych akcji
- **Animacje**: płynne wjazd/wyjście, odpowiednie czas trwania

#### 9. Historia opadów
Wykres deszczomierza pokazuje sumę opadu, jednostkę i czas odczytu.

#### 10. Tabela danych (Data Table)
Komponent do prezentacji rekordów pomiarowych i historii:
- **Funkcjonalności**:
  - Sortowanie kolumn
  - Filtrowanie wierszy
  - Paginacja lub nieskończone przewijanie
  - Wybór wierszy do akcji masowych
  - Eksporz wybranych danych
  - Responsywność (przekształca się w karty dla małych ekranów)
- **Wygląd**:
  - Czytelne nagłówki z jasnym podkreśleniem klikalności
  - Przemienny kolor wierszy dla lepszej śledzenia
  - Wyrównanie danych zgodnie z typem (tekst-lewo, liczby-prawo)
  - Subtelne linie oddzielające wiersze

### Responsywność
System zapewnia optymalne doświadczenie na różnych urządzeniach:

#### Punkty przerwania (Breakpoints)
- **Mobilny**: < 640px
- **Tablet**: 640px - 1024px
- **Desktop**: > 1024px
- **Szeroki desktop**: > 1440px (opcjonalnie dla dodatkowego miejsca na boczne panele)

#### Strategie adaptacji
1. **Układ(layout)**:
   - Mobilny: jednokolumnowy układ, sekcje układające się pionowo
   - Tablet: dwukolumnowy dla przeglądu głównego, możliwość bocznej nawigacji
   - Desktop: stały boczny pasek nawigacyjny + główny obszar zawartości
   - Szeroki desktop: dodatkowe miejsce na zaawansowane panele boczne

2. **Komponenty**:
   - Karty metryczne: pełna szerokość na mobilnym, wielokolumnowy układ na większych ekranach
   - Wykresy: pełna szerokość z odpowiednią wysokością, na desktop możliwe umieszczenie obok siebie
   - Tabele: przewijanie poziome na małych ekranach, pełna funkcjonalność na większych
   - Nawigacja: hamburger menu na mobilnym, boczny pasek na tabletach i desktopach

3. **Typografia**:
   - Skalowanie rozmiarów czcionek zależnie od szerokości ekranu (skalowanie typu fluid)
   - Minimalne rozmiary czytelności zachowane na wszystkich urządzeniach

4. **Odstępy**:
   - Proporcjonalne skalowanie odstępów zależnie od punktu przerwania
   - Zachowanie rytmu pionowego i poziomego

### Animacje i przejścia
Animacje mają cel informacyjny, nie dekoracyjny, zgodnie z zasadami projektu:

#### Zasady animacji
1. **Celowość**: każda animacja musi przekazywać informację o zmianie stanu
2. **Subtelność**: animacje są krótkie i niezauważalne, chyba że przekazują krytyczną informację
3. **Wydajność**: wykorzystywanie właściwości sprzętowo przyspieszanych (transform, opacity)
4. **Preferencje użytkownika**: szanowanie `prefers-reduced-motion`
5. **Dostępność**: unikanie animacji mogących powodować sekizje lub zawroty głowy

#### Typowe animacje
- **Przejścia stanu**: ładowanie → dane, błąd → sukces (fade, slide)
- **Zmiany wartości**: płynna interpolacja liczbowej zmiany wartości (counter animation)
- **Pojawianie się danych**: fade-in lub slide-in dla nowych elementów
- **Przeładowanie**: subtelne pulsujące wskazanie odświeżania
- **Błędy**: krótkie miganie lub potrząsanie dla krytycznych błędów (do użycia ostrożnie)
- **Interakcje**: efekty naciskania, podświetlenie przy hoverze
- **Wykresy**: animowane przejścia między punktami danych, pojawianie się nowych punktów
- **Wykres opadów**: płynne przejście między seriami danych

#### Czas trwania i krzywe
- **Szybkie przejścia**: 150ms (stan UI, małe zmiany)
- **Standardowe przejścia**: 250ms (pojawianie się komponentów, zmiany widoku)
- **Wolne przejścia**: 350-400ms (ważne zmiany stanu, nawigacja między stronami)
- **Animacje natury**: 500ms-1s (płynne zmiany wartości na wykresach)
- **Krzywe**: `ease-in-out` dla większości przejść, `ease-out` dla pojawiania się, `ease-in` dla znikania

### Dostępność (Accessibility)
Podstawowe wymagania dostępności WCAG 2.1 AA:

#### Kontrast kolorów
- Tekst i ważne elementy UI muszą mieć współczynnik kontrastu co najmniej 4.5:1
- Tekst duży (18pt+ lub 14pt+ pogrubiony): minimum 3:1
- Elementy interaktywne i komponenty graficzne: minimum 3:1
- Sprawdzone kombinacje z palety zapewniają wymagany kontrast

#### Obsługa klawiatury
- Wszystkie funkcjonalności dostępne przez klawiaturę
- Jasny wskaźnik fokusu (outline 2px solid var(--color-text-primary))
- Logiczną kolejność tabulacji
- Dostępne skróty klawiaturowe dla częstych akcji (gdzie stosowne)

#### Kompatybilność z czytnikami ekranu
- Semantyczny HTML5 (nagłówki, listy, regiony landmark)
- Odpowiednie etykiety dla formularzy i kontrolek
- Opisy grafiki i wykresów (gdzie stosowne)
- ARIA labels dla komponentów bez wystarczającego kontekstu
- Live regions dla dynamicznie zmieniających się wartości

#### Responsywność dostępności
- Elementy nie tracą funkcjonalności przy powiększeniu tekstu do 200%
- Brak utraty zawartości lub funkcjonalności przy przejściowym układzie pionowym
- Celowe rozmiary elementów dotykowych minimum 44x44px

### Zasady spójności i wykorzystania systemu
Aby zapewnić spójne stosowanie systemu projektowego:

#### Tokeny projektowe (Design Tokens)
Wszystkie wartości powinny być definiowane jako tokeny, aby umożliwić łatwe utrzymywanie i motywy:
- **Kolory**: `--color-bg-primary`, `--color-surface`, `--color-text-primary`, `--color-accent`, `--color-status-success` itp.
- **Odstępy**: `--space-1`, `--space-2`, `--space-3` itp.
- **Typografia**: `--font-size-heading-1`, `--font-weight-bold`, `--line-height-body` itp.
- **Promienie narożników**: `--radius-sm`, `--radius-md`, `--radius-lg`
- **Czas trwania animacji**: `--duration-fast`, `--duration-normal`, `--duration-slow`
- **Przejścia**: `--transition-fast`, `--transition-normal` itp.

#### Implementacja w CSS
Użycie zmiennych CSS dla łatwego motywowania i utrzymywania:
```css
:root {
  /* Kolory - wymagana paleta dla AD */
  --color-bg-primary: #0F1419;       /* główne tło */
  --color-surface: #393E44;          /* panele i powierzchnie */
  --color-text-primary: #D4F4FF;     /* tekst i dane pomiarowe */
  --color-accent: #E49D22;           /* oszczędnie stosowany akcent */
  
  /* Dodatkowe kolory stanowe (zachowane dla funkcjonalności) */
  --color-status-success: #4CAF50;
  --color-status-warning: #FFC107;
  --color-status-error: #F44336;
  --color-status-info: #00BFA6;
  --color-text-secondary: #B0BEC5;
  --color-text-disabled: #78909C;
  --color-border: #2E3A4F;
  
  /* Tekst na kolorach akcentowych (do sprawdzenia kontrastu) */
  --color-text-on-accent: #000000; /* Czarny na jasnych akcentach */
  
  /* Odstępy */
  --space-0: 0px;
  --space-0-5: 4px;
  --space-1: 8px;
  --space-1-5: 12px;
  --space-2: 16px;
  --space-3: 24px;
  --space-4: 32px;
  --space-5: 40px;
  --space-6: 48px;
  --space-7: 56px;
  --space-8: 64px;
  --space-10: 80px;
  --space-12: 96px;
  --space-16: 128px;
  
  /* Typografia */
  --font-family-base: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-size-heading-1: 2.5rem;
  --font-size-heading-2: 2rem;
  --font-size-heading-3: 1.5rem;
  --font-size-body: 1rem;
  --font-size-sm: 0.875rem;
  --font-size-xs: 0.75rem;
  --font-weight-light: 300;
  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;
  --line-height-body: 1.5;
  --line-height-heading: 1.2;
  
  /* Promienie narożników */
  --radius-none: 0px;
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-full: 50%;
  
  /* Animacje */
  --duration-fast: 150ms;
  --duration-normal: 250ms;
  --duration-slow: 350ms;
  --duration-slower: 400ms;
  --duration-nature: 500ms;
  
  /* Przejścia */
  --transition-fast: var(--duration-fast) ease-in-out;
  --transition-normal: var(--duration-normal) ease-in-out;
  --transition-slow: var(--duration-slow) ease-in-out;
}
```

#### Komponenty jako klasy CSS lub moduły
Komponenty powinny być implementowane jako wielokrotnego użytku klasy CSS lub (w przypadku frameworków JS) jako komponenty z jasno zdefiniowanym interfejsem:
- **Nazewnictwo**: prefiks `ad-` dla uniknięcia konfliktów (np. `ad-metric-card`, `ad-chart-container`)
- **Modyfikatory**: skład notation BEM lub podobna dla wariantów (np. `ad-metric-card--warning`)
- **Stany**: klasy dla różnych stanów (np. `.is-loading`, `.is-error`, `.is-disabled`)

#### Dokumentacja komponentów
Każdy komponent powinien być dokumentowany z:
- Cel i zastosowanie
- Właściwości (props) i ich typy
- Zdarzenia (events) które emituje
- Stany i warianty
- Przykłady użycia
- Zależności od innych komponentów lub tokenów

### Integracja z architekturą aplikacji
System projektowy ściśle współpracuje z zdefiniowaną architekturą:

#### Warstwa prezentacji (Views)
- Szablony HTML wykorzystują klasy i komponenty z systemu projektowego
- Zachowanie oddzielenia odpowiedzialności: HTML dla struktury, CSS dla stylizacji, JS dla zachowania
- Użycie szablonów Jinja2 do wielokrotnego wykorzystania komponentów (np. makra dla kart metrycznych)

#### Warstwa stylizacji (Static/CSS)
- Pliki CSS zorganizowane według zasad systemu projektowego
- Oddzielenie: tokeny, komponenty, layouty, strony
- Możliwość łatwego tworzenia motywów (jasny/ciemny) poprzez nadpisywanie tokenów
- Optymalizacja poprzez usuwanie nieużywanych CSS w produkcji

#### Warstwa komponentów (JS/Controllers)
- Komponenty UI otrzymują dane poprzez dobrze zdefiniowane interfejsy
- Logika prezentacji oddzielona od logiki biznesowej
- Komponenty są kontrolowane poprzez właściwości (props) i komunikują zdarzenia

#### Motywy
System przygotowany jest na łatwe implementowanie motywów:
- **Motyw ciemny** (domyślny): jak opisano powyżej
- **Motyw jasny**: odwrócona paleta z odpowiednimi przystosowaniami dla kontrastu
- **Motyw systemowy**: automatyczne wykrywanie preferencji systemowych
- Implementacja poprzez klasę na elemencie `<html>` lub `<body>` (np. `.theme-dark`, `.theme-light`)

### Pliki, które należy utworzyć lub zmodyfikowane
W ramach tej sekcji zostanie utworzona dokumentacja systemu projektowego. Rzeczywiste implementacja komponentów i stylów będzie następować w kolejnych sekacjach:

**Dokumentacja:**
- Ten plik (03_DESIGN_SYSTEM.md) - kompletna specyfikacja systemu projektowego

**Do utworzenia w kolejnych sekach (wskazówki gdzie umieścić):**
- `/app/static/css/base.css` - zmienne CSS z tokenami projektu
- `/app/static/css/components.css` - style dla komponentów UI
- `/app/static/css/utilities.css` - klasy pomocnicze
- `/app/static/css/animations.css` - definicje animacji
- `/app/static/css/responsive.css` - media queries i adaptacje responsywne
- `/app/templates/components/` - makra HTML dla wielokrotnego użytku komponentów
- `/app/static/js/ui-components.js` - klasy/funkcje dla komponentów UI (jeśli używamy vanilla JS)

### Integracja z pozostałymi elementami systemu
System projektowy zapewnia:
- Spójny wygląd wszystkich komponentów dashboardu
- Łatwe utrzymywanie poprzez zentralizowane definicje wartości
- Skalowalność poprzez modułowe komponenty
- Dostępność poprzez wbudowane zasadz i wzorce
- Profesjonalny wygląd odpowiedni dla aplikacji monitoringu infrastruktury
- Możliwość łatwego tworzenia motywów (jasny/ciemny, systemowy)
- Wydajność poprzez wykorzystanie właściwości sprzętowo przyspieszonych
- Gotowość na międzynarodowanie (i18n) poprzez oddzielenie prezentacji od treści

### Obsługa błędów i przypadków brzegowych
System projektowy zawiera wskazówki dotyczące radzenia sobie z różnymi sytuacjami:

#### Stany danych
- **Ładowanie**: subtelna animacja wskazująca pobieranie danych
- **Błąd wyraźny**: komponent w stanie błędu z możliwością ponowienia próby
- **Puste dane**: komunikat informujący o braku dostępnych danych z sugestiami
- **Częściowe dane**: komponenty radzą sobie z brakującymi polami (wyświetlają dostępne informacje)
- **Przestarzałe dane**: wyraźne oznaczenie wieku danych i możliwość odświeżania

#### Stany połączenia
- **Online**: zielony wskaźnik statusu + normalna funkcjonalność
- **Wolne połączenie**: żółty wskaźnik + wskazanie opóźnienia
- **Offline**: czerwony wskaźnik + tryb offline z buforowaniem akcji
- **Przełączanie**: płynne przejścia między stanami połączenia

#### Stany urządzeń
- **Podłączony i aktualny**: zielony status + najnowsze dane
- **Podłączony ale nieaktualny**: żółty status + wskazanie wieku danych
- **Rozłączony**: czerwony status + opcje ponownego połączenia
- **W trybie демонстрации**: wyraźne oznaczenie że pokazane dane są symulowane

#### Błędy użytkownika
- **Walidacja formularzy**: wyraźne wskazanie pól z błędami i komunikaty wyjaśniające
- **Nieprawidłowe akcje**: powiadomienia wyjaśniające dlaczego akcja nie może być wykonana
- **Brak uprawnień**: komunikat informujący o braku dostępu do funkcji lub danych
- **Sesja wygasła**: przekierowanie do logowania z zachowaniem kontekstu (gdzie możliwe)

### Testy wymagane do uznania sekcji za ukończoną
- Zweryfikowanie, że wszystkie elementy systemu projektowego są oparte na wymaganiach projektu
- Potwierdzenie, że paleta kolorów zapewnia odpowiedni kontrast dla dostępności
- Dokumentacja wszystkich tokenów projektowych i ich zastosowania
- Określenie zasad użycia komponentów i wzorców projektowych
- Zaplanowanie integracji z architekturą aplikacji
- Dokumentacja podejścia do responsywności i dostępności
- Określenie zasad animacji i przejść stanu UI

### Jednoznaczne kryteria akceptacji
- Dokument zawiera kompletną definicję palety kolorów z zachowaniem zasad dostępności
- System typograficzny jest czytelny, profesjonalny i odpowiedni dla prezentacji danych
- System odstępy zapewnia konsekwentne wyrównanie i skalowanie
- Komponenty UI są odpowiednio zdefiniowane dla potrzeb monitoringu IoT
- Zasady responsywności zapewniają optymalne doświadczenie na różnych urządzeniach
- Animacje mają cel informacyjny i szanują preferencje użytkownika
- System jest przygotowany na łatwe implementowanie motywów i dostosowań
- Dokumentacja zawiera wskazówki dotyczące integracji z architekturą aplikacji
- System projektowy szanuje zasady projektu AD (profesjonalizm, funkcjonalność, nie nadmierne dekorowanie)

### Zależności od innych sekcji
- Wymaga ukończenia: 01_PROJECT_ANALYSIS.md, 02_ARCHITECTURE.md
- Jest wymaganiem wstępnym dla: wszystkie sekcje implementacyjne dotyczące UI (07-18)

### Warunki zakończenia prac
Uznać sekcję za zakończoną gdy:
- Zdefiniowano kompletną paletę kolorów z uwzględnieniem dostępności
- Określono system typograficzny odpowiedni dla prezentacji danych
- Zaplanowano system odstępy i siatkę układu
- Zdefiniowano wielokrotnego użytku komponenty UI dla potrzeb dashboardu
- Określono zasady responsywności i adaptacji do różnych ekranów
- Dokumentowano zasady animacji i przejść stanu UI
- Określono wymagania dostępności i sposoby ich spełnienia
- Zaplanowano integrację z architekturą aplikacji

### Informacje, które należy przekazać do kolejnych sekcji
- Pełna definicja tokenów projektowych (zmienne CSS)
- Specyfikacja komponentów UI i ich interfejsów
- Zasady użycia kolorów, typografii i odstępów
- Wytyczne dotyczące responsywności i punktów przerwania
- Specyfikacja animacji i przejść stanu
- Wymagania dostępności i sposoby ich implementacji
- Podejście do motywów (jasny/ciemny, systemowy)
- Integracja z warstwą prezentacji aplikacji Flask

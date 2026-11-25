# 22. DESIGN TOOLS, SKILLS & UI ENGINEERING WORKFLOW

## 1. CEL

Ten dokument określa obowiązkowy sposób wykorzystania dostępnych skilli, narzędzi projektowych i narzędzi przeglądarkowych podczas tworzenia dashboardu Analizatora Deszczówki (AD).

Nie wystarczy stworzyć działający frontend. Interfejs ma być profesjonalnie zaprojektowany, dopracowany wizualnie, funkcjonalny i zweryfikowany w rzeczywistej przeglądarce.

Claude Code ma wykorzystywać dostępne skille jako narzędzia pracy, a nie tylko o nich wspominać.

## 2. OBOWIĄZKOWE ROZPOZNANIE SKILLI

Przed rozpoczęciem implementacji:

1. Sprawdź, jakie skille są faktycznie dostępne w bieżącym środowisku Claude Code.
2. Sprawdź globalne i projektowe katalogi skilli, konfigurację projektu oraz dostępne integracje i pluginy.
3. Odczytaj instrukcje `SKILL.md` wszystkich skilli istotnych dla tego zadania.
4. Zidentyfikuj skille dotyczące:
   - projektowania interfejsów i jakości UI/UX;
   - frontend engineering i CSS;
   - animacji, mikrointerakcji i motion design;
   - typografii, layoutu i design systems;
   - audytu i poprawiania istniejących interfejsów;
   - przeglądarki, automatyzacji i testowania;
   - dostępności i responsywności.

### Skille wskazane przez użytkownika

W pierwszej kolejności sprawdź dostępność następujących skilli:

- `emil-kowalski-skills`
- `chrome-dev-tools`
- `apple-design`
- `no-ai-slop`

Nazwy mogą odpowiadać pakietom zawierającym kilka skilli, a nie pojedynczym instrukcjom. Znajdź ich rzeczywistą strukturę i ustal, które instrukcje są odpowiednie dla bieżącego zadania.

Jeśli skill nie jest dostępny pod dokładnie podaną nazwą, poszukaj jego rzeczywistej nazwy w dostępnych katalogach i konfiguracji. Nie zakładaj, że jest zainstalowany.

Nie kończ pracy po sprawdzeniu dwóch powyższych pozycji. Wykryj i oceń również pozostałe dostępne skille, które mogą istotnie poprawić jakość dashboardu.

Nie twierdź, że przeczytałeś instrukcje, których faktycznie nie udało się otworzyć.

## 3. WYKORZYSTANIE SKILLI PODCZAS PRACY

Po rozpoznaniu środowiska przygotuj wewnętrzną mapę:

| Obszar | Wymagane działanie |
|---|---|
| Projektowanie UI | Wykorzystaj dostępne skille do określenia hierarchii wizualnej, kompozycji, typografii i jakości interfejsu. |
| Frontend engineering | Stosuj zalecenia skilli dotyczące struktury HTML, CSS, JavaScript i utrzymywalności kodu. |
| Animacje | Wykorzystaj odpowiednie skille do projektowania celowych mikrointerakcji i animacji. |
| Design system | Użyj skilli do zachowania spójności tokenów, komponentów i stanów interfejsu. |
| Audyt wizualny | Wykorzystaj dostępne narzędzia do oceny rzeczywistego wyglądu i identyfikowania problemów. |
| Przeglądarka | Wykorzystaj `chrome-dev-tools` lub faktycznie dostępne narzędzie równoważne do inspekcji i testowania działającej aplikacji. |
| Dostępność | Sprawdź kontrast, semantykę, obsługę klawiaturą i responsywność przy użyciu dostępnych narzędzi. |

Tabela nie ogranicza wykorzystania skilli. Jeżeli dostępny skill oferuje bardziej odpowiednią metodę, zastosuj ją.

### Zasady

- Przeczytaj instrukcje przed użyciem danego skilla.
- Stosuj jego zalecenia w rzeczywistym kodzie i procesie projektowania.
- Łącz skille, gdy wzajemnie się uzupełniają.
- Jeśli skill wymaga konkretnego workflow, przestrzegaj go.
- Jeśli skill zawiera checklisty jakościowe, wykorzystaj je przy weryfikacji.
- Nie uruchamiaj wszystkich skilli bezrefleksyjnie. Wybieraj te, które rzeczywiście pomagają osiągnąć cel.
- Nie zastępuj działania opisem planowanego działania.

Jeśli dostępne są skille specjalizujące się w jakości interfejsu, animacjach lub frontendzie, użyj ich zarówno podczas implementacji, jak i podczas późniejszych iteracji.

## 4. DESIGN WORKFLOW

Pracuj w następującej kolejności.

### Etap A — analiza istniejącego produktu

- Przeanalizuj strukturę frontendu i wszystkie istniejące widoki.
- Przeczytaj pozostałe dokumenty w `/sections/`.
- Zidentyfikuj aktualne problemy z hierarchią, layoutem, typografią, nawigacją i czytelnością danych.
- Sprawdź istniejące komponenty, style, tokeny i wzorce interakcji.
- Jeśli dostępny jest projekt referencyjny w Figma lub innym narzędziu, sprawdź go i wykorzystaj.
- Nie twórz nowego projektu od zera, jeśli istniejący projekt można rozwinąć zgodnie z wymaganiami.

### Etap B — projektowanie i implementacja

- Wykorzystaj odpowiednie skille do opracowania rozwiązań dla rzeczywistych problemów zidentyfikowanych w etapie A.
- Zachowaj spójność całego interfejsu.
- Twórz komponenty z myślą o ponownym wykorzystaniu.
- Zaprojektuj kompletne stany interakcji: normalny, hover, focus, active, disabled, loading, empty i error, zależnie od funkcji komponentu.
- Zadbaj o czytelność danych pomiarowych, wykresów, jednostek, dat i statusów urządzeń.
- Nie wprowadzaj dekoracyjnych elementów, które pogarszają czytelność lub nie pełnią żadnej funkcji.

### Etap C — animacje i interakcje

Jeżeli dostępne skille obsługują motion design:

- wykorzystaj je do projektowania animacji;
- preferuj krótkie, celowe animacje wynikające z działania interfejsu;
- zachowaj czytelność i płynność;
- unikaj animowania każdego elementu bez uzasadnienia;
- respektuj `prefers-reduced-motion`;
- nie poświęcaj wydajności ani dostępności dla efektów wizualnych.

Animacje mają wspierać zrozumienie stanu i działania produktu, a nie odwracać uwagę od danych.

### Etap D — weryfikacja wizualna

- Uruchom rzeczywistą aplikację.
- Otwórz ją w dostępnej przeglądarce.
- Sprawdź każdy istotny widok.
- Oceń hierarchię informacji, wyrównania, odstępy, typografię, wykresy i zachowanie komponentów.
- Porównaj wynik z dokumentacją i ewentualnym projektem referencyjnym.
- Popraw problemy, a następnie ponownie sprawdź interfejs.

Nie uznawaj za ukończony widoku, którego rzeczywistego renderowania nie zweryfikowano, jeśli dostępne narzędzia pozwalają na taką weryfikację.

## 5. CHROME DEVTOOLS I TESTOWANIE

Skill `chrome-dev-tools`, jeśli jest dostępny, powinien być podstawowym narzędziem inspekcji i weryfikacji działającego frontendu.

Przeczytaj jego instrukcje i wykorzystuj udostępnione przez niego możliwości. Nie ograniczaj się do sprawdzenia, czy strona się otwiera.

Zweryfikuj:

### Konsola i błędy
- błędy JavaScript;
- nieobsłużone wyjątki;
- ostrzeżenia wskazujące na problemy aplikacji;
- błędy renderowania i inicjalizacji komponentów.

### Network i API
- nieudane żądania;
- nieprawidłowe odpowiedzi API;
- błędy CORS i problemy z połączeniem;
- zgodność danych z oczekiwaniami frontendu;
- zachowanie aplikacji, kiedy backend jest niedostępny.

### Interakcje
- nawigację;
- przyciski i formularze;
- filtry i inne kontrolki;
- wykresy oraz aktualizację danych;
- komunikaty błędów;
- loading i empty states;
- obsługę klawiaturą.

### Responsywność
Sprawdź co najmniej:
- szeroki ekran desktopowy;
- typowy ekran laptopa;
- tablet;
- telefon.

Szukaj przepełnień, poziomego scrollowania, nieczytelnych wykresów, zbyt małych celów dotykowych i problemów z nawigacją.

Po wykryciu problemu:
1. Ustal przyczynę.
2. Napraw kod.
3. Ponownie otwórz lub odśwież odpowiedni widok.
4. Powtórz test.
5. Sprawdź, czy poprawka nie zepsuła innych widoków.

Jeżeli wskazany skill jest niedostępny, sprawdź inne dostępne narzędzia przeglądarkowe. Jeśli nie ma żadnego, wykonaj wszystkie możliwe testy automatyczne i udokumentuj brakującą weryfikację.

## 6. ZASADY DESIGN SYSTEMU AD

Podstawowym źródłem prawdy jest `sections/03_DESIGN_SYSTEM.md`.

Obowiązujące kolory bazowe:

- Background: `#0F1419`
- Surfaces: `#393E44`
- Text i dane pomiarowe: `#D4F4FF`
- Accent: `#E49D22`

Kolory statusów:
- `#4CAF50`
- `#FFC107`
- `#F44336`
- `#00BFA6`

Stosuj je zgodnie z przeznaczeniem opisanym w design systemie.

Nie zmieniaj samowolnie podstawowej palety, zasad typografii ani istniejących tokenów. Jeśli dokumentacja zawiera bardziej szczegółowe reguły, mają one zastosowanie.

Dashboard ma być profesjonalnym produktem technicznym do monitorowania i analizy deszczówki.

Unikaj:
- generycznego wyglądu dashboardów AI;
- przypadkowych gradientów i glassmorphismu;
- nadmiaru kart i obramowań;
- emoji zamiast odpowiednich ikon;
- dekoracji bez funkcji;
- sztucznych danych używanych do maskowania braków integracji;
- animacji bez uzasadnienia;
- niespójnych odstępów i przypadkowej typografii.

Jakość wizualna ma wynikać z przemyślanej kompozycji, czytelności, precyzji, spójności i użyteczności.

## 7. OGRANICZENIA TECHNICZNE

- Zachowaj architekturę Flask + Jinja2 + HTML/CSS/JavaScript.
- Nie migruj do Reacta ani innego frameworka bez jednoznacznego wymagania w dokumentacji.
- Nie dodawaj nowych bibliotek wyłącznie dlatego, że są modne.
- Przed dodaniem zależności sprawdź, czy istniejące narzędzia nie rozwiązują już problemu.
- Nie przebudowuj działających elementów bez uzasadnienia.
- Nie zmieniaj kontraktów API bez konieczności i analizy wpływu na backend.
- Nie usuwaj funkcjonalności, aby uprościć testy.
- Nie ukrywaj błędów przez wyłączanie logowania, testów lub komunikatów diagnostycznych.

## 8. KRYTERIA UKOŃCZENIA

Pracę uznaje się za ukończoną, gdy:

- dostępne i istotne skille zostały rozpoznane;
- instrukcje używanych skilli zostały przeczytane;
- zalecenia odpowiednich skilli zostały zastosowane w implementacji;
- interfejs został uruchomiony i sprawdzony w rzeczywistej przeglądarce, jeśli narzędzia na to pozwalają;
- znalezione problemy zostały naprawione lub precyzyjnie udokumentowane;
- wszystkie dostępne testy zostały uruchomione;
- design jest spójny z dokumentacją AD;
- nie ma znanych błędów krytycznych ani atrap funkcjonalności.

Na koniec raportu podaj:
1. Jakie skille wykryto.
2. Które skille zostały faktycznie wykorzystane i do jakich zadań.
3. Jakie narzędzia projektowe i przeglądarkowe wykorzystano.
4. Jakie widoki i funkcje sprawdzono.
5. Jakie testy wykonano i jakie były wyniki.
6. Jakie problemy naprawiono.
7. Co pozostało niewykonane i dlaczego.

Nie deklaruj użycia narzędzia, skilla ani testu, jeśli faktycznie go nie użyto.

## 9. NAJWAŻNIEJSZA ZASADA

Nie traktuj designu jako jednorazowego etapu przed programowaniem.

Używaj dostępnych skilli podczas analizy, implementacji, iteracji i audytu. Po każdej większej zmianie sprawdzaj rzeczywisty rezultat. Jeśli interfejs nadal wygląda źle, jest niespójny lub działa nieprawidłowo, popraw go i ponownie przetestuj.

Celem jest kompletny, działający i dopracowany dashboard AD, a nie jedynie kod, który się kompiluje.
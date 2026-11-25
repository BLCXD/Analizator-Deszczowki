# 02_ARCHITECTURE.md
## Architektura aplikacji Flask, podział odpowiedzialności i struktura plików

## Cel sekcji
Zdefiniowanie architektury aplikacji Flask dashboardu, określenie podziału odpowiedzialności między komponentami oraz zaplanowanie struktury plików która będzie wspierać rozwój, testowanie i utrzymanie aplikacji.

## Kontekst i zależności
Ta sekcja zależy od:
- 01_PROJECT_ANALYSIS.md (zrozumienie rzeczywistego backendu i jego możliwości)
Nie ma zależności od innych sekcji architektonicznych, ale wszystkie kolejne sekcje implementacyjne będą się odnosić do tej architektury.

## Stan początkowy
- Katalog `flask-frontend-user` jest pusty
- Brak istniejącej struktury aplikacji Flask
- Brak zdefiniowanego wzorca architektonicznego dla frontendzie

## Szczegółowy zakres implementacji
### Wybrany wzorzec architektoniczny
Dla aplikacji Flask dashboardu zostanie zastosowany **modularny wzorzec MVC (Model-View-Controller) z elementami architektury opartej na komponentach**, dostosowany do specyfiki aplikacji webowej konsumującej API zewnętrzne:

1. **Model (M)** - nie będzie przechowywał własnych danych biznesowych (ponieważ dane pochodzą z backendu), ale będzie obsługiwał:
   - Stan UI aplikacji (tryb ładowania, błędów, filtrowania)
   - Formularze i dane wejściowe
   - Cache tymczasowy danych pobranych z API (opcjonalnie)

2. **View (V)** - szablony HTML5 z użyciem:
   - Semantycznego HTML5
   - CSS3 dla stylizacji i responsywności
   - Minimalnego JavaScript vanilla dla interakcji
   - Anime.js dla animacji
   - Biblioteki wykresów (do wyboru podczas implementacji)

3. **Controller (C)** - moduły Python Flask obsługujące:
   - Routing i endpointy aplikacji
   - Pobieranie danych z backend API
   - Przetwarzanie odpowiedzi API
   - Zarządzanie stanem sesji i uwierzytelnianiem
   - Obsługę błędów i przypadków brzegowych

### Struktura plików aplikacji
```
flask-frontend-user/
├── app/                           # Główna aplikacja Flask
│   ├── __init__.py               # Inicjalizacja pakietu
│   ├── models/                   # Modele stanu UI (nie biznesowe)
│   │   ├── __init__.py
│   │   ├── ui_state.py           # Stan interfejsu użytkownika
│   │   └── forms.py              # Definicje formularzy
│   │
│   ├── views/                    # Szablony HTML i logika prezentacji
│   │   ├── __init__.py
│   │   ├── templates/            # Szablony Jinja2
│   │   │   ├── base.html         # Bazowy szablon layoutu
│   │   │   ├── index.html        # Strona główna/dashboard
│   │   │   ├── measurements.html # Historia pomiarów
│   │   │   ├── charts.html       # Strona z wykresami
│   │   │   ├── devices.html      # Status urządzeń
│   │   │   ├── settings.html     # Ustawienia
│   │   │   ├── login.html        # Strona logowania
│   │   │   └── errors/           # Szablony błędów
│   │   │       ├── 404.html
│   │   │       ├── 500.html
│   │   │       └── offline.html
│   │   │
│   │   └── components/           # Wielokrotnego użytku komponenty HTML
│   │       ├── __init__.py
│   │       ├── header.html
│   │       ├── navbar.html
│   │       ├── footer.html
│   │       ├── metric-card.html
│   │       ├── chart-container.html
│   │       └── status-badge.html
│   │
│   ├── controllers/              # Moduły obsługujące routing i logikę biznesową
│   │   ├── __init__.py
│   │   ├── base.py               # Bazowy kontroler z wspólną funkcjonalnością
│   │   ├── dashboard.py          # Kontroler strony głównej
│   │   ├── measurements.py       # Kontroler historii pomiarów
│   │   ├── analytics.py          # Kontroler wykresów i analizy
│   │   ├── devices.py            # Kontroler statusu urządzeń
│   │   ├── auth.py               # Kontroler uwierzytelniania
│   │   └── settings.py           # Kontroler ustawień
│   │
│   ├── services/                 # Warstwa usług komunikujących się z backendem
│   │   ├── __init__.py
│   │   ├── api_client.py         # Klient komunikujący się z backend API
│   │   ├── websocket_service.py  # Usługa WebSocket do streamingu danych
│   │   ├── auth_service.py       # Usługa uwierzytelniania
│   │   └── data_processor.py     # Przetwarzanie i formatowanie danych
│   │
│   ├── static/                   # Pliki statyczne
│   │   ├── css/                  # Style CSS
│   │   │   ├── main.css          # Główny arkusz stylów
│   │   │   ├── responsive.css    # Stylizacja responsywna
│   │   │   ├── components.css    # Style dla komponentów
│   │   │   └── animations.css    # Style dla animacji Anime.js
│   │   │
│   │   ├── js/                   # Pliki JavaScript
│   │   │   ├── main.js           # Główny plik JS aplikacji
│   │   │   ├── api.js            # Funkcje pomocnicze do komunikacji API
│   │   │   ├── websocket.js      # Obsługa WebSocket
│   │   │   ├── charts.js         # Inicjalizacja i aktualizacja wykresów
│   │   │   ├── ui.js             # Funkcje interfejsu użytkownika
│   │   │   └── utils.js          # Funkcje pomocnicze
│   │   │
│   │   ├── vendor/               # Biblioteki zewnętrzne
│   │   │   ├── anime.js          # Biblioteka animacji
│   │   │   ├── chart.js          # Biblioteka wykresów (do wyboru)
│   │   │   └── ...               # Andere biblioteki jeśli potrzebne
│   │   │
│   │   └── images/               # Obrazy i ikony
│   │       ├── logo.png
│   │       ├── icons/
│   │       └── ...
│   │
│   ├── config/                   # Konfiguracja aplikacji
│   │   ├── __init__.py
│   │   ├── development.py        # Konfiguracja rozwojowa
│   │   ├── production.py         # Konfiguracja produkcyjna
│   │   └── default.py            # Domyślna konfiguracja
│   │
│   ├── utils/                    # Funkcje pomocnicze
│   │   ├── __init__.py
│   │   ├── helpers.py            # Pomocnicze funkcje
│   │   ├── decorators.py         # Dekoratory Flask
│   │   └── constants.py          # Stałe aplikacji
│   │
│   ├── errors/                   # Obsługa błędów aplikacji
│   │   ├── __init__.py
│   │   └── handlers.py           # Obsługuje błędów HTTP i aplikacji
│   │
│   └── app.py                    # Głównaplikacja Flask
│
├── migrations/                   # (opcjonalnie) jeśli będzie potrzebna lokalna baza
├── tests/                        # Testy jednostkowe i integracyjne
│   ├── __init__.py
│   ├── unit/                     # Testy jednostkowe
│   └── integration/              # Testy integracyjne
│
├── docs/                         # Dokumentacja techniczna
├── requirements.txt              # Zależności Python
├── config.py                     # Punkt wejścia konfiguracji
├── wsgi.py                       # Punkt wejścia dla serwerów WSGI
├── Dockerfile                    # (opcjonalnie) konteneryzacja
└── README.md                     # Dokumentacja projektu
```

### Podział odpowiedzialności
1. **Warstwa prezentacji (Views + Static)**:
   - Odpowiada za wyświetlanie danych użytkownikowi
   - Nie zawiera logiki biznesowej związanej z przetwarzaniem danych pomiarowych
   - Odpowiada za interakcje użytkownika (kliki, formularze, nawigację)
   - Implementuje responsywność i dostępność

2. **Warstwa aplikacji (Controllers + Services)**:
   - Odpowiada za logikę aplikacji
   - Komunikuje się z backendem poprzez usługi API
   - Przetwarza odpowiedzi z backendu przed przekazaniem do widoków
   - Zarządza stanem sesji i uwierzytelnianiem
   - Implementuje logikę biznesową specyficzną dla dashboardu (filtrowanie, agregacje UI)

3. **Warstwa integracji z backendem (Services)**:
   - Wyłącznie odpowiedzialna za komunikację z zewnętrznym backendem API
   - Nie zawiera logiki biznesowej aplikacji
   - Obsługuje błędów komunikacji, timeouty, ponawiania prób
   - Mapuje odpowiedzi API na formaty używane wewnętrznie w aplikacji
   - Implementuje uwierzytelnianie wobec backendu (jeśli wymagane)

4. **Warstwa konfiguracji**:
   - Zarządza ustawieniami środowiska
   - Oddziela konfigurację rozwojową, testową i produkcyjną
   - Definiuje stałe takie jak endpointy API, timeouty, limity

### Wzorce komunikacji z backendem
1. **Komunikacja HTTP/REST**:
   - Wszystkie operacje CRUD na danych pomiarowych poprzez REST API
   - Użycie biblioteki `requests` lub podobnej
   - Implementacja obsługi błędów HTTP (4xx, 5xx)
   - Implementacja timeoutów i ponawiania prób
   - Walidacja odpowiedzi JSON według określonych schematów

2. **Komunikacja WebSocket (opcjonalnie)**:
   - Jeśli backend dostarcza WebSocket dla streamingu danych na żywo
   - Implementacja klienta WebSocket z obsługą ponownego łączenia
   - Buforowanie najnowszych danych dla natychmiastowego wyświetlenia
   - Oddzielanie danych na żywo od danych historycznych z REST API

### Bezpieczeństwo
1. **Uwierzytelnianie**:
   - Jeśli backend wymaga uwierzytelniania, implementacja bezpiecznego przechowywania tokenów
   - Użycie sesji Flask lub JWT w zależności od wymagań backendu
   - Automatyczne odświeżanie tokenów (jeśli wspierane przez backend)
   - Wylogowanie i czyszczenie danych sesji

2. **Ochrona przed powszechnymi zagrożeniami webowymi**:
   - CSRF Protection (Flask-WTF lub podobne)
   - Zapobieganie XSS poprzez odpowiednie escapowanie w szablonach Jinja2
   - Bezpieczne obsługiwanie danych użytkownika w formularzach
   - Ograniczenie rozmiaru przesyłanych danych

### Wydajność i optymalizacja
1. **Strategia ładowania danych**:
   - Lazy loading danych niezbędnych do początkowego renderowania
   - Stronicowanie dużych zestawów danych (historia pomiarów)
   - Caching często używanych danych (np. lista urządzeń)
   - Odświeżanie danych w tle bez blokowania interfejsu

2. **Optymalizacja frontendowa**:
   - Minimalizacja i bundling plików CSS/JS
   - Optymalizacja obrazów
   - Ładowanie skryptów asynchroniczne gdzie to możliwe
   - Minimalizacja manipulacji DOM

### Testowalność
1. **Oddzielenie warstw**:
   - Łatwe mockowanie usług API w testach jednostkowych kontrolerów
   - Możliwość testowania usług API poprzez mockowanie zewnętrznych wywołań HTTP
   - Testowanie komponentów UI w izolacji (gdzie stosowne)

2. **Wstrzykiwanie zależności**:
   - Usługi API jako wstrzykiwane zależności w kontrolerach
   - Łatwa wymiana implementacji usług na mocki w testach

### Technologie i biblioteki
1. **Backend aplikacji**: Flask 2.x+
2. **Szablony**: Jinja2 (wbudowane w Flask)
3. **Komunikacja HTTP**: requests lub httpx
4. **Komunikacja WebSocket**: python-socketio lub websocket-client (w zależności od backendu)
5. **Animacje**: Anime.js
6. **Wykresy**: Do wyboru podczas implementacji (Chart.js zalecany ze względu na prostotę i integrację)
7. **Stylizacja**: CSS3 z możliwością użycia preprocesora (SCSS) jeśli będzie potrzebny
8. **Formularze**: Flask-WTF lub własna implementacja z walidacją
9. **Uwierzytelnianie**: Flask-Login lub własna implementacja sesji

### Konwencje kodowania
1. **Nazewnictwo**:
   - Pliki Python: snake_case
   - Klasy: PascalCase
   - Funkcje i zmienne: snake_case
   - Stałe: UPPER_SNAKE_CASE
   - Pliki szablonów HTML: snake_case z rozszerzeniem .html
   - Pliki CSS/JS: snake_case

2. **Organizacja kodu**:
   - Jeden zasób na plik (gdzie praktyczne)
   - Maksymalna długość funkcji: 50 linii
   - Maksymalna zagnieżdżenie: 4 poziomy
   - Komentarze wyjaśniające dlaczego, nie co
   - Typy danych w dokumentacji funkcji (typy Python 3.5+)

3. **Jakość kodu**:
   - Przestrzeganie PEP 8 dla kodu Python
   - Użycie linterników (flake8, pylint)
   - Testy jednostkowe dla krytycznej logiki biznesowej
   - Dokumentacja publicznych interfejsów API

### Integracja z systemem AD
Frontend będzie:
- Konsumentem istniejącego backend API FastAPI (nie będzie próbował go modyfikować ani duplikować)
- Szanował istniejące kontrakty API i formaty danych
- Nie będzie przechowywał własnej kopii danych pomiarowych (oprócz tymczasowego stanu UI)
- Będzie traktował backend jako źródło prawdy dla wszystkich danych
- Implementuje mechanizmy radzenia sobie z niedostępnością backendu (stany offline, błędów)
- Będzie komunikował się wyłącznie przez dokumentowane endpointy (nie będzie wykorzystywał nieoficjalnych metod)

### Wymagania środowiskowe
- Python 3.8+
- Flask i zależności wymienione w requirements.txt
- Dostęp do sieci do komunikacji z backendem
- Nowoczesna przeglądarka internetowa obsługująca ES6+, WebSocket, CSS3

### Pliki, które należy utworzyć lub zmodyfikowane
Wszystkie wymienione w strukturze plików powyżej zostaną utworzone jako część tej sekcji i kolejnych sekcji implementacyjnych.

### Integracja z pozostałymi elementami systemu
Architektura zapewnia:
- Jasne oddzielenie odpowiedzialności między frontendem a backendem
- Możliwość niezależnego rozwoju i testowania frontendzie
- Łatwą wymianę implementacji usług jeśli backend API ulegnie zmianie (z zachowaniem tego samego kontraktu)
- Skalowalność poprzez modularną strukturę
- Utrzymywalność poprzez konsekwentne wzorce projektowe

### Obsługa błędów i przypadków brzegowych
Architektura zawiera:
- Centralizowaną obsługę błędów HTTP i aplikacji
- Oddzielne ścieżki kodowe dla różnych typów błędów (sieciowe, API, walidacyjne)
- Stany UI dla błędów, ładowania, pustych danych
- Mechanizmy retry dla przejściowych błędów sieciowych
- Obsługę rozłączeń WebSocket i próby ponownego połączenia
- Gracjalną degradację funkcjonalności gdy niektóre usługi są niedostępne

### Testy wymagane do uznania sekcji za ukończoną
- Zdefiniowanie struktury katalogów aplikacji Flask zgodnej z opisem
- Dokumentacja wybranego wzorca architektonicznego i uzasadnienie wyboru
- Określenie podziału odpowiedzialności między warstwami aplikacji
- Zaplanowanie wzorców komunikacji z backendem
- Określenie strategii bezpieczeństwa i optymalizacji wydajności
- Dokumentacja konwencji kodowania i standardów jakości

### Jednoznaczne kryteria akceptacji
- Dokument zawiera szczegółowy opis struktury plików aplikacji Flask
- Jasno zdefiniowany podział odpowiedzialności między warstwami aplikacji
- Określone wzorce komunikacji z rzeczywistym backendem API
- Zaplanowane podejście do bezpieczeństwa, wydajności i testowalności
- Architektura zgodna z zasadami projektu AD (nie duplikuje logiki backendu, szanuje kontrakty API)

### Zależności od innych sekcji
- Wymaga ukończenia: 01_PROJECT_ANALYSIS.md
- Jest wymaganiem wstępnym dla: wszystkie sekcje implementacyjne (03-20)

### Warunki zakończenia prac
Uznać sekcję za ukończoną gdy:
- Zdefiniowano kompletną strukturę katalogów aplikacji Flask
- Opisano wzorzec architektoniczny i uzasadnienie wyboru
- Określono podział odpowiedzialności między komponentami
- Zaplanowano komunikację z backendem na podstawie rzeczywistych endpointów
- Dokumentowano podejście do bezpieczeństwa, wydajności i utrzymywalności

### Informacje, które należy przekazać do kolejnych sekcji
- Struktura katalogów i nazewnictwo plików
- Wzorzec architektoniczny i podział odpowiedzialności
- Metody komunikacji z backendem (HTTP/WebSocket)
- Podejście do zarządzania stanem aplikacji
- Strategie obsługi błędów i przypadków brzegowych
- Konwencje kodowania i standardy jakości do zastosowania w implementacji
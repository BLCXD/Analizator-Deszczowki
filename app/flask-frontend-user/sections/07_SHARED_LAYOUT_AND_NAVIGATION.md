# 07_SHARED_LAYOUT_AND_NAVIGATION.md
## Wspólny layout, nawigacja, nagłówek, stopka, responsywność i wspólne komponenty

## Cel sekcji
Zaimplementowanie wspólnego layoutu aplikacji Flask, który będzie zawierał spójny nagłówek, nawigację, stopkę oraz podstawową strukturę stron. Sekcja definiuje szablony bazowe i komponenty wielokrotnego użytku, które będą wykorzystywane we wszystkich pozostałych sekcjach dashboardu.

## Kontekst i zależności
Ta sekcja zależy od:
- 01_PROJECT_ANALYSIS.md (zrozumienie wymagań projektu)
- 02_ARCHITECTURE.md (wybrany wzorzec architektoniczny)
- 03_DESIGN_SYSTEM.md (kolory, typografia, komponenty UI)
- 04_ENVIRONMENT_AND_CONFIGURATION.md (zmienne środowiskowe)
- 05_FLASK_FOUNDATION.md (podstawowa struktura Flaska)
- 06_BACKEND_INTEGRATION.md (do sprawdzania stanu uwierzytelniania)
Nie ma zależności od innych sekcji implementacyjnych poza wymienionymi powyżej, ale jest wymagana dla wszystkich sekcji, które będą tworzyć konkretne strony (08, 09, 10, 11, 12).

## Stan początkowy
- Katalog `flask-frontend-user` zawiera podstawową strukturę Flaska (z 05_FLASK_FOUNDATION.md)
- Brak istniejących szablonów HTML
- Brak zdefiniowanego layoutu bazowego
- Brak komponentów nawigacji

## Szczegółowy zakres implementacji
### 1. Struktura szablonów
- Utworzenie katalogu `app/templates/` jeśli nie istnieje
- Utworzenie bazowego szablonu `app/templates/base.html` zawierającego:
  - Deklarację DOCTYPE HTML5
  - Sekcję `<head>` z:
    - Meta tagami (charset, viewport, description)
    - Linkami do arkuszy CSS (własnego i ewentualnych bibliotek)
    - Tagiem tytułowym z dynamiczną częścią (`{% block title %}Analizator Deszczówki{% endblock %}`)
    - Sekcją na dodatkowe CSS (`{% stylesheets %}`)
  - Sekcję `<body>` z:
    - Nagłówkiem strony (header)
    - Główną zawartością (`{% block content %}{% endblock %}`)
    - Stopką strony (footer)
    - Sekcją na dodatkowe JavaScript (`{% scripts %}`)

### 2. Nagłówek (Header)
- Utworzenie komponentu nagłówka w `app/templates/components/header.html` lub bezpośrednio w base.html
- Elementy nagłówka:
  - Logo lub nazwa aplikacji "Analizator Deszczówki"
  - Menu nawigacyjne (różne dla użytkowników zalogowanych i niezalogowanych)
  - Indykator stanu połączenia z backendem (opcjonalnie)
  - Informacje o zalogowanym użytkowniku (avatar, nazwisko, menu rozwijane)
  - Przycisk wylogowania (dla zalogowanych użytkowników)

### 3. Nawigacja
- Zdefiniowanie struktury menu nawigacyjnego:
  - Dla użytkowników niezalogowanych:
    - Strona główna / Dashboard
    - Logowanie
    - Rejestracja
  - Dla użytkowników zalogowanych:
    - Dashboard (strona główna)
    - Pomiarów i historia
    - Analiza i wykresy
    - Status urządzeń
    - Ustawienia
    - Profil użytkownika
    - Wylogowanie
- Implementacja nawigacji jako lista `<ul>` lub `<nav>` z aktywnym wyróżnieniem bieżącej strony
- Użycie Flask-URL-for do generowania linków
- Podświetlanie aktywnej pozycji w menu na podstawie bieżącego endpointu

### 4. Stopka (Footer)
- Utworzenie komponentu stopki w `app/templates/components/footer.html`
- Elementy stopki:
  - Informacje o prawach autorskich
  - Wersja aplikacji
  - Linki do dokumentacji lub wsparcia (opcjonalnie)
  - Ikony mediów społecznościowych (opcjonalnie, jeśli wymagane)

### 5. Wspólne komponenty UI
- Utworzenie katalogu `app/templates/components/` dla komponentów wielokrotnego użytku:
  - `alert.html` - komponent wyświetlania powiadomień (sukces, błąd, ostrzeżenie, informacja)
  - `loading.html` - komponent wskaźnika ładowania
  - `empty_state.html` - komponent wyświetlany gdy brak danych do pokazania
  - `error_boundary.html` - komponent obsługi błędów w komponencie
  - `device_card.html` - karta przedstawiająca podstawowe informacje o urządzeniu
  - `measurement_tile.html` - kafelk wyświetlający pojedynczy pomiar

### 6. Responsywność layoutu
- Zapewnienie, że layout działa na różnych rozmiarach ekranów:
  - Menu nawigacyjne zamienia się w "hamburger" na małych ekranach
  - Szerokość głównej zawartości ograniczona dla dużych ekranów (max-width)
  - Odpowiednie wewnętrzne odstępy (padding) na małych ekranach
  - Testowanie na szerokościach: 320px (mobile), 768px (tablet), 1024px (small desktop), 1440px (desktop)

### 7. Integracja z uwierzytelnianiem
- Wykorzystanie modułu z sekcji 06 do sprawdzania stanu uwierzytelniania
- Dynamiczne pokazywanie/ukrywanie elementów menu w zależności od stanu logowania
- Przekierowanie niezalogowanych użytkowników próbujących uzyskać dostęp do chronionych stron
- Pokazywanie powiadomienia o wygasłej sesji

### 8. Dostępność layoutu
- Semantyczne znaczniki HTML (`<header>`, `<nav>`, `<main>`, `<footer>`)
- Odpowiednie etykiety ARIA dla elementów interaktywnych
- Wystarczający kontrast kolorów zgodnie z WCAG
- Obsługa nawigacji klawiaturą (Tab, Enter, Escape)
- Fokus zarządzany logicznie (np. po zamknięciu menu mobilnego fokus wraca do przycisku)

## Konkretne zadania do wykonania
1. Utworzyć katalog `app/templates/` i `app/templates/components/`
2. Utworzyć plik `app/templates/base.html` z podstawowym layoutem
3. Utworzyć komponent nagłówka z logiką uwierzytelniania
4. Utworzyć komponent stopki
5. Utworzyć wspólne komponenty UI (alert, loading, empty state, error boundary)
6. Zaimplementować responsywne menu nawigacyjne
7. Dodawać odpowiednie klasy CSS zgodnie z design systemem z sekcji 03
8. Zaimplementować logikę pokazywania/ukrywania elementów na podstawie stanu uwierzytelniania
9. Utworzyć przykładowe strony wykorzystujące nowy layout (do testowania)
10. Napisać testy integracyjne sprawdzające renderowanie layoutu (zobacz sekcję 18)

## Wymagania techniczne
- Jinja2 jako silnik szablonów (standardowo z Flaskiem)
- Brak dodatkowych bibliotek wymaganych dla podstawowej funkcjonalności
- Opcjonalnie: Flask-Menu lub podobna biblioteka do zarządzania nawigacją (ale można zaimplementować ręcznie dla prostoty)
- Zmienne środowiskowe (z sekcji 04):
  - `APP_NAME`: nazwa aplikacji wyświetlana w nagłówku
  - `APP_VERSION`: wersja aplikacji wyświetlana w stopce

## Wymagania wizualne
- Nagłówek: stałej wysokości lub zwijany przy przewijaniu (do decyzji w design systemie)
- Menu nawigacyjne: poziome na dużych ekranach, pionowe lub "hamburger" na małych ekranach
- Aktywny element menu: wyraźnie wyróżniony (kolor tła, kolor tekstu, podkreślenie)
- Stopka: stała wysokość lub dopasowana do zawartości
- Komponenty UI: zgodne z design systemem (kolory, typografia, odstępy)
- Odstępy i wyrównanie zgodne z siatką zdefiniowaną w design systemie

## Pliki, które należy utworzyć lub zmodyfikować
- `app/templates/base.html` - nowy plik
- `app/templates/components/header.html` - nowy plik
- `app/templates/components/footer.html` - nowy plik
- `app/templates/components/alert.html` - nowy plik
- `app/templates/components/loading.html` - nowy plik
- `app/templates/components/empty_state.html` - nowy plik
- `app/templates/components/error_boundary.html` - nowy plik
- `app/templates/components/device_card.html` - nowy plik (opcjonalnie, może być wykorzystany później)
- `app/templates/components/measurement_tile.html` - nowy plik (opcjonalnie, może być wykorzystany później)
- `app/templates/index.html` lub podobny - strona główna wykorzystująca nowy layout (do testowania)

## Integrację z pozostałymi elementami systemu
- Layout będzie używany przez:
  - Sekcję 08 (Dashboard Overview) - strona główna po zalogowaniu
  - Sekcję 09 (Measurements and History) - strona z listą pomiarów
  - Sekcję 10 (Charts and Analytics) - strona z wykresami
  - Sekcję 11 (Device Status and Diagnostics) - strona ze statusem urządzeń
  - Sekcję 12 (Settings and Additional Features) - strona z ustawieniami
  - Sekcję 13 (AnimeJS and Interactions) - do animacji przejść między stronami
  - Sekcję 14 (Loading, Empty, Error States) - komponenty będą wykorzystywane w layoutzie
  - Sekcję 15 (Responsiveness and Accessibility) - zapewnienie właściwości responsywności i dostępności
  - Sekcję 16 (Security and Reliability) - integracja z mechanizmami uwierzytelniania i obsługi błędów

## Obsługę błędów i przypadków brzegowych
- Brak danych użytkownika: pokazanie podstawowego interfejsu bez informacji o użytkowniku
- Problemy z ładowaniem zasobów CSS/JS: zapewnienie podstawowej używalności bez stylizacji
- Długie nazwy w menu: implementacja rozwinięcia lub podpowiedzi przy przepełnieniu
- Brak połączenia z backendem przy sprawdzaniu stanu uwierzytelniania: graceful degradation (pokazanie jako niezalogowany)
- Nieobsługiwane przeglądarki: podstawowa funkcjonalność bez zaawansowanych efektów
- Długie sesje: okresowe odświeżanie stanu uwierzytelniania (jeśli wymagane przez backend)

## Testy wymagane do uznania sekcji za ukończoną
- Testy integracyjne sprawdzające renderowanie wszystkich komponentów layoutu
- Testy sprawdzające prawidłowe pokazywanie/ukrywanie elementów w zależności od stanu uwierzytelniania
- Testy responsywności (sprawdzenie zachowania na różnych szerokościach ekranu)
- Testy dostępności (sprawdzenie semantycznego HTML, etykiet ARIA, nawigacji klawiaturą)
- Testy wizualne porównujące output z oczekiwanym designem (opcjonalnie, zobacz sekcję 18)

## Jednoznaczne kryteria akceptacji
- Wszystkie strony aplikacji wykorzystują wspólny layout `base.html`
- Nagłówek prawidłowo wyświetla logo, menu nawigacyjne i informacje o użytkowniku
- Menu nawigacyjne zmienia się w zależności od stanu uwierzytelniania użytkownika
- Stopka jest obecna na wszystkich stronach
- Komponenty UI (alert, loading, empty state) są łatwe w użyciu poprzez proste includowanie
- Layout jest responsywny i działa na szerokościach od 320px do 1920px
- Layout spełnia podstawowe wymagania dostępności (semantyczny HTML, nawigacja klawiaturą)
- Moduł jest łatwy w użyciu przez inne sekcje poprzez prostą strukturę includowania szablonów

## Zależności od innych sekcji
- Zależna od: 01_PROJECT_ANALYSIS.md, 02_ARCHITECTURE.md, 03_DESIGN_SYSTEM.md, 04_ENVIRONMENT_AND_CONFIGURATION.md, 05_FLASK_FOUNDATION.md, 06_BACKEND_INTEGRATION.md
- Wymagana przez: 08_DASHBOARD_OVERVIEW.md, 09_MEASUREMENTS_AND_HISTORY.md, 10_CHARTS_AND_ANALYTICS.md, 11_DEVICE_STATUS_AND_DIAGNOSTICS.md, 12_SETTINGS_AND_ADDITIONAL_FEATURES.md

## Warunki zakończenia prac
- Plik `app/templates/base.html` jest w pełni zaimplementowany
- Wszystkie komponenty UI są stworzone i gotowe do użycia
- Menu nawigacyjne działa poprawnie dla zalogowanych i niezalogowanych użytkowników
- Layout jest responsywny i dostępny
- Sekcja może być uznana za ukończoną po pozytywnej weryfikacji przez lead developer lub poprzez automated tests

## Informacje, które należy przekazać do kolejnych sekcji
- Struktura szablonów i sposób includowania komponentów
- Dostępne zmienne w szablonach (np. `current_user`, `authenticated`)
- Przykłady użycia komponentów UI w konkretnych stronach
- Informacje o klasach CSS i identyfikatorach używanych w komponencie (dla stylizacji w sekcji 03)
- Interfejs do sprawdzania stanu uwierzytelniania w szablonach (z sekcji 06)

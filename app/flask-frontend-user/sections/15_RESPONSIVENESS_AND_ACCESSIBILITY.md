# 15_RESPONSIVENESS_AND_ACCESSIBILITY.md
## Responsywność, obsługa klawiatury, semantyczny HTML, kontrast i dostępność

## Cel sekcji
Zaimplementowanie odpowiedzialności i dostępności aplikacji Flask dashboardu, zapewniającą, że interfejs jest używalny na różnych urządzeniach i przez użytkowników z różnymi potrzebami. Sekcja obejmuje responsywny układ, nawigację klawiaturą, semantyczny HTML, odpowiedni kontrast kolorów oraz zgodność ze standardami dostępności (WCAG).

## Kontekst i zależności
Ta sekcja zależy od:
- 01_PROJECT_ANALYSIS.md (zrozumienie wymagań projektu)
- 02_ARCHITECTURE.md (wzorzec architektoniczny)
- 03_DESIGN_SYSTEM.md (kolory, typografia, odstępy, które muszą być dostępne)
- 04_ENVIRONMENT_AND_CONFIGURATION.md (konfiguracja)
- 05_FLASK_FOUNDATION.md (struktura aplikacji)
- 07_SHARED_LAYOUT_AND_NAVIGATION.md (layout i nawigacja które muszą być responsywne i dostępne)
Nie ma zależności od innych sekcji implementacyjnych, ale jest wymagana dla wszystkich sekcji które tworzą interfejs użytkownika.

## Stan początkowy
- Katalog `flask-frontend-user` zawiera podstawową strukturę Flaska, szablony layoutu i klienta API
- Brak zdefiniowanych zasad responsywności lub dostępności
- Brak przetestowanej responsywności na różnych urządzeniach

## Szczegółowy zakres implementacji
### 1. Responsywność układu
- Zastosowanie podejścia mobile-first lub desktop-first w zależności od rzeczywistego użytkowania
- Zdefiniowanie punktów przerywania (breakpoints) dla różnych rozmiarów ekranów:
  - Extra small (mobile < 576px)
  - Small (mobile ≥ 576px)
  - Medium (tablet ≥ 768px)
  - Large (desktop ≥ 992px)
  - Extra large (large desktop ≥ 1200px)
- Wykorzystanie jednostek względnych (%, rem, em) zamiast stałych pikseli gdzie to możliwe
- Elastyczne kontenery (flexbox lub CSS grid) które dostosowują się do dostępnej przestrzeni
- Ukrywanie lub pokazywanie określonych elementów w zależności od rozmiaru ekranu (np. menu nawigacyjne zamienia się w hamburger na małych ekranach)
- Responsywne obrazy i media (jeśli stosowane)
- Responsywna typografia (rozmiary czcionek które skalują się z szerokością ekranu)

### 2. Obsługa klawiatury
- Wszystkie interaktywne elementy (przyciski, linki, pola formularza, kontrolki) muszą być dostępne poprzez nawigację klawiaturą (Tab, Shift+Tab)
- Logiczną kolejność fokusa która podąża za kolejnością czytania (od góry do dołu, od lewej do prawej)
- Widoczny fokus (focus ring) który jest wyraźnie widoczny i spełnia wymagania kontrastu
- Obsługa klawisza Enter i Space dla aktywowania przycisków i kontrolek
- Obsługa klawiszy strzałek dla komponentów takich jak rozwijane listy, suwaki, karuzele
- Obsługa klawisza Escape dla zamykania rozwijanych menu, modalnych okien i tooltipów
- Obsługa klawiszy Page Up, Page Down, Home, End dla długich list i stron
- Unikanie zatrzymywania fokusa (focus trap) poza przypadkami specjalnymi (np. modalne okno)

### 3. Semantyczny HTML
- Użycie odpowiednich znaczników HTML5 które przekazują strukturę i znaczenie:
  - `<header>`, `<nav>`, `<main>`, `<section>`, `<article>`, `<aside>`, `<footer>`
  - `<h1>`-`<h6>` dla nagłówków w hierarchicznej kolejności
  - `<ul>`, `<ol>`, `<dl>` dla list
  - `<table>` dla danych tabelarycznych z odpowiednimi `<th>`, `<td>`, `<caption>`
  - `<form>` dla formularzy z odpowiednimi `<label>`, `<input>`, `<select>`, `<textarea>`, `<button>`
  - `<button>` dla przycisków (zamiast `<div>` lub `<span>` z obsługą kliknięcia)
  - `<label>` powiązany z polem formularza poprzez `for` i `id`
  - `<fieldset>` i `<legend>` dla grupowania powiązanych pól formularza
- Unikanie znaczników które nie mają znaczenia semanticznego gdy dostępny jest odpowiednik semanticzny
- Użycie ARIA atrybutów tylko wtedy gdy semanticzny HTML nie wystarcza (prefers semantic first)

### 4. Kontrast kolorów
- Zapewnienie wystarczającego kontrastu między tekstem a tłem zgodnie z WCAG 2.1:
  - Minimum 4.5:1 dla normalnego tekstu (poziom AA)
  - Minimum 3:1 dla dużego tekstu (poziom AA)
  - Minimum 4.5:1 dla grafiki i komponentów interfejsu użytkownika (poziom AA)
- Testowanie kombinacji kolorów z design systemu pod kątem kontrastu
- Dostarczanie alternatywnych wersji kolorów lub trybu wysokiego kontrastu jeśli wymagane
- Unikanie przekazywania informacji wyłącznie za pomocą koloru (np. błąd powinien być również oznaczony ikoną lub tekstem)

### 5. Dostępność multimedialna
- Jeśli stosowane są obrazy, ikony lub inne elementy niemowy:
  - Tekst alternatywny (alt) dla obrazów które przekazują informacje
  - Pusty alt (`alt=""`) dla obrazów czysto dekoracyjnych
  - Opisy audio lub transkrypcje dla treści audio-wideo (jeśli stosowane)
  - Kontrolki odtwarzania które są dostępne klawiaturą i etykietowane

### 6. Dostępność dynamicznej zawartości
- Jeśli zawartość jest aktualizowana bez przeładowania strony (AJAX, WebSockets):
  - Informowanie czytników ekranu o zmianach (np. przy użyciu ARIA live regions)
  - Zapewnienie że nowe fokusa są logiczne i przewidywalne
  - Unikanie automatycznych przejść lub animacji które mogą zdezorientować użytkownika
  - Zachowanie stanu fokusa podczas aktualizacji zawartości (gdzie to możliwe)

### 7. Dostępność formularzy
- Jasno związane etykiety z polami formularza
- Komunikaty o błędach walidacji które są powiązane z odpowiednimi polami (np. poprzez ARIA describedby)
- Sekwencja fokusa która logicznie przechodzi przez pola formularza
- Opcjonalnie: autofokus na pierwszym polu formularza przy ładowaniu (uważaj aby nie dezorientować)
- Grupowanie powiązanych pól w fieldsetach z odpowiednimi legendami
- Dostępne kontrolki takie jak suwaki, przełączniki, wybory daty

### 8. Nawigacja i struktura strony
- Logiczną i przewidywalną strukturę nagłówków (tylko jeden h1 na stronę, następnie h2, h3 itd.)
- Dostępna nawigacja która pozwala na pominięcie powtarzającej się zawartości (np. link "Skip to main content")
- Jasne tytuły stron które odzwierciedlają zawartość i są unikalne
- Logiczną kolejność fokusa która podąża za strukturą wizualną
- Unikanie pułapek fokusa poza przypadkami specjalnymi (np. modalne okno)

### 9. Testowanie dostępności
- Ręczne testowanie nawigacji klawiaturą
- Testowanie z użyciem czytników ekranu (NVDA, JAWS, VoiceOver)
- Testowanie kontrastu kolorów (np. używając WebAIM Contrast Checker)
- Testowanie z wyłączonym CSS aby sprawdzić kolejność czytania
- Testowanie przy różnych rozmiarach czcionek (powiększenie tekstu do 200%)
- Testowanie z wyłączonymi obrazami

## Konkretne zadania do wykonania
1. Przejrzeć wszystkie istniejące szablony HTML i komponenty pod kątem:
   - Semantycznego HTML
   - Obsługi klawiatury
   - Kontrastu kolorów
   - Responsywności
2. Zaimplementować brakujące elementy semantyczne gdzie to konieczne
3. Zapewnić logiczną kolejność fokusa poprzez odpowiednią kolejność elementów w DOM
4. Dodawać widoczne style fokusa które są zgodne z design systemem (zmodyfikować lub dodać w CSS)
5. Zaimplementować link "Skip to main content" na górze każdej strony
6. Zaimplementować odpowiednie etykiety ARIA gdzie semanticzny HTML nie wystarcza
7. Zaimplementować responsywne punkty przerywania i przetestować na różnych szerokościach ekranu
8. Zaimplementować obsługę klawiszy specjalnych (Enter, Space, Escape, strzałki) dla komponentów interaktywnych
9. Zaimplementować ostrzeżenia o błędach walidacji które są powiązane z polami formularza
10. Zaimplementować komunikaty o stanie ładowania które są dostępne czytnikom ekranu (np. przy użyciu ARIA live region dla paska postępu)
11. Przegrać i dostosować kolory z design systemu aby zapewnić wystarczający kontrast
12. Napisać testy jednostkowe i integracyjne sprawdzające odpowiedzialność i dostępność (zobacz sekcje 17 i 18)

## Wymagania techniczne
- Jinja2 dla renderowania szablonów
- CSS3 dla responsywności (media queries, flexbox, grid)
- Brak dodatkowych bibliotek wymaganych dla podstawowej odpowiedzialności i dostępności
- Opcjonalnie: biblioteka do testowania dostępności (ale można testować ręcznie)

## Wymagania wizualne
- Responsywność:
  - Układ dostosowuje się płynnie do różnych rozmiarów ekranów
  - Treść pozostaje czytelna i używalna bez konieczności poziomego przewijania
  - Elementy interfejsu zachowują swoją funkcjonalność na wszystkich rozmiarach
- Dostępność:
  - Widoczny fokus który jest wyraźnie odróżnialny od stanu normalnego
  - Kontrast kolorów spełniający wymagania WCAG 2.1 AA
  - Semantyczny HTML który przekazuje strukturę strony
  - Obsługa klawiatury która pozwala na wykonanie wszystkich działań bez myszki

## Pliki, które należy utworzyć lub zmodyfikować
- Wszystkie istniejące pliki szablonów HTML (`app/templates/*.html`)
- Wszystkie istniejące pliki komponentów (`app/templates/components/*.html`)
- Pliki CSS (`app/static/css/*.css`) - dodanie odpowiedzialności i poprawek dostępności
- Pliki JavaScript jeśli potrzebne dla obsługi klawiatury lub dynamicznej zawartości
- Dodanie komentarzy w kodzie wskających gdzie zastosowano środki dostępności

## Integrację z pozostałymi elementami systemu
- Sekcja jest integrowana z:
  - Sekcją 07 (Shared Layout) - zapewnienie że layout bazowy jest responsywny i dostępny
  - Sekcją 08 (Dashboard Overview) - responsywne karty urządzeń, dostępne filtry i przyciski
  - Sekcją 09 (Measurements and History) - responsywna tabela z dostępnym sortowaniem i paginacją
  - Sekcją 10 (Charts and Analytics) - responsywne wykresy, dostępne kontrolek i tooltipy
  - Sekcją 11 (Device Status and Diagnostics) - responsywne karty urządzeń, dostępne szczegóły
  - Sekcją 12 (Settings and Additional Features) - responsywne formularze z dostępną walidacją
  - Sekcją 13 (AnimeJS and Interactions) - zapewnienie że animacje nie utrudniają dostępu
  - Sekcją 14 (Loading, Empty, Error States) - dostępne komunikaty o stanie
  - Sekcją 16 (Security and Reliability) - dostępne komunikaty o błędach uwierzytelniania

## Obsługę błędów i przypadków brzegowych
- Konflikt między responsywnością a dostępnością: wybór rozwiązania które spełnia oba wymagania (np. responsywne menu które jest również dostępne klawiaturą)
- Ograniczona przestrzeń na małych ekranach: priorytetyzacja najważniejszych treści i działań
- Użytkownicy z niezwykłymi ustawieniami (np. bardzo duża czcionka): zapewnienie że layout nie łamie się
- Starsze przeglądarki: zapewnienie podstawowej funkcjonalności bez zaawansowanych funkcji CSS/JS
- Wydajność: unikanie kosztownych operacji JavaScript podczas przewijania lub zmiany rozmiaru

## Testy wymagane do uznania sekcji za ukończoną
- Testy responsywności (sprawdzenie układu na różnych szerokościach ekranu: 320px, 768px, 1024px, 1440px, 1920px)
- Testy obsługi klawiatury (nawigacja przez wszystkie strony za pomocą jedynie klawiatury)
- Testy kontrastu kolorów (sprawdzenie że wszystkie kombinacje tekstu/tła spełniają wymagania WCAG 2.1 AA)
- Testy semantycznego HTML (sprawdzenie użycia odpowiednich znaczników)
- Testy dostępności z czytnikami ekranu (jeśli dostępne)
- Testy podwyższania kontrastu lub trybu wysokiego kontrastu (jeśli implementowane)
- Testy powiększania tekstu (sprawdzenie że layout nie łamie się przy powiększeniu tekstu do 200%)

## Jednoznaczne kryteria akceptacji
- Aplikacja jest responsywna i działa poprawnie na szerokościach ekranów od 320px do 1920px
- Wszystkie interaktywne elementy są dostępne poprzez nawigację klawiaturą
- Widoczny fokus jest wyraźnie widoczny i spełnia wymagania kontrastu
- Kontrast kolorów spełnia wymagania WCAG 2.1 AA dla normalnego i dużego tekstu oraz komponentów interfejsu
- Semantyczny HTML jest używany odpowiednio w całej aplikacji
- Sekcja może być uznana za ukończoną po pozytywnej weryfikacji przez lead developer lub poprzez automated tests

## Zależności od innych sekcji
- Zależna od: wszystkie poprzednie sekcje (01-14) ponieważ odpowiedzialność i dostępność dotyczą całej aplikacji
- Wymagana przez: żadna sekcja nie jest ścisłe zależna od tej sekcji (odpowiedzialność i dostępność są wymaganiami przekrojowymi)
- Jednak wszystkie sekcje które tworzą interfejs użytkownika (07-14) muszą spełniać wymagania tej sekcji

## Warunki zakończenia prac
- Wszystkie strony i komponenty aplikacji są responsywne
- Wszystkie interaktywne elementy są dostępne klawiaturą
- Wszystkie kolory spełniają wymagania kontrastu
- Semantyczny HTML jest używany odpowiednio
- Sekcja może być uznana za ukończoną po pozytywnej weryfikacji przez lead developer lub poprzez automated tests

## Informacje, które należy przekazać do kolejnych sekcji
- Zdefiniowane punkty przerywania dla responsywności
- Przykłady implementacji semantycznego HTML dla typowych komponentów
- Przykłady implementacji widocznego fokusa
- Informacje o klasach CSS używanych dla responsywności (np. klasy ukrywania/pokazywania przy określonych szerokościach)
- Przykłady implementacji dostępnych komponentów formularza
- Przykłady implementacji dostępnej nawigacji i struktury strony
- Informacje o przetestowanych kombinacjach kolorów z design systemu

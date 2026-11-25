# 12_SETTINGS_AND_ADDITIONAL_FEATURES.md
## Ustawienia oraz pozostałe funkcje wynikające z rzeczywistych wymagań i możliwości backendu

## Cel sekcji
Zaimplementowanie strony ustawień użytkownika oraz dodatkowych funkcji, które wynikają z rzeczywistych możliwości backendu Analizator Deszczówki. Sekcja obejmuje zarządzanie profilem, urządzeniami, powiadomieniami oraz innymi konfiguracjami dostępnymi poprzez API.

## Kontekst i zależności
Ta sekcja zależy od:
- 01_PROJECT_ANALYSIS.md (zrozumienie rzeczywistych wymagań i możliwości backendu)
- 02_ARCHITECTURE.md (wzorzec architektoniczny)
- 03_DESIGN_SYSTEM.md (stylizacja formularzy i komponentów)
- 04_ENVIRONMENT_AND_CONFIGURATION.md (konfiguracja)
- 05_FLASK_FOUNDATION.md (routing i struktura)
- 06_BACKEND_INTEGRATION.md (komunikacja z backendem)
- 07_SHARED_LAYOUT_AND_NAVIGATION.md (layout i nawigacja)
Nie ma zależności od innych sekcji implementacyjnych.

## Stan początkowy
- Katalog `flask-frontend-user` zawiera podstawową strukturę Flaska, szablony layoutu i klienta API
- Brak istniejącej strony ustawień
- Brak komponentów formularzy do zarządzania ustawieniami

## Szczegółowy zakres implementacji
### 1. Struktura strony ustawień
- Utworzenie kontrolera Flask dla ustawień w `app/controllers/settings.py` lub bezpośrednio w `app/routes.py`
- Utworzenie szablonu HTML `app/templates/settings/index.html` dla głównej strony ustawień
- Strona będzie wykorzystywać layout bazowy z sekcji 07
- Strona ustawień może być podzielona na zakładki lub sekcje dla lepszej organizacji

### 2. Zakładki/sekcje ustawień
Strona ustawień będzie podzielona na następujące sekcje (w zależności od rzeczywistych możliwości backendu):

#### Profil użytkownika
- Edytowanie podstawowych informacji:
  - Imię i nazwisko
  - Adres e-mail (może być tylko do odczytu jeśli używany do logowania)
  - Numer telefonu (opcjonalnie)
  - Avatar lub zdjęcie profilowe (opcjonalnie)
- Zmiana hasła:
  - Pole na obecne hasło
  - Pole na nowe hasło
  - Pole na potwierdzenie nowego hasła
- Preferencje językowe i regionalne (jeśli wspierane przez backend)

#### Zarządzanie urządzeniami
- Dodawanie nowego urządzenia:
  - Formularz z polami:
    - Nazwa urządzenia
    - Lokalizacja
    - Typ/Model urządzenia (jeśli istotne dla konfiguracji)
    - Klucz API lub kod parowania (jeśli wymagany przez backend)
- Edytowanie istniejącego urządzenia:
  - Te same pola co przy dodawaniu
  - Informacje o stanie urządzenia (online/offline, ostatni kontakt)
- Usuwanie urządzenia (z potwierdzeniem)
- Informacje o limitach (jeśli istnieją): maksymalna liczba urządzeń na użytkownika

#### Powiadomienia i alerty
- Konfiguracja powiadomień e-mail (jeśli wspierane przez backend):
  - Włącz/Wyłącz powiadomienia e-mail
  - Typy zdarzeń powiadamiania:
    - Przekroczenie progów wartości (pH, mętność, etc.)
    - Utrachata połączenia z urządzeniem
    - Konserwacja wymagana
  - Progi wartości dla każdego parametru (konfigurolne przez użytkownika)
- Powiadomienia w aplikacji (jeśli wspierane):
  - Włącz/Wyłącz powiadomienia w przeglądarce
  - Częstotliwość przypomnień

#### Jednostki i formaty
- Wybór jednostek dla wyświetlania (jeśli backend wspiera konwersję lub przechowuje w jednostkach podstawowych):
  - Temperatura: °C vs °F
  - Przepływ: L/min vs GPM
  - Inne parametry jeśli適用
- Format daty i czasu:
  - Format daty: DD/MM/YYYY vs MM/DD/YYYY vs YYYY-MM-DD
  - Format czasu: 24h vs 12h
  - Strefa czasowa

#### Ustawienia systemowe (jeśli dostępne przez backend)
- Informacje o użyciu zasobów (jeśli udostępnione przez backend)
- Historia logowań
- Sesje aktywne
- Klucze API lub tokeny dostępu (zarządzanie)
- Ustawienia prywatności i udostępniania danych

### 3. Dodatkowe funkcje wynikające z backendu
Na podstawie analizy backendu, zaimplementować funkcje które są rzeczywiście wspierane:

#### Parowanie urządzeń
- Jeśli backend wspiera endpoint `/api/v1/devices/pair`:
  - Formularz do wprowadzania kodu parowania
  - Instrukcje jak uruchomić tryb parowania na urządzeniu ESP32
  - Status procesu parowania

#### Aktualizacja firmware
- Jeśli backend wspiera aktualizację firmware urządzeń:
  - Informacje o aktualnej wersji firmware
  - Informacje o dostępnej nowej wersji
  - Przycisk do zainicjowania aktualizacji
  - Status procesu aktualizacji

#### Kalibracja czujników
- Jeśli backend wspiera operacje kalibracji:
  - Informacje o ostatniej kalibracji
  - Przycisk do zainicjowania kalibracji
  - Instrukcje jak przygotować urządzenie do kalibracji
  - Status procesu kalibracji

#### Eksport danych
- Jeśli backend wspiera eksport lub jeśli możemy zaimplementować eksport po stronie frontendowej:
  - Eksport pomiarów do CSV
  - Eksport pomiarów do JSON
  - Wybór zakresu czasu i urządzeń do eksportu
  - Format eksportu (CSV, JSON, Excel)

### 4. Pobieranie i wysyłanie danych
- Wykorzystanie klienta API z sekcji 06 do:
  - Pobierania obecnych ustawień użytkownika: zależnie od dostępnych endpointów (sprawdzić w backendzie)
  - Aktualizacji ustawień użytkownika: `PUT /api/v1/auth/me` lub podobny endpoint
  - Pobierania listy urządzeń: `GET /api/v1/devices/`
  - Dodawania nowego urządzenia: `POST /api/v1/devices/`
  - Aktualizacji urządzenia: `PUT /api/v1/devices/{device_id}`
  - Usuwania urządzenia: `DELETE /api/v1/devices/{device_id}`
  - Pobierania informacji o urządzeniu dla edycji: `GET /api/v1/devices/{device_id}`
  - Operacji na urządzeniach (pair, code, heartbeat): odpowiednie endpointy z sekcji 06
- Implementacja stanu ładowania podczas pobierania/zapisu ustawień (komponent z sekcji 14)
- Implementacji obsługi błędów podczas komunikacji z backendem (komunikaty użytkownikowi)
- Walidacji formularzy po stronie klienta przed wysłaniem do backendu

### 5. Formatowanie i walidacja
- Walidacja formularzy po stronie klienta (np. wymagane pola, format e-mail, silność hasła)
- Wyświetlanie błędów walidacji przy odpowiednich polach
- Formatowanie danych do wyświetlania (daty, liczby, etc.)
- Obsługa wartości pustych i wartości domyślnych
- Przywracanie wartości z backendu przy ładowaniu strony ustawień

### 6. Responsywność
- Formularze dostosowujące się do szerokości ekranu:
  - Na dużych ekranach: pola obok siebie (np. imię i nazwisko w jednej linii)
  - Na małych ekranach: pola jednej pod drugą
- Zakładki mogą zamieniać się w akordeon na małych ekranach
- Przyciski dostosowujące swój rozmiar i układ

## Konkretne zadania do wykonania
1. Utworzyć kontroler/route dla ustawień (np. `@app.route('/settings')`)
2. Utworzyć szablon HTML dla strony ustawień
3. Zaimplementować logikę pobierania ustawień użytkownika z backendu (jeśli dostępne)
4. Zaimplementować logikę aktualizacji ustawień użytkownika
5. Zaimplementować formularze zarządzania urządzeniami (dodawanie, edytowanie, usuwanie)
6. Zaimplementować sekcję powiadomień jeśli wspierana przez backend
7. Zaimplementować sekcję jednostek i formatów jeśli stosowne
8. Zaimplementować dodatkowe funkcje wynikające z analizy backendu (parowanie, aktualizacja firmware, etc.)
9. Zaimplementować stan ładowania i obsługę błędów
10. Zaimplementować walidację formularzy po stronie klienta
11. Zaimplementować responsywny układ strony
12. Dodawać odpowiednie klasy CSS zgodnie z design systemem
13. Napisać testy jednostkowe i integracyjne dla kontrolera i szablonu (zobacz sekcje 17 i 18)

## Wymagania techniczne
- Dostęp do klienta API z sekcji 06
- Jinja2 dla renderowania szablonów
- Brak dodatkowych bibliotek wymaganych dla podstawowej funkcjonalności
- Opcjonalnie: biblioteka do walidacji formularzy (np. WTForms jeśli używana z Flaskiem, lub ręczna walidacja)
- Opcjonalnie: biblioteka do obsługi dat (np. `python-dateutil`)

## Wymagania wizualne
- Strona ustawień powinna być przejrzysta i dobrze zorganizowana
- Formularze powinny mieć wyraźnie opisane pola
- Sekcje powinny być oddzielone wyraźnymi nagłówkami lub zakładkami
- Pola formularza (input, select, textarea) zgodne z design systemem
- Przyciski zgodne z design systemem (różne style dla głównych i sekundarnych akcji)
- Komunikaty walidacji wyraźnie widoczne przy odpowiednich polach
- Ikony lub wizualne wskaźniki (opcjonalnie, jeśli wspierane przez design system)

## Pliki, które należy utworzyć lub zmodyfikować
- `app/routes.py` lub podobny - dodanie route dla ustawień
- `app/controllers/settings.py` - nowy plik kontrolera (opcjonalnie)
- `app/templates/settings/index.html` - nowy plik szablonu dla głównej strony ustawień
- `app/templates/settings/profile.html` - szablon dla sekcji profilu (opcjonalnie, można umieścić w głównym szablonie)
- `app/templates/settings/devices.html` - szablon dla sekcji urządzeń (opcjonalnie)
- `app/templates/settings/notifications.html` - szablon dla sekcji powiadomień (opcjonalnie)
- Komponenty UI do wykorzystania w szablonach (formularze, przyciski, pola input)
- Pliki statyczne (CSS/JS) jeśli potrzebne dla konkretnych efektów na tej stronie

## Integrację z pozostałymi elementami systemu
- Strona ustawień będzie wykorzystywać:
  - Layout bazowy z sekcji 07
  - Komponenty UI z sekcji 07 i 14 (loading, empty state, error)
  - Klient API z sekcji 06 do pobierania i wysyłania danych
  - Mechanizm uwierzytelniania (sprawdzenie czy użytkownik jest zalogowany)
  - Nawigację z sekcji 07 (aktywny element w menu)
  - Animacje przejść z sekcji 13 (opcjonalnie)
  - Responsywność z sekcji 15
  - Obsługę błędów z sekcji 14 i 16
  - Informacje mogą być wykorzystywane przez sekcję 08 (Dashboard Overview) do pokazywania podstawowych informacji o urządzeniach
  - Informacje mogą być wykorzystywane przez sekcję 11 (Device Status) do synchronizacji stanu urządzeń

## Obsługę błędów i przypadków brzegowych
- Brak uprawnień do zmiany ustawień: pokazanie komunikatu o braku uprawnień
- Błąd połączenia z backendem: pokazanie komunikatu o problemach z połączeniem i możliwość ponowienia próby
- Nieprawidłowe dane w formularzu: walidacja i pokazanie komunikatów użytkownikowi
- Konflikt przy dodawaniu urządzenia (np. urządzenie już istnieje): komunikatu użytkownikowi
- Błąd aktualizacji ustawień: pokazanie komunikatu o błędzie i możliwość ponowienia próby
- Sesja wygasła podczas edycji: automatyczne przekierowanie do logowania
- Próba dostępu do ustawień przez niezalogowanego użytkownika: przekierowanie do strony logowania
- Problemy z walidacją po stronie backendu: pokazanie komunikatów zwróconych przez backend

## Testy wymagane do uznania sekcji za ukończoną
- Testy jednostkowe dla kontrolerów/logiki pobierania i aktualizacji ustawień
- Testy integracyjne sprawdzające renderowanie strony ustawień z różnymi danymi wejściowymi
- Testy sprawdzające obsługę przypadków brzegowych (brak danych, błąd połączenia, nieprawidłowe formularze, itp.)
- Testy walidacji formularzy (pozytywne i negatywne przypadki)
- Testy responsywności (sprawdzenie układu na różnych szerokościach ekranu)
- Testy dostępności (sprawdzenie semantycznego HTML, etykiet ARIA, nawigacji klawiaturą)

## Jednoznaczne kryteria akceptacji
- Strona ustawień jest dostępna po zalogowaniu pod odpowiednim URL (np. `/settings`)
- Strona wykorzystuje layout bazowy z sekcji 07
- Strona pozwala na wyświetlanie i edytowanie dostępnych ustawień użytkownika
- Strona pozwala na zarządzanie urządzeniami (dodawanie, edytowanie, usuwanie)
- Strona prawidłowo pobiera i wysyła dane do backendu
- Strona jest responsywna i działa na szerokościach od 320px do 1920px
- Strona prawidłowo obsługuje stany ładowania, puste dane i błędy
- Strona jest łatwa w użyciu poprzez intuicyjny interfejs i nawigację

## Zależności od innych sekcji
- Zależna od: wszystkie poprzednie sekcje (01-11)
- Wymagana przez: sekcje które mogą potrzebować informacji o ustawieniach (np. sekcje 08, 10, 11 mogą wykorzystywać preferencje jednostek)

## Warunki zakończenia prac
- Strona ustawień jest w pełni zaimplementowana i zintegrowana z layoutem
- Wszystkie komponenty strony są stworzone i działają poprawnie
- Strona prawidłowo zarządza ustawieniami użytkownika i urządzeniami poprzez komunikację z backendem
- Sekcja może być uznana za ukończoną po pozytywnej weryfikacji przez lead developer lub poprzez automated tests

## Informacje, które należy przekazać do kolejnych sekcji
- Przykłady użycia klienta API do pobierania i aktualizacji ustawień użytkownika
- Przykłady użycia klienta API do zarządzania urządzeniami
- Formaty danych zwracane przez funkcje API (po mapowaniu z sekcji 06)
- Wzorce tworzenia komponentów formularza zarządzania ustawieniami
- Informacje o klasach CSS i identyfikatorach używanych w stronie (dla stylizacji w sekcji 03)
- Przykłady implementacji stanu ładowania i obsługi błędów
- Przykłady implementacji walidacji formularzy po stronie klienta
- Przykłady implementacji dodatkowych funkcji (parowanie urządzeń, aktualizacja firmware, etc.) jeśli wspierane przez backend

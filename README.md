# Manipulator-z-elektromagnesem

Projekt studencki trójosiowego ramienia robotycznego z efektonem końcowym w postaci elektromagnesu. Urządzenie pozwala na bezprzewodowe sortowanie i przenoszenie małych elementów metalowych (np. śrubek) za pomocą panelu sterowania w przeglądarce internetowej.

Architektura Systemu
System działa w architekturze klient-serwer z komunikacją przez bezstanowy protokół HTTP:
1. Frontend & Backend (Flask): Aplikacja w Pythonie uruchomiona w chmurze (PythonAnywhere). Sterowanie odbywa się za pomocą suwaków JavaScript, a aktualny stan matrycy przeznaczony jest bezpośrednio w pamięci RAM serwera (optymalizacja dla środowiska darmowego).
2. Firmware (ESP32): Kod w C++ (Arduino IDE) cyklicznie odpytuje serwer co 800 ms (polling), pobiera dane JSON i steruje serwomechanizmami (z autorskim algorytmem interpolacji krokowej dla płynnego ruchu) oraz aktywuje elektromagnes.

Elektronika i Zabezpieczenia
* Logika: Wykorzystuje ESP32 zasilane z 5V.
* Moc: Serwomechanizmy (2x MG-995, 1x AR-3606HB) oraz elektromagnes pracują w obwodzie 6V zasilanym przez przetwornicę step-up, co izoluje mikrokontroler od zakłóceń indukcyjnych.
* Układ został zaprojektowany w programie KiCAD i przetestowany pod kątem tłumienia szumów w LTSpice.

Konstrukcja Mechaniczna
* Wszystkie elementy zostały zaprojektowane w CAD i wydrukowane z wytrzymałego filamentu PET-G.
* Konstrukcja posiada wewnętrzne kanały na estetyczne i bezpieczne poprowadzenie okablowania.
* Zakładany udźwig wynosi do 150 g.

Skład Zespołu
* Zuzanna Głowacz
* Filip Żórawski
* Konrad Teplicki
* Norbert Pala

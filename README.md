# URL zu PDF Konverter

Ein Tool, um mehrere Webseiten (auch komplizierte) in ein einziges, sauber formatiertes PDF-Dokument umzuwandeln. Die fertigen PDFs werden automatisch mit dem Datum und Inhalt benannt und in einer organisierten Ordnerstruktur abgelegt.

![image](https://github.com/user-attachments/assets/3035f2b3-a01a-417d-b657-0f535e280ec1)
![image](https://github.com/user-attachments/assets/b3814bde-b1fd-4462-8f04-6deab115d6c5)



---

## ✨ Features

- **Robuste PDF-Erstellung:** Funktioniert auch bei Webseiten, bei denen andere Tools versagen.
- **Intelligente Ordnerstruktur:** Speichert PDFs automatisch in Ordnern, die nach dem aktuellen Datum benannt sind (z.B. `/fertige_pdfs/11.07.2024/`).
- **Dynamische Dateinamen:** Benennt PDFs automatisch nach dem Schema `<Tag.Monat> <Inhaltstitel 1> <Inhaltstitel 2>....pdf`.
- **Automatische Formatierung:** Entfernt die ersten beiden Seiten und verhindert unschöne Seitenumbrüche im Dokument.
- **Einfacher Start:** Eine `start_konverter.bat` Datei startet alles mit einem Doppelklick.
- **Bequemer Zugriff:** Ein "Ordner öffnen"-Button auf der Erfolgsseite öffnet direkt den Speicherort der Datei.

---

## 🚀 Setup (Einmalige Einrichtung)

### Voraussetzungen
- **Windows** Betriebssystem
- **Python** (Version 3.8 oder neuer) muss installiert sein. [Download hier](https://www.python.org/downloads/).
- **Brave Browser** oder **Google Chrome** muss installiert sein.

### Installationsschritte

1.  **Projekt herunterladen:**
    Lade dieses Projekt als ZIP-Datei herunter und entpacke den Ordner an einem beliebigen Ort auf deinem PC (z.B. auf dem Desktop).

2.  **Abhängigkeiten installieren:**
    - Öffne den Projektordner.
    - Mache einen Doppelklick auf die Datei `install_requirements.bat`.
    - Ein Fenster öffnet sich und installiert die notwendigen Pakete. Warte, bis es sich von selbst schließt oder "Drücken Sie eine beliebige Taste..." anzeigt.

*(Hinweis: Falls du die `install_requirements.bat` nicht findest, erstelle sie als Textdatei und füge `pip install Flask selenium pypdf` ein, dann benenne sie um.)*

---

## 🏃 Anwendung

1.  **App starten:**
    Mache einen **Doppelklick** auf die Datei `start_konverter.bat`.

2.  **Konvertieren:**
    - Dein Browser öffnet sich automatisch mit der Web-Oberfläche.
    - Füge eine oder mehrere Webseiten-Links in das große Textfeld ein (jeder Link in eine neue Zeile).
    - Klicke auf den Button **"PDFs erstellen und herunterladen"**.

3.  **Ergebnis finden:**
    - Nach kurzer Zeit erscheint eine Erfolgsseite.
    - Klicke dort auf den Button **"Zielordner öffnen"**, um direkt zum Speicherort deines neuen PDFs zu gelangen.
    - Alle erstellten Dokumente findest du im Projektordner unter `/fertige_pdfs/`.

---

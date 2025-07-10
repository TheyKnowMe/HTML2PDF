# -*- coding: utf-8 -*-

import os
import uuid
import base64
import time
import traceback
import re
from datetime import datetime
from flask import Flask, render_template, request, send_file, after_this_request, redirect, url_for # redirect/url_for sind jetzt dabei
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pypdf import PdfWriter

# --- Initialisierung ---
app = Flask(__name__)
TEMP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp')
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fertige_pdfs')

if not os.path.exists(TEMP_DIR): os.makedirs(TEMP_DIR)
if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)


# --- HILFSFUNKTIONEN ---

# NEU: Diese Funktion sucht automatisch nach Brave oder Chrome
def find_browser_executable():
    """
    Sucht nach der ausführbaren Datei von Brave oder Chrome an Standardorten.
    Gibt den Pfad des ersten gefundenen Browsers zurück.
    """
    # Liste der möglichen Pfade in der gewünschten Priorität (Brave zuerst)
    # Wir berücksichtigen Standard-Installationen und benutzerdefinierte (AppData)
    possible_paths = [
        r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
        # Fallback auf Google Chrome
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    ]
    
    # Füge den benutzer-spezifischen Pfad für Brave hinzu (sehr häufig)
    local_app_data = os.getenv('LOCALAPPDATA')
    if local_app_data:
        possible_paths.insert(1, os.path.join(local_app_data, r"BraveSoftware\Brave-Browser\Application\brave.exe"))

    # Gehe die Liste durch und gib den ersten existierenden Pfad zurück
    for path in possible_paths:
        if os.path.exists(path):
            print(f"Browser gefunden unter: {path}")
            return path
            
    # Wenn kein Browser gefunden wurde
    return None

def inject_print_optimizations(driver):
    # (Diese Funktion bleibt unverändert)
    print("Versuche, CSS für Druck-Optimierung zu injizieren...")
    css = """
    @media print {
        @page { margin: 1.5cm; }
        .py-4, .content-cell, table.inner-body { break-inside: avoid !important; page-break-inside: avoid !important; }
        h1, h2, h3, h4, h5, h6 { break-after: avoid !important; page-break-after: avoid !important; }
        a, img { break-inside: avoid !important; page-break-inside: avoid !important; }
        img { max-width: 100% !important; height: auto !important; }
    }
    """
    script = f"""
    var style = document.createElement('style');
    style.type = 'text/css';
    style.innerHTML = `{css.replace("`", "'")}`;
    document.head.appendChild(style);
    """
    driver.execute_script(script)
    print("CSS für Druck-Optimierung wurde erfolgreich injiziert.")

# GEÄNDERT: Verwendet jetzt die Suchfunktion anstatt eines festen Pfades
def url_to_pdf(url: str, output_path: str) -> (bool, list):
    """
    Steuert einen headless Browser, extrahiert Aktientitel und speichert die Seite als PDF.
    """
    # NEU: Browser-Pfad dynamisch finden
    browser_path = find_browser_executable()
    if not browser_path:
        print("!!!!!!!! FEHLER: Konnte weder Brave noch Google Chrome finden. Bitte einen der Browser installieren. !!!!!!!!")
        return False, []

    chrome_options = Options()
    chrome_options.binary_location = browser_path # GEÄNDERT: Verwendet den gefundenen Pfad
    
    # Rest der Optionen bleibt gleich
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
    chrome_options.add_argument(f'user-agent={user_agent}')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    driver = None
    stock_names = []
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(30)
        
        print(f"Verarbeite URL: {url}")
        driver.get(url)
        
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        try:
            h3_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'py-4')]//h3[string-length(text()) > 0]")
            extracted_names = [elem.text.strip() for elem in h3_elements if elem.text.strip()]
            stock_names = list(dict.fromkeys(extracted_names))
            print(f"Gefundene Aktientitel: {stock_names}")
        except Exception as e:
            print(f"Konnte keine Aktientitel extrahieren: {e}")
        
        inject_print_optimizations(driver)
        time.sleep(1)

        print_options = {'landscape': False, 'displayHeaderFooter': False, 'printBackground': True, 'preferCSSPageSize': True}
        result = driver.execute_cdp_cmd("Page.printToPDF", print_options)
        
        pdf_data = base64.b64decode(result['data'])
        with open(output_path, 'wb') as f: f.write(pdf_data)
        
        print(f"PDF erfolgreich erstellt: {output_path}")
        return True, stock_names

    except Exception as e:
        print(f"!!!!!!!! FEHLER bei der Verarbeitung von {url} !!!!!!!!")
        traceback.print_exc()
        return False, []
    finally:
        if driver: driver.quit()

def merge_pdfs(pdf_files: list, output_path: str):
    # (Diese Funktion bleibt unverändert)
    merger = PdfWriter()
    for pdf_path in pdf_files:
        if os.path.exists(pdf_path): merger.append(pdf_path)
    
    if len(merger.pages) > 2:
        print(f"PDF hat {len(merger.pages)} Seiten. Entferne die ersten beiden...")
        del merger.pages[0]
        del merger.pages[0] 
        print("Die ersten beiden Seiten wurden entfernt.")
    else:
        print(f"PDF hat nur {len(merger.pages)} Seiten. Es werden keine Seiten entfernt.")

    merger.write(output_path)
    merger.close()
    print(f"Alle PDFs zusammengefügt und bearbeitet in: {output_path}")

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)

# --- FLASK ROUTEN ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/open-folder/<path:folder_path>')
def open_folder(folder_path):
    safe_base_path = os.path.abspath(OUTPUT_DIR)
    requested_path = os.path.abspath(folder_path)

    if os.path.exists(requested_path) and requested_path.startswith(safe_base_path):
        try:
            os.startfile(requested_path)
            print(f"Befehl zum Öffnen von Ordner '{requested_path}' gesendet.")
        except Exception as e: print(f"Fehler beim Öffnen des Ordners: {e}")
    else:
        print(f"Unsicherer oder ungültiger Pfad angefordert: {requested_path}")

    return redirect(url_for('index'))

@app.route('/process', methods=['POST'])
def process_urls():
    # ... (Diese Funktion bleibt unverändert)
    urls_text = request.form.get('urls')
    if not urls_text: return "Keine URLs angegeben!", 400
    
    urls = [url.strip() for url in urls_text.splitlines() if url.strip()]
    if not urls: return "Keine gültigen URLs gefunden!", 400
        
    session_id = str(uuid.uuid4())
    session_dir = os.path.join(TEMP_DIR, session_id)
    os.makedirs(session_dir)

    generated_pdfs, all_stock_names = [], []
    
    for i, url in enumerate(urls):
        pdf_filename = f"page_{i+1}.pdf"
        output_path = os.path.join(session_dir, pdf_filename)
        
        success, names = url_to_pdf(url, output_path)
        if success:
            generated_pdfs.append(output_path)
            all_stock_names.extend(names)
            
    if not generated_pdfs: return "Konnte keine der angegebenen URLs in PDF umwandeln.", 500
        
    today = datetime.now()
    date_folder_name = today.strftime("%d.%m.%Y")
    final_output_folder = os.path.join(OUTPUT_DIR, date_folder_name)
    if not os.path.exists(final_output_folder): os.makedirs(final_output_folder)
        
    unique_stock_names = list(dict.fromkeys(all_stock_names))
    sanitized_names = [sanitize_filename(name) for name in unique_stock_names]
    date_part = today.strftime("%d.%m")
    stocks_part = " ".join(sanitized_names)
    final_filename = f"{date_part} {stocks_part}.pdf"
    final_pdf_path = os.path.join(final_output_folder, final_filename)
    
    merge_pdfs(generated_pdfs, final_pdf_path)

    @after_this_request
    def cleanup(response):
        try:
            print(f"Räume temporäre Dateien für Session {session_id} auf...")
            for pdf_file in generated_pdfs:
                if os.path.exists(pdf_file): os.remove(pdf_file)
            if os.path.exists(session_dir): os.rmdir(session_dir)
            print("Aufräumen der temporären Dateien erfolgreich.")
        except Exception as e: print(f"Fehler beim Aufräumen: {e}")
        return response

    return f"""
    <!DOCTYPE html><html lang="de"><head><meta charset="UTF-8"><title>Erfolg!</title><style>body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;padding:2em;background-color:#f4f4f9;color:#333}}.container{{max-width:800px;margin:40px auto;padding:20px;background-color:#fff;border-radius:8px;box-shadow:0 2px 10px rgba(0,0,0,0.1)}}h1{{color:#27ae60}}p{{line-height:1.6}}code{{background-color:#eee;padding:2px 5px;border-radius:4px}}.button{{display:inline-block;padding:12px 25px;margin-top:15px;font-size:16px;color:#fff;background-color:#3498db;text-decoration:none;border-radius:5px;transition:background-color .3s}}.button:hover{{background-color:#2980b9}}.button-secondary{{background-color:#7f8c8d}}.button-secondary:hover{{background-color:#6c7a7d}}</style></head><body><div class="container"><h1>Erfolgreich erstellt!</h1><p>Das PDF wurde erfolgreich generiert und im Zielordner abgelegt.</p><p><b>Dateiname:</b> <code>{final_filename}</code></p><p><b>Speicherort:</b> <code>{final_output_folder}</code></p><a href="{url_for('open_folder', folder_path=final_output_folder)}" class="button">Zielordner öffnen</a> <a href="{url_for('index')}" class="button button-secondary">Zurück zur Startseite</a></div></body></html>
    """

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs' / 'figures'
OUT.mkdir(parents=True, exist_ok=True)

def capture(url='http://localhost:8000/index.html', out_name='dashboard.png'):
    opts = Options()
    opts.headless = True
    opts.add_argument('--no-sandbox')
    opts.add_argument('--disable-dev-shm-usage')
    # Use webdriver-manager to install the correct chromedriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)
    driver.set_window_size(1400, 900)
    driver.get(url)
    # wait for main content or timeline to load
    try:
        WebDriverWait(driver, 8).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#timelineChart, #map')))
    except Exception:
        time.sleep(3)
    outp = OUT / out_name
    driver.save_screenshot(str(outp))
    driver.quit()
    print('Saved', outp)

if __name__=='__main__':
    capture()

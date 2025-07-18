from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

# Setup Chrome browser (non-headless to avoid blocking)
def setup_driver():
    options = Options()
    # Run in visible mode
    # options.add_argument("--headless")  # Don't use headless for page 1
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--log-level=3")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    service = Service()
    return webdriver.Chrome(service=service, options=options)

# Extract product data safely with waits
def extract_product_info(product):
    name, price, old_price, brand, rating, reviews = '', '', '', '', '', ''

    try:
        name_elem = WebDriverWait(product, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h3.name"))
        )
        name = name_elem.text
    except:
        pass

    try:
        price = product.find_element(By.CSS_SELECTOR, "div.prc").text
    except:
        pass

    try:
        old_price = product.find_element(By.CSS_SELECTOR, "div.old").text
    except:
        pass

    try:
        brand = name.split()[0] if name else ''
    except:
        pass

    try:
        rating = product.find_element(By.CSS_SELECTOR, "div.stars").get_attribute("aria-label")
    except:
        pass

    try:
        reviews = product.find_element(By.CSS_SELECTOR, "div.rev").text
    except:
        pass

    return {
        "Product Name": name,
        "Brand": brand,
        "Price": price,
        "Old Price": old_price,
        "Rating": rating,
        "Reviews": reviews
    }

# Scrape the first page with scrolling and full waits
def scrape_page_1():
    url = "https://www.jumia.co.ke/mobile-phones/"
    driver = setup_driver()
    driver.get(url)

    # Gradual scroll to trigger lazy loading (real user behavior)
    for i in range(5):
        driver.execute_script(f"window.scrollBy(0, 800);")
        time.sleep(1.5)  # let products load bit by bit

    # Wait for product cards to load
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article.prd"))
        )
    except:
        print("❌ Timeout waiting for products to load.")
        driver.quit()
        return

    products = driver.find_elements(By.CSS_SELECTOR, "article.prd")
    print(f"✅ Found {len(products)} products on Page 1")

    if not products:
        with open("page1_debug.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("❌ No products found. Saved HTML to 'page1_debug.html'")
        driver.quit()
        return

    # Scrape product data
    data = [extract_product_info(p) for p in products]

    driver.quit()

    # Save to CSV
    df = pd.DataFrame(data)
    df.to_csv("jumia_page1_full.csv", index=False)
    print("✅ Done. Saved as 'jumia_page1_full.csv'.")

# Run the script
if __name__ == "__main__":
    scrape_page_1()


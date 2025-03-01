import streamlit as st
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Konfigurasi WebDriver
@st.cache_resource
def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Jalankan tanpa membuka browser
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Scraping function
def scrape_reviews(place_url, max_scroll=10):
    driver = get_driver()
    driver.get(place_url)
    time.sleep(5)  # Tunggu halaman loading
    
    # Klik tombol "Lihat semua ulasan"
    try:
        review_button = driver.find_element(By.XPATH, "//button[contains(@aria-label, 'ulasan')]")
        review_button.click()
        time.sleep(5)
    except:
        st.error("🚫 Tidak menemukan tombol ulasan!")
        return []

    # Scroll untuk memuat lebih banyak ulasan
    try:
        scrollable_div = driver.find_element(By.CLASS_NAME, "m6QErb.DxyBCb.kA9KIf.dS8AEf")
        for _ in range(max_scroll):
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
            time.sleep(2)
    except:
        st.error("⚠️ Gagal melakukan scrolling!")

    # Ambil data ulasan
    reviews = driver.find_elements(By.CLASS_NAME, "jftiEf.fontBodyMedium")
    review_list = []
    for review in reviews:
        try:
            author = review.find_element(By.CLASS_NAME, "d4r55").text
            rating = review.find_element(By.CLASS_NAME, "kvMYJc").get_attribute("aria-label")
            text = review.find_element(By.CLASS_NAME, "wiI7pd").text
            review_list.append({"Nama": author, "Rating": rating, "Ulasan": text})
        except:
            continue

    driver.quit()
    return review_list

# UI Streamlit
st.set_page_config(page_title="Google Maps Review Scraper", page_icon="🌍")

st.title("🌍 Google Maps Review Scraper")
st.write("Masukkan URL tempat di Google Maps untuk mengambil ulasan.")

place_url = st.text_input("🔗 Masukkan URL Google Maps", "")

if st.button("Scrape Ulasan"):
    if place_url:
        with st.spinner("🔍 Mengambil ulasan..."):
            results = scrape_reviews(place_url)
            if results:
                df = pd.DataFrame(results)
                st.success(f"✅ Berhasil mengambil {len(df)} ulasan!")

                # Tampilkan hasil
                st.subheader("📌 Hasil Ulasan")
                st.dataframe(df)

                # Unduh sebagai CSV
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="⬇️ Unduh CSV",
                    data=csv,
                    file_name="google_maps_reviews.csv",
                    mime="text/csv"
                )
            else:
                st.error("❌ Tidak ada ulasan yang ditemukan.")
    else:
        st.warning("⚠️ Harap masukkan URL Google Maps!")

st.markdown("---")
st.write("Dibuat oleh **Abizar Egi** 🚀")

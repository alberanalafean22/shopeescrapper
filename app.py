import streamlit as st
import requests
import pandas as pd
import time
import io

# ===================== CONFIG =====================
st.set_page_config(
    page_title="Shopee Business Scraper - BPS1372",
    page_icon="🛍️",
    layout="wide"
)

# ===================== CUSTOM CSS (Simplified for brevity) =====================
st.markdown("""
<style>
    .main-title { font-size: 38px; font-weight: 800; color: #ee4d2d; }
    .stButton > button { background: #ee4d2d; color: white; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# ===================== FUNGSI SCRAPING (API BASED) =====================
def search_shopee_shops(keyword, limit=20):
    """
    Mengambil data toko berdasarkan keyword menggunakan API publik Shopee.
    """
    # Header minimal untuk menghindari blokir sederhana
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Referer': 'https://shopee.co.id/search'
    }
    
    # Endpoint pencarian toko (ini contoh endpoint pencarian produk, 
    # lalu kita ambil data shopid-nya untuk mendapatkan detail toko)
    search_url = f"https://shopee.co.id/api/v4/search/search_items?keyword={keyword}&limit={limit}&offset=0&page_type=search&scenario=PAGE_GLOBAL_SEARCH"
    
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        data = response.json()
        items = data.get('items', [])
        
        shops_data = []
        processed_shops = set()

        for item in items:
            shop_id = item.get('item_basic', {}).get('shopid')
            
            if shop_id and shop_id not in processed_shops:
                # Ambil detail Toko
                shop_info_url = f"https://shopee.co.id/api/v4/shop/get_shop_detail?shopid={shop_id}"
                shop_res = requests.get(shop_info_url, headers=headers).json()
                shop_details = shop_res.get('data', {})

                if shop_details:
                    shops_data.append({
                        "Nama Bisnis": shop_details.get('name'),
                        "Username": shop_details.get('account', {}).get('username'),
                        "Lokasi/Alamat": shop_details.get('place'),
                        "URL Toko": f"https://shopee.co.id/{shop_details.get('account', {}).get('username')}",
                        "Rating": round(shop_details.get('rating_star', 0), 2),
                        "Total Produk": shop_details.get('item_count')
                    })
                    processed_shops.add(shop_id)
                
                time.sleep(1) # Delay agar tidak kena banned
        
        return shops_data
    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
        return []

# ===================== SIDEBAR =====================
with st.sidebar:
    st.header("⚙️ Parameter Shopee")
    keyword = st.text_input("Nama Usaha / Produk", placeholder="Contoh: Keripik Sanjai")
    max_results = st.slider("Jumlah Toko", 5, 50, 10)
    start_button = st.button("🚀 Mulai Scrapping")
    st.info("Catatan: Shopee memiliki proteksi tinggi. Jika gagal, coba lagi beberapa saat kemudian.")

# ===================== MAIN UI =====================
st.markdown('<div class="main-title">🛍️ Shopee Business Scraper</div>', unsafe_allow_html=True)
st.write("Mencari informasi toko/bisnis berdasarkan kata kunci produk yang dijual.")

# ===================== PROCESS =====================
if start_button:
    if not keyword:
        st.warning("⚠️ Masukkan keyword pencarian.")
    else:
        with st.status("🔍 Sedang mencari data toko...", expanded=True) as status:
            results = search_shopee_shops(keyword, limit=max_results)
            
            if results:
                df = pd.DataFrame(results)
                status.update(label="✅ Data berhasil diambil!", state="complete")
                
                st.subheader(f"Hasil Pencarian untuk: {keyword}")
                st.dataframe(df, use_container_width=True)

                # Export Excel
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Shopee Business')
                
                st.download_button(
                    label="📥 Download Data Toko (Excel)",
                    data=buffer.getvalue(),
                    file_name=f"shopee_{keyword}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                status.update(label="❌ Gagal mengambil data.", state="error")
                st.error("Tidak ada data ditemukan atau koneksi diblokir oleh Shopee.")

# Footer
st.markdown("---")
st.caption("© BPS Kota Solok - 2026 | Research Tool Only")

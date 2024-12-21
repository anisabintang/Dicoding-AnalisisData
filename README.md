Berikut adalah versi README yang lebih ringkas dan relevan:

---

# Dicoding-AnalisisData

Proyek ini adalah bagian dari submission kursus **Analisis Data** di Dicoding. Dashboard ini dibuat untuk menganalisis data e-commerce dan menjawab pertanyaan bisnis yang diajukan menggunakan **Streamlit**.

## 🎯 **Tujuan**
Menyediakan wawasan dari data e-commerce melalui visualisasi interaktif, untuk membantu pengambilan keputusan bisnis.

## 📊 **Fitur Utama**
1. **Overview Metrics**: 
   - Total pesanan, pendapatan, rata-rata nilai pesanan, dan waktu pengiriman.
2. **Time Series Analysis**: 
   - Tren pesanan harian dan pendapatan.
3. **Customer Demographics**: 
   - Distribusi pelanggan berdasarkan provinsi dan kota.
4. **Product Insights**: 
   - Penjualan dan hubungan antara waktu pengiriman dengan ulasan per kategori.
5. **RFM Analysis**: 
   - Mengidentifikasi pelanggan berdasarkan Recency, Frequency, dan Monetary.
6. **Payment Analysis**:
   - Distribusi metode pembayaran, total transaksi, dan rata-rata ulasan.
7. **Jawaban Pertanyaan Bisnis**:
   - Rata-rata waktu pengiriman per kategori produk.
   - Total transaksi dan ulasan berdasarkan metode pembayaran.

## 🛠️ **Teknologi**
- **Python**: Analisis data.
- **Streamlit**: Dashboard interaktif.
- **Pandas, Matplotlib, Seaborn, Plotly**: Manipulasi data dan visualisasi.

## 🔗 **Akses Dashboard**
Dashboard dapat diakses melalui tautan berikut:  
[**E-commerce Analytics Dashboard**](https://anisabintang-dicoding-submission-andat.streamlit.app/)

## 📂 **Struktur Proyek**
```
Dicoding-AnalisisData/
│
├── dashboard/               # Script dashboard
│   ├── app.py               # Script utama Streamlit
│   ├── requirements.txt     # Dependensi proyek
│
├── data/                    # Dataset
│   ├── cleaned_data.csv     # Dataset yang telah dibersihkan
│
├── notebook.ipynb           # Notebook analisis awal
├── README.md                # Dokumentasi proyek
```

## 📝 **Cara Menjalankan**
1. **Clone Repository**
   ```bash
   git clone https://github.com/anisabintang/Dicoding-AnalisisData.git
   cd Dicoding-AnalisisData/dashboard
   ```

2. **Install Dependensi**
   ```bash
   pip install -r requirements.txt
   ```

3. **Jalankan Dashboard**
   ```bash
   streamlit run app.py
   ```

4. **Akses di Browser**  
   Buka `http://localhost:8501`.

## 📧 **Kontak**
Anisa Bintang Maharani  
[GitHub Profile](https://github.com/anisabintang)


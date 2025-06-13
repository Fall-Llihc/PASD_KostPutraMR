import streamlit as st
import pandas as pd
import datetime
import pickle

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Sistem Prediksi Kesehatan",
    page_icon="🤖",
    layout="wide"
)

# --- MODEL LOADING ---
@st.cache_data
def load_models():
    """
    Loads the pickled models for smoking and drinking prediction.
    This is cached to improve performance.
    """
    try:
        # Menggunakan path relatif. Pastikan file .pkl berada di folder yang sama.
        with open('xgb_best_model_smk.pkl', 'rb') as file:
            smoking_model = pickle.load(file)
        with open('xgb_best_model_drink.pkl', 'rb') as file:
            drinking_model = pickle.load(file)
        return smoking_model, drinking_model
    except FileNotFoundError:
        return None, None

smoking_model, drinking_model = load_models()

# --- SESSION STATE INITIALIZATION ---
def initialize_data():
    """Initializes session state for storing health data."""
    if 'health_data' not in st.session_state:
        st.session_state['health_data'] = []

# --- APP INITIALIZATION ---
initialize_data()

# --- MAIN PAGE ---
st.sidebar.title("Sistem Prediksi Kesehatan")
st.sidebar.info("Aplikasi ini hanya berisi halaman Prediksi Kesehatan.")

# --- PAGE ROUTING ---
if smoking_model is None or drinking_model is None:
    st.error("Gagal memuat file model. Pastikan file `xgb_best_model_smk.pkl` dan `xgb_best_model_drink.pkl` berada di direktori yang sama dengan aplikasi.")
else:
    st.title("🔎 Prediksi Status Merokok & Minum")
    st.markdown("Masukkan data berikut untuk mendapatkan prediksi terpisah untuk status merokok dan minum.")

    with st.form("prediction_form"):
        st.header("Input Data Pengguna")
        col1, col2 = st.columns(2)
        with col1:
            # Disesuaikan dengan Skenario Tes: value=None untuk validasi data tidak lengkap
            age = st.number_input("Usia (Tahun)", min_value=1, max_value=120, value=None, placeholder="Masukkan usia...")
            sex = st.selectbox("Jenis Kelamin", ["Pria", "Wanita"])
            height = st.number_input("Tinggi Badan (cm)", min_value=100, max_value=250, value=None, placeholder="Contoh: 170")
        with col2:
            weight = st.number_input("Berat Badan (kg)", min_value=30, max_value=200, value=None, placeholder="Contoh: 70")
            gamma_gtp = st.number_input("Gamma-GTP (γ-GTP)", min_value=1, max_value=50, value=None, placeholder="Contoh: 25", help="Enzim yang sering dikaitkan dengan fungsi hati.")

        submitted = st.form_submit_button("Dapatkan Prediksi", type="primary")

    if submitted:
        # --- VALIDASI YANG DIPERBARUI ---
        # Memeriksa setiap input dan mengumpulkan nama kolom yang kosong
        empty_fields = []
        if age is None:
            empty_fields.append("Usia (Tahun)")
        if height is None:
            empty_fields.append("Tinggi Badan (cm)")
        if weight is None:
            empty_fields.append("Berat Badan (kg)")
        if gamma_gtp is None:
            empty_fields.append("Gamma-GTP (γ-GTP)")

        # Jika daftar kolom kosong tidak kosong, tampilkan error yang spesifik
        if empty_fields:
            st.error(f"Data tidak lengkap. Harap isi kolom berikut: {', '.join(empty_fields)}", icon="🚨")
        else:
            # Jika semua kolom terisi, lanjutkan proses prediksi
            sex_encoded = 1 if sex == "Pria" else 0
            
            # Menyesuaikan urutan kolom DataFrame agar sama persis dengan yang diharapkan model.
            input_smoking = pd.DataFrame([[sex_encoded, age]], columns=['sex', 'age'])
            input_drinking = pd.DataFrame([[sex_encoded, age, height, gamma_gtp]], columns=['sex', 'age', 'height', 'gamma_GTP'])
            
            # Membuat prediksi
            prediction_smoking = smoking_model.predict(input_smoking)[0]
            prediction_drinking = drinking_model.predict(input_drinking)[0]
            
            # Mengubah hasil prediksi menjadi teks
            smoking_result_text = "Perokok" if prediction_smoking == 1 else "Bukan Perokok"
            drinking_result_text = "Peminum" if prediction_drinking == 1 else "Bukan Peminum"
            
            # Menyimpan catatan prediksi
            new_record = {
                'date': datetime.date.today(),
                'age': age, 'sex': sex, 'height': height, 'weight': weight, 'gamma_GTP': gamma_gtp,
                'smoking_prediction': smoking_result_text,
                'drinking_prediction': drinking_result_text
            }
            st.session_state.health_data.append(new_record)

            st.balloons()
            st.success("Prediksi Berhasil Dibuat!")
            st.subheader("Hasil Prediksi Model")
            
            res_col1, res_col2 = st.columns(2)
            res_col1.metric(label="Status Merokok", value=smoking_result_text)
            res_col2.metric(label="Status Minum", value=drinking_result_text)


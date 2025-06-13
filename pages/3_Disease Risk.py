import streamlit as st
import pandas as pd
import numpy as np

# Cek autentikasi
if not st.session_state.get('authenticated'):
    st.warning('Silahkan login terlebih dahulu.')
    st.stop()
    
# Muat model yang telah dilatih
import pickle
try:
    with open('hypertension_risk_model.pkl', 'rb') as file:
        hypertension_model = pickle.load(file)
    with open('diabetes_risk_model.pkl', 'rb') as file:
        diabetes_model = pickle.load(file)
    with open('high_cholesterol_risk_model.pkl', 'rb') as file:
        high_cholesterol_model = pickle.load(file)
    with open('anemia_risk_model.pkl', 'rb') as file:
        anemia_model = pickle.load(file)
    with open('fatty_liver_risk_model.pkl', 'rb') as file:
        fatty_liver_model = pickle.load(file)
except FileNotFoundError:
    st.error("Error: Satu atau lebih file model (.pkl) tidak ditemukan. Pastikan file-file tersebut berada di direktori yang sama dengan aplikasi.")
    st.stop()

# Definisikan kolom fitur
feature_columns = ['sex', 'age', 'height', 'weight', 'waistline', 'sight_left',
                   'sight_right', 'hear_left', 'hear_right', 'SBP', 'DBP', 'BLDS',
                   'tot_chole', 'HDL_chole', 'LDL_chole', 'triglyceride', 'hemoglobin',
                   'urine_protein', 'serum_creatinine', 'SGOT_AST', 'SGOT_ALT',
                   'gamma_GTP', 'smoking', 'drinking']

st.set_page_config(layout="wide", page_title="Prediktor Risiko Penyakit")

st.title("Prediktor Risiko Penyakit Komprehensif")
st.markdown("Masukkan informasi kesehatan Anda untuk mendapatkan prediksi risiko penyakit yang dipersonalisasi.")

# Inisialisasi session state untuk kolom input jika belum ada
# SEMUA KUNCI HARUS BERAKHIR DENGAN '_input_main' AGAR FUNGSI TOMBOL CLEAR BEKERJA DENGAN ANDAL
if 'sex_input_main' not in st.session_state:
    st.session_state['sex_input_main'] = None
if 'age_input_main' not in st.session_state:
    st.session_state['age_input_main'] = None
if 'height_input_main' not in st.session_state:
    st.session_state['height_input_main'] = None
if 'weight_input_main' not in st.session_state:
    st.session_state['weight_input_main'] = None
if 'waistline_input_main' not in st.session_state:
    st.session_state['waistline_input_main'] = None
if 'sight_left_input_main' not in st.session_state:
    st.session_state['sight_left_input_main'] = None
if 'sight_right_input_main' not in st.session_state:
    st.session_state['sight_right_input_main'] = None
if 'hear_left_input_main' not in st.session_state:
    st.session_state['hear_left_input_main'] = None
if 'hear_right_input_main' not in st.session_state:
    st.session_state['hear_right_input_main'] = None
if 'sbp_input_main' not in st.session_state:
    st.session_state['sbp_input_main'] = None
if 'dbp_input_main' not in st.session_state:
    st.session_state['dbp_input_main'] = None
if 'blds_input_main' not in st.session_state:
    st.session_state['blds_input_main'] = None
if 'tot_chole_input_main' not in st.session_state:
    st.session_state['tot_chole_input_main'] = None
if 'hdl_chole_input_main' not in st.session_state:
    st.session_state['hdl_chole_input_main'] = None
if 'ldl_chole_input_main' not in st.session_state:
    st.session_state['ldl_chole_input_main'] = None
if 'triglyceride_input_main' not in st.session_state:
    st.session_state['triglyceride_input_main'] = None
if 'hemoglobin_input_main' not in st.session_state:
    st.session_state['hemoglobin_input_main'] = None
if 'urine_protein_input_main' not in st.session_state:
    st.session_state['urine_protein_input_main'] = None
if 'serum_creatinine_input_main' not in st.session_state:
    st.session_state['serum_creatinine_input_main'] = None
if 'sgot_ast_input_main' not in st.session_state:
    st.session_state['sgot_ast_input_main'] = None
if 'sgot_alt_input_main' not in st.session_state:
    st.session_state['sgot_alt_input_main'] = None
if 'gamma_gtp_input_main' not in st.session_state:
    st.session_state['gamma_gtp_input_main'] = None
if 'smoking_input_main' not in st.session_state:
    st.session_state['smoking_input_main'] = None
if 'drinking_input_main' not in st.session_state:
    st.session_state['drinking_input_main'] = None

# --- Definisikan fungsi callback untuk mengosongkan input ---
def _clear_inputs():
    """Mengatur semua kunci session state terkait input menjadi None."""
    for key in st.session_state.keys():
        if '_input_main' in key:
            st.session_state[key] = None
    # Tidak ada st.rerun() di sini, st.form_submit_button dengan on_click menangani rerun.

# Form input langsung di halaman utama
with st.form("form_kesehatan"):
    st.header("Input Data Kesehatan Pribadi")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Demografi")
        sex_options = ["Pria", "Wanita"]
        current_sex_index = None
        if st.session_state['sex_input_main'] in sex_options:
            current_sex_index = sex_options.index(st.session_state['sex_input_main'])
        st.radio("Jenis Kelamin", sex_options, index=current_sex_index, key="sex_input_main")

        st.number_input("Usia", min_value=18, max_value=100,
                        value=st.session_state['age_input_main'],
                        placeholder="Contoh: 30", key="age_input_main")
        st.number_input("Tinggi Badan (cm)", min_value=100, max_value=250,
                        value=st.session_state['height_input_main'],
                        placeholder="Contoh: 170", key="height_input_main")
        st.number_input("Berat Badan (kg)", min_value=30, max_value=200,
                        value=st.session_state['weight_input_main'],
                        placeholder="Contoh: 70", key="weight_input_main")
        st.number_input("Lingkar Pinggang (cm)", min_value=50.0, max_value=150.0,
                        value=st.session_state['waistline_input_main'],
                        format="%.1f", placeholder="Contoh: 80.0", key="waistline_input_main")

        st.subheader("Penglihatan & Pendengaran")
        st.number_input("Penglihatan (Kiri)", min_value=0.1, max_value=2.0,
                        value=st.session_state['sight_left_input_main'],
                        format="%.1f", placeholder="Contoh: 1.0", key="sight_left_input_main")
        st.number_input("Penglihatan (Kanan)", min_value=0.1, max_value=2.0,
                        value=st.session_state['sight_right_input_main'],
                        format="%.1f", placeholder="Contoh: 1.0", key="sight_right_input_main")
        st.number_input("Pendengaran (Kiri - 1:Normal, 2:Abnormal)", min_value=1, max_value=2,
                        value=st.session_state['hear_left_input_main'],
                        placeholder="Contoh: 1", key="hear_left_input_main")
        st.number_input("Pendengaran (Kanan - 1:Normal, 2:Abnormal)", min_value=1, max_value=2,
                        value=st.session_state['hear_right_input_main'],
                        placeholder="Contoh: 1", key="hear_right_input_main")

        st.subheader("Tekanan Darah")
        st.number_input("Tekanan Darah Sistolik (SBP)", min_value=70, max_value=200,
                        value=st.session_state['sbp_input_main'],
                        placeholder="Contoh: 120", key="sbp_input_main")
        st.number_input("Tekanan Darah Diastolik (DBP)", min_value=40, max_value=150,
                        value=st.session_state['dbp_input_main'],
                        placeholder="Contoh: 80", key="dbp_input_main")

    with col2:
        st.subheader("Tes Darah & Urin")
        st.number_input("Glukosa Darah Puasa (BLDS)", min_value=50, max_value=300,
                        value=st.session_state['blds_input_main'],
                        placeholder="Contoh: 90", key="blds_input_main")
        st.number_input("Kolesterol Total", min_value=100, max_value=400,
                        value=st.session_state['tot_chole_input_main'],
                        placeholder="Contoh: 180", key="tot_chole_input_main")
        st.number_input("Kolesterol HDL", min_value=20, max_value=100,
                        value=st.session_state['hdl_chole_input_main'],
                        placeholder="Contoh: 50", key="hdl_chole_input_main")
        st.number_input("Kolesterol LDL", min_value=50, max_value=250,
                        value=st.session_state['ldl_chole_input_main'],
                        placeholder="Contoh: 100", key="ldl_chole_input_main")
        st.number_input("Trigliserida", min_value=50, max_value=500,
                        value=st.session_state['triglyceride_input_main'],
                        placeholder="Contoh: 100", key="triglyceride_input_main")
        st.number_input("Hemoglobin", min_value=8.0, max_value=20.0,
                        value=st.session_state['hemoglobin_input_main'],
                        format="%.1f", placeholder="Contoh: 14.0", key="hemoglobin_input_main")
        st.number_input("Protein Urin (1:Normal, 2+:Abnormal)", min_value=1, max_value=4,
                        value=st.session_state['urine_protein_input_main'],
                        placeholder="Contoh: 1", key="urine_protein_input_main")
        st.number_input("Kreatinin Serum", min_value=0.5, max_value=5.0,
                        value=st.session_state['serum_creatinine_input_main'],
                        format="%.1f", placeholder="Contoh: 1.0", key="serum_creatinine_input_main")
        st.number_input("SGOT (AST)", min_value=5, max_value=200,
                        value=st.session_state['sgot_ast_input_main'],
                        placeholder="Contoh: 20", key="sgot_ast_input_main")
        st.number_input("SGOT (ALT)", min_value=5, max_value=200,
                        value=st.session_state['sgot_alt_input_main'],
                        placeholder="Contoh: 20", key="sgot_alt_input_main")
        st.number_input("Gamma GTP", min_value=5, max_value=300,
                        value=st.session_state['gamma_gtp_input_main'],
                        placeholder="Contoh: 30", key="gamma_gtp_input_main")

        st.subheader("Faktor Gaya Hidup")
        smoking_options = ["Tidak Merokok", "Mantan Perokok", "Perokok"]
        current_smoking_index = None
        if st.session_state['smoking_input_main'] in smoking_options:
            current_smoking_index = smoking_options.index(st.session_state['smoking_input_main'])
        st.radio("Status Merokok", smoking_options, index=current_smoking_index, key="smoking_input_main")

        drinking_options = ["Tidak", "Ya"]
        current_drinking_index = None
        if st.session_state['drinking_input_main'] in drinking_options:
            current_drinking_index = drinking_options.index(st.session_state['drinking_input_main'])
        st.radio("Status Minum Alkohol", drinking_options, index=current_drinking_index, key="drinking_input_main")

    # Tambahkan tombol Prediksi dan Bersihkan berdampingan
    col_buttons = st.columns(2)
    with col_buttons[0]:
        predict_button = st.form_submit_button("Prediksi Risiko Penyakit")
    with col_buttons[1]:
        # --- PERUBAHAN PENTING DI SINI ---
        # Teruskan fungsi callback ke on_click, hapus blok 'elif clear_button:' yang lama
        clear_button = st.form_submit_button("Bersihkan Input", on_click=_clear_inputs)

# Logika setelah pengiriman formulir
# Blok ini berjalan SETELAH formulir dikirimkan.
if predict_button:
    # Ambil nilai langsung dari st.session_state karena otomatis diperbarui oleh kunci widget
    sex_input = st.session_state['sex_input_main']
    age_input = st.session_state['age_input_main']
    height_input = st.session_state['height_input_main']
    weight_input = st.session_state['weight_input_main']
    waistline_input = st.session_state['waistline_input_main']
    sight_left_input = st.session_state['sight_left_input_main']
    sight_right_input = st.session_state['sight_right_input_main']
    hear_left_input = st.session_state['hear_left_input_main']
    hear_right_input = st.session_state['hear_right_input_main']
    sbp_input = st.session_state['sbp_input_main']
    dbp_input = st.session_state['dbp_input_main']
    blds_input = st.session_state['blds_input_main']
    tot_chole_input = st.session_state['tot_chole_input_main']
    hdl_chole_input = st.session_state['hdl_chole_input_main']
    ldl_chole_input = st.session_state['ldl_chole_input_main']
    triglyceride_input = st.session_state['triglyceride_input_main']
    hemoglobin_input = st.session_state['hemoglobin_input_main']
    urine_protein_input = st.session_state['urine_protein_input_main']
    serum_creatinine_input = st.session_state['serum_creatinine_input_main']
    sgot_ast_input = st.session_state['sgot_ast_input_main']
    sgot_alt_input = st.session_state['sgot_alt_input_main']
    gamma_gtp_input = st.session_state['gamma_gtp_input_main']
    smoking_input = st.session_state['smoking_input_main']
    drinking_input = st.session_state['drinking_input_main']

    # Validasi bahwa semua input telah diberikan
    required_inputs = [
        sex_input, age_input, height_input, weight_input, waistline_input,
        sight_left_input, sight_right_input, hear_left_input, hear_right_input,
        sbp_input, dbp_input, blds_input, tot_chole_input, hdl_chole_input,
        ldl_chole_input, triglyceride_input, hemoglobin_input, urine_protein_input,
        serum_creatinine_input, sgot_ast_input, sgot_alt_input, gamma_gtp_input,
        smoking_input, drinking_input
    ]

    if None in required_inputs:
        st.warning("Mohon lengkapi semua data kesehatan yang diperlukan sebelum memprediksi.")
    else:
        # Petakan input kategorikal ke nilai numerik seperti yang digunakan dalam pelatihan
        sex_encoded = 0 if sex_input == "Pria" else 1 # Pria: 0, Wanita: 1
        drinking_encoded = 0 if drinking_input == "Tidak" else 1 # Tidak: 0, Ya: 1
        smoking_encoded = 0
        if smoking_input == "Tidak Merokok":
            smoking_encoded = 1
        elif smoking_input == "Mantan Perokok":
            smoking_encoded = 2
        elif smoking_input == "Perokok":
            smoking_encoded = 3

        # Buat DataFrame dari input, pastikan urutan kolom
        input_data = pd.DataFrame([[
            sex_encoded, age_input, height_input, weight_input, waistline_input,
            sight_left_input, sight_right_input, hear_left_input, hear_right_input,
            sbp_input, dbp_input, blds_input, tot_chole_input, hdl_chole_input,
            ldl_chole_input, triglyceride_input, hemoglobin_input, urine_protein_input,
            serum_creatinine_input, sgot_ast_input, sgot_alt_input, gamma_gtp_input,
            smoking_encoded, drinking_encoded
        ]], columns=feature_columns)

        st.subheader("Hasil Prediksi")

        # Prediksi dan tampilkan untuk setiap penyakit
        models = {
            "Risiko Hipertensi": hypertension_model,
            "Risiko Diabetes": diabetes_model,
            "Risiko Kolesterol Tinggi": high_cholesterol_model,
            "Risiko Anemia": anemia_model,
            "Risiko Perlemakan Hati": fatty_liver_model
        }

        for disease_name, model in models.items():
            prediction = model.predict(input_data)[0]
            if prediction == 1:
                st.error(f"🔴 **{disease_name}: RISIKO TINGGI**")
            else:
                st.success(f"🟢 **{disease_name}: RISIKO RENDAH**")

        st.markdown("---")
        st.markdown(
            """
            <p style='font-size: small; color: gray;'>
            Prediksi ini didasarkan pada data kesehatan yang diberikan dan panduan medis umum.
            Untuk diagnosis yang akurat dan saran kesehatan yang dipersonalisasi, mohon konsultasikan dengan profesional kesehatan yang berkualifikasi.
            </p>
            """,
            unsafe_allow_html=True
        )

# --- BLOK elif clear_button LAMA DIHAPUS ---
# Logika pembersihan sekarang ditangani oleh fungsi callback _clear_inputs().

# Memahami Baseline Risiko
with st.expander("Memahami Baseline Risiko"):
    st.markdown("""
    **Risiko Hipertensi (Tekanan Darah Tinggi):**
    Didefinisikan jika Tekanan Darah Sistolik (SBP) >= 140 mmHg atau Tekanan Darah Diastolik (DBP) >= 90 mmHg, sesuai pedoman WHO.

    **Risiko Diabetes:**
    Diidentifikasi jika Glukosa Plasma Puasa (BLDS) >= 126 mg/dL, berdasarkan pedoman WHO dan American Diabetes Association.

    **Risiko Kolesterol Tinggi (Dislipidemia):**
    Ditentukan oleh berbagai tingkat lipid: Kolesterol Total >= 193 mg/dL, ATAU Kolesterol LDL >= 116 mg/dL, ATAU Trigliserida >= 150 mg/dL. Juga, Kolesterol HDL < 40 mg/dL untuk pria atau < 50 mg/dL untuk wanita.

    **Risiko Anemia:**
    Ditunjukkan oleh kadar hemoglobin: < 13 g/dL untuk pria dan < 12 g/dL untuk wanita tidak hamil, sesuai pedoman WHO.

    **Risiko Perlemakan Hati (Risiko NAFLD):**
    Indikator risiko sederhana berdasarkan peningkatan enzim hati (SGOT_AST > 40, SGOT_ALT > 40, atau Gamma GTP > 60) DAN adanya setidaknya dua faktor risiko metabolik, yang meliputi obesitas/kelebihan berat badan (BMI >= 25 atau >= 30), lingkar pinggang tinggi (>= 94 cm untuk pria, >= 80 cm untuk wanita), hipertensi, diabetes, dan kolesterol tinggi.
    """)

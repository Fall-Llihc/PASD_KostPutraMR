import streamlit as st
import pandas as pd
import datetime
import pickle
from user_manager import add_health_data # Import the new function

if not st.session_state.get('authenticated'):
    st.warning('Silahkan login terlebih dahulu.')
    st.stop()

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
            age = st.number_input("Usia (Tahun)", min_value=1, max_value=120, value=None, placeholder="Masukkan usia...")
            sex = st.selectbox("Jenis Kelamin", ["Pria", "Wanita"])
            height = st.number_input("Tinggi Badan (cm)", min_value=100, max_value=250, value=None, placeholder="Contoh: 170")
            sbp = st.number_input("Tekanan Darah Sistolik (SBP)", 70, 250, value=None, placeholder="Contoh: 120")
        with col2:
            weight = st.number_input("Berat Badan (kg)", min_value=30, max_value=200, value=None, placeholder="Contoh: 70")
            gamma_gtp = st.number_input("Gamma-GTP (γ-GTP)", min_value=1, max_value=50, value=None, placeholder="Contoh: 25", help="Enzim yang sering dikaitkan dengan fungsi hati.")
            dbp = st.number_input("Tekanan Darah Diastolik (DBP)", 40, 200, value=None, placeholder="Contoh: 80")
            blds = st.number_input("Gula Darah Puasa (mg/dL)", 50, 500, value=None, placeholder="Contoh: 90")


        submitted = st.form_submit_button("Dapatkan Prediksi", type="primary")

    if submitted:
        empty_fields = []
        if age is None:
            empty_fields.append("Usia (Tahun)")
        if height is None:
            empty_fields.append("Tinggi Badan (cm)")
        if weight is None:
            empty_fields.append("Berat Badan (kg)")
        if gamma_gtp is None:
            empty_fields.append("Gamma-GTP (γ-GTP)")
        if sbp is None:
            empty_fields.append("Tekanan Darah Sistolik (SBP)")
        if dbp is None:
            empty_fields.append("Tekanan Darah Diastolik (DBP)")
        if blds is None:
            empty_fields.append("Gula Darah Puasa (mg/dL)")

        if empty_fields:
            st.error(f"Data tidak lengkap. Harap isi kolom berikut: {', '.join(empty_fields)}", icon="🚨")
        else:
            sex_encoded = 1 if sex == "Pria" else 0

            input_smoking = pd.DataFrame([[sex_encoded, age]], columns=['sex', 'age'])
            input_drinking = pd.DataFrame([[sex_encoded, age, height, gamma_gtp]], columns=['sex', 'age', 'height', 'gamma_GTP'])

            prediction_smoking = smoking_model.predict(input_smoking)[0]
            prediction_drinking = drinking_model.predict(input_drinking)[0]

            smoking_result_text = "Perokok" if prediction_smoking == 1 else "Bukan Perokok"
            drinking_result_text = "Peminum" if prediction_drinking == 1 else "Bukan Peminum"

            # Store the data in the database
            current_user = st.session_state.user
            add_health_data(current_user, age, sex, height, weight, gamma_gtp, prediction_smoking, prediction_drinking, sbp, dbp, blds)

            # Store the data in session state for pre-filling Health Recommendation
            st.session_state.latest_prediction_data = {
                'age': age,
                'sex': sex, # Keep original sex for consistency
                'height': height,
                'weight': weight,
                'gamma_gtp': gamma_gtp,
                'smoking_prediction': prediction_smoking, # Store as 0/1
                'drinking_prediction': prediction_drinking, # Store as 0/1
                'sbp': sbp,
                'dbp': dbp,
                'blds': blds
            }
            st.success("Prediksi Berhasil Dibuat!")
            st.subheader("Hasil Prediksi Model")

            res_col1, res_col2 = st.columns(2)
            res_col1.metric(label="Status Merokok", value=smoking_result_text)
            res_col2.metric(label="Status Minum", value=drinking_result_text)

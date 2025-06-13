import streamlit as st
import pandas as pd
import numpy as np

if not st.session_state.get('authenticated'):
    st.warning('Please login first.')
    st.stop()
    
    
import streamlit as st
import pandas as pd
import numpy as np
import joblib # To load the .pkl models

# Load the pre-trained models
try:
    model_hypertension = joblib.load('model_hypertension.pkl')
    model_liver_disease = joblib.load('model_liver_disease.pkl')
    models_loaded = True
except FileNotFoundError:
    st.error("Error: Model files (.pkl) not found. Please ensure 'model_obesity.pkl', 'model_hypertension.pkl', and 'model_liver_disease.pkl' are in the same directory.")
    models_loaded = False
    
# Define the features that the models expect, in the exact order they were trained with
# This list must match the 'features' list used during model training
MODEL_FEATURES = [
    'sex', 'age', 'height', 'weight', 'waistline', 'sight_left', 'sight_right',
    'hear_left', 'hear_right', 'SBP', 'DBP', 'BLDS', 'tot_chole', 'HDL_chole',
    'LDL_chole', 'triglyceride', 'hemoglobin', 'urine_protein',
    'serum_creatinine', 'SGOT_AST', 'SGOT_ALT', 'gamma_GTP', 'BMI'
]

def predict_disease_risk(data):
    # Calculate BMI
    data['BMI'] = data['weight'] / ((data['height'] / 100) ** 2)
    
    # Prepare the input data as a DataFrame for the models
    # Ensure the order of columns matches MODEL_FEATURES
    input_df = pd.DataFrame([data], columns=MODEL_FEATURES)
    
    predictions = {}
    if models_loaded:

        # Predict Hypertension
        pred_hypertension = model_hypertension.predict(input_df)[0]
        predictions['Hypertension'] = "Tinggi" if pred_hypertension == 1 else "Rendah"

        # Predict Liver Disease
        pred_liver_disease = model_liver_disease.predict(input_df)[0]
        predictions['Liver Disease'] = "Tinggi" if pred_liver_disease == 1 else "Rendah"
    else:
        return {"Error": "Models not loaded. Cannot make predictions."}

    return predictions


st.set_page_config(page_title="Sistem Prediksi dan Pemantauan Kesehatan Pribadi", layout="centered")

st.title("Sistem Prediksi dan Pemantauan Kesehatan Pribadi")
st.header("Prediksi Risiko Penyakit")

st.write("""
    Fitur ini memprediksi risiko Anda terhadap penyakit seperti obesitas, hipertensi, atau gangguan hati 
    berdasarkan indikator medis yang Anda masukkan. Prediksi ini didasarkan pada model Machine Learning
    yang telah dilatih menggunakan dataset kesehatan.
""")

# Input fields for the user
st.subheader("Data Kesehatan Anda")

# Using st.columns for better layout
col1, col2 = st.columns(2)

with col1:
    age = st.number_input("Usia", min_value=1, max_value=120, value=30)
    gender_options = {"Pria": 0, "Wanita": 1} # Male: 0, Female: 1 as per preprocessing
    gender = st.selectbox("Jenis Kelamin", list(gender_options.keys()))
    height = st.number_input("Tinggi Badan (cm)", min_value=50.0, max_value=250.0, value=170.0)
    weight = st.number_input("Berat Badan (kg)", min_value=10.0, max_value=300.0, value=70.0)
    waistline = st.number_input("Lingkar Pinggang (cm)", min_value=30.0, max_value=200.0, value=85.0)
    sight_left = st.number_input("Penglihatan Kiri", min_value=0.1, max_value=2.0, value=1.0, step=0.1)
    sight_right = st.number_input("Penglihatan Kanan", min_value=0.1, max_value=2.0, value=1.0, step=0.1)
    hear_left = st.selectbox("Pendengaran Kiri", options=[1, 2], format_func=lambda x: "Normal" if x == 1 else "Abnormal", index=0) # 1: normal, 2: abnormal
    hear_right = st.selectbox("Pendengaran Kanan", options=[1, 2], format_func=lambda x: "Normal" if x == 1 else "Abnormal", index=0) # 1: normal, 2: abnormal


with col2:
    sbp = st.number_input("Tekanan Darah Sistolik (SBP)", min_value=50, max_value=250, value=120)
    dbp = st.number_input("Tekanan Darah Diastolik (DBP)", min_value=30, max_value=150, value=80)
    blds = st.number_input("Gula Darah (BLDS)", min_value=50, max_value=400, value=90)
    tot_chole = st.number_input("Kolesterol Total", min_value=50, max_value=500, value=180)
    hdl_chole = st.number_input("Kolesterol HDL", min_value=10, max_value=150, value=50)
    ldl_chole = st.number_input("Kolesterol LDL", min_value=30, max_value=400, value=100)
    triglyceride = st.number_input("Trigliserida", min_value=30, max_value=1000, value=100)
    hemoglobin = st.number_input("Hemoglobin", min_value=5.0, max_value=20.0, value=14.0, step=0.1)
    urine_protein = st.selectbox("Protein Urin", options=[1, 2, 3, 4, 5, 6], format_func=lambda x: f"Level {x}", index=0) # Assume 1 is normal
    serum_creatinine = st.number_input("Kreatinin Serum", min_value=0.1, max_value=5.0, value=1.0, step=0.1)
    sgot_ast = st.number_input("SGOT (AST)", min_value=5, max_value=500, value=20)
    sgot_alt = st.number_input("SGPT (ALT)", min_value=5, max_value=500, value=20)
    gamma_gtp = st.number_input("Gamma GTP", min_value=5, max_value=1000, value=30)

if st.button("Prediksi Risiko Penyakit"):
    if models_loaded:
        user_data = {
            'sex': gender_options[gender],
            'age': age,
            'height': height,
            'weight': weight,
            'waistline': waistline,
            'sight_left': sight_left,
            'sight_right': sight_right,
            'hear_left': hear_left,
            'hear_right': hear_right,
            'SBP': sbp,
            'DBP': dbp,
            'BLDS': blds,
            'tot_chole': tot_chole,
            'HDL_chole': hdl_chole,
            'LDL_chole': ldl_chole,
            'triglyceride': triglyceride,
            'hemoglobin': hemoglobin,
            'urine_protein': urine_protein,
            'serum_creatinine': serum_creatinine,
            'SGOT_AST': sgot_ast,
            'SGOT_ALT': sgot_alt,
            'gamma_GTP': gamma_gtp
            # BMI will be calculated inside predict_disease_risk function before passing to model
        }

        st.subheader("Hasil Analisis")
        
        # Calculate and display BMI
        bmi_calculated = user_data['weight'] / ((user_data['height'] / 100) ** 2)
        st.write(f"**Indeks Massa Tubuh (BMI):** {bmi_calculated:.2f}")

        predictions = predict_disease_risk(user_data)
        
        if "Error" in predictions:
            st.error(predictions["Error"])
        else:
            st.markdown("---")
            st.write("### **Risiko Penyakit:**")
            st.write(f"- **Hipertensi:** Risiko {predictions['Hypertension']}")
            st.write(f"- **Gangguan Hati:** Risiko {predictions['Liver Disease']}")
            
            st.markdown("""
                ---
                **Penting:** Hasil prediksi ini adalah alat bantu dan edukasi. Untuk keputusan medis lebih lanjut, 
                Anda sangat disarankan untuk berkonsultasi dengan tenaga kesehatan profesional.
            """)
    else:
        st.warning("Tidak dapat melakukan prediksi karena model belum dimuat.")

st.markdown("---")
st.caption("Dikembangkan oleh Kelompok Kost Putra MR - Sains Data, Fakultas Informatika, Universitas Telkom")
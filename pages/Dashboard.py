import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
if not st.session_state.get('authenticated'):
    st.warning('Please login first.')
    st.stop()
st.set_page_config(layout="wide")
# --- Data Loading and Preprocessing ---
@st.cache_data # Cache the data loading for better performance
def load_data():
    try:
        # Path filenya diganti berdasarkan yang make
        df = pd.read_csv(r'C:\Users\asus\PASD_KostPutraMR\smoking_drinkin_100k.csv')
    except FileNotFoundError:
        st.error("Error: 'smoking_drinkin_100k.csv' not found. Please make sure the file is in the correct directory.")
        # Create a dummy DataFrame for demonstration if file not found
        data = {
            'sex': ['Male', 'Female', 'Male', 'Female', 'Male', 'Female', 'Male', 'Female'],
            'age': [25, 30, 45, 50, 35, 40, 60, 55],
            'height': [170, 160, 175, 165, 180, 155, 172, 168],
            'weight': [70, 60, 80, 65, 85, 55, 78, 62],
            'waistline': [80, 70, 85, 75, 90, 65, 88, 72],
            'sight_left': [1.0, 0.8, 1.2, 0.9, 1.0, 0.7, 1.1, 0.9],
            'sight_right': [1.0, 0.8, 1.2, 0.9, 1.0, 0.7, 1.1, 0.9],
            'hear_left': [1, 1, 1, 1, 1, 1, 1, 1],
            'hear_right': [1, 1, 1, 1, 1, 1, 1, 1],
            'SBP': [120, 110, 130, 125, 135, 115, 140, 128],
            'DBP': [80, 70, 85, 78, 88, 72, 90, 80],
            'BLDS': [90, 85, 110, 95, 100, 88, 120, 92], # Fasting Blood Sugar
            'tot_chole': [180, 190, 220, 200, 195, 185, 230, 198], # Total Cholesterol
            'HDL_chole': [50, 60, 45, 55, 48, 62, 40, 58],
            'LDL_chole': [100, 110, 140, 120, 130, 105, 150, 115],
            'triglyceride': [100, 90, 150, 110, 120, 95, 180, 105],
            'hemoglobin': [14.5, 13.0, 15.0, 13.5, 15.5, 12.8, 16.0, 13.2],
            'urine_protein': [1, 1, 2, 1, 1, 1, 2, 1],
            'serum_creatinine': [0.8, 0.7, 1.0, 0.9, 1.1, 0.75, 1.2, 0.85],
            'SGOT_AST': [20, 25, 35, 30, 40, 22, 45, 28],
            'SGOT_ALT': [22, 28, 40, 32, 45, 25, 50, 30],
            'gamma_GTP': [30, 25, 50, 35, 60, 28, 70, 32],
            'smoking': [0, 1, 0, 1, 1, 0, 0, 1], # Assuming 0/1 for smoking
            'drinking': [1, 0, 1, 0, 1, 0, 0, 1]  # Assuming 0/1 for drinking
        }
        df = pd.DataFrame(data)
        st.warning("Using a dummy DataFrame for demonstration as 'smoking_drinkin_100k.csv' was not found.")
    return df

df = load_data()

# Convert 'smoking' and 'drinking' to more descriptive labels if they are 0/1
if 'smoking' in df.columns and df['smoking'].dtype != 'object':
    df['smoking'] = df['smoking'].map({1: 0, 2:0,3:1})
if 'drinking' in df.columns and df['drinking'].dtype != 'object':
    df['drinking'] = df['drinking'].map({'N': 0, 'Y': 1})

# Calculate BMI using 'height' (cm) and 'weight' (kg)
if 'height' in df.columns and 'weight' in df.columns:
    df['height_m'] = df['height'] / 100 # Convert cm to meters
    df['bmi'] = df['weight'] / (df['height_m'] ** 2)

# Create age groups
if 'age' in df.columns:
    bins = [0, 18, 30, 45, 60, 100]
    labels = ['<18', '18-30', '31-45', '46-60', '>60']
    df['age_group'] = pd.cut(df['age'], bins=bins, labels=labels, right=False)

st.title("Dashboard Kebiasaan Merokok dan Minum")
# --- Streamlit App Layout ---
st.header("Metrik Kesehatan Utama (Pilih dari Dropdown) 🎯")

# Define gauge configurations for different metrics
gauge_configs = {
    'Rata-rata Gula Darah Puasa (BLDS)': {
        'column': 'BLDS',
        'value_type': 'mean',
        'title': 'Rata-rata Gula Darah Puasa (BLDS)',
        'range': [0, 200],
        'steps': [
            {'range': [0, 99], 'color': "lightgreen"},
            {'range': [100, 125], 'color': "gold"},
            {'range': [126, 200], 'color': "salmon"}
        ],
        'unit': ' mg/dL'
    },
    'Rata-rata BMI': {
        'column': 'bmi',
        'value_type': 'mean',
        'title': 'Rata-rata BMI',
        'range': [0, 40],
        'steps': [
            {'range': [0, 18.5], 'color': "salmon"},
            {'range': [18.5, 24.9], 'color': "lightgreen"},
            {'range': [25, 29.9], 'color': "gold"},
            {'range': [30, 40], 'color': "salmon"}
        ],
        'unit': ''
    },
    'Persentase Perokok': {
        'column': 'smoking',
        'value_type': 'percentage_yes',
        'title': 'Persentase Perokok',
        'range': [0, 100],
        'steps': [
            {'range': [0, 20], 'color': "lightgreen"},
            {'range': [20, 40], 'color': "gold"},
            {'range': [40, 100], 'color': "salmon"}
        ],
        'unit': '%'
    },
    'Rata-rata Tekanan Darah Sistolik (SBP)': {
        'column': 'SBP',
        'value_type': 'mean',
        'title': 'Rata-rata Tekanan Darah Sistolik (SBP)',
        'range': [0, 180],
        'steps': [
            {'range': [0, 119], 'color': "lightgreen"},
            {'range': [120, 139], 'color': "gold"},
            {'range': [140, 180], 'color': "salmon"}
        ],
        'unit': ' mmHg'
    },
    'Rata-rata Tekanan Darah Diastolik (DBP)': {
        'column': 'DBP',
        'value_type': 'mean',
        'title': 'Rata-rata Tekanan Darah Diastolik (DBP)',
        'range': [0, 120],
        'steps': [
            {'range': [0, 79], 'color': "lightgreen"},
            {'range': [80, 89], 'color': "gold"},
            {'range': [90, 120], 'color': "salmon"}
        ],
        'unit': ' mmHg'
    },
    'Rata-rata Total Kolesterol (tot_chole)': {
        'column': 'tot_chole',
        'value_type': 'mean',
        'title': 'Rata-rata Total Kolesterol',
        'range': [0, 300],
        'steps': [
            {'range': [0, 199], 'color': "lightgreen"},
            {'range': [200, 239], 'color': "gold"},
            {'range': [240, 300], 'color': "salmon"}
        ],
        'unit': ' mg/dL'
    }
}

# Filter gauge options based on available columns in df
available_gauge_options = {
    k: v for k, v in gauge_configs.items()
    if v['column'] in df.columns or (v['column'] in ['smoking', 'drinking'] and 'Ya' in df[v['column']].unique())
}
if 'bmi' not in df.columns and 'bmi' in [v['column'] for v in gauge_configs.values()]:
    if 'height' in df.columns and 'weight' in df.columns:
        available_gauge_options['Rata-rata BMI'] = gauge_configs['Rata-rata BMI']
    else:
        # Remove BMI if source columns are missing
        if 'Rata-rata BMI' in available_gauge_options:
            del available_gauge_options['Rata-rata BMI']

if available_gauge_options:
    selected_gauge_metric_name = st.selectbox(
        "Pilih Metrik untuk Gauge Meter:",
        options=list(available_gauge_options.keys()),
        index=0 # Default ke opsi pertama yang tersedia
    )

    config = available_gauge_options[selected_gauge_metric_name]
    metric_column = config['column']
    metric_value = None

    if config['value_type'] == 'mean':
        if metric_column in df.columns:
            metric_value = df[metric_column].mean()
    elif config['value_type'] == 'percentage_yes':
        if metric_column in df.columns:
            metric_value = (df[metric_column] == 'Ya').mean() * 100

    if metric_value is not None:
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=metric_value,
            title={'text': config['title']},
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': config['range'], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "darkblue"},
                'steps': config['steps'],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': metric_value
                }
            },
            number={'suffix': config['unit']}
        ))
        fig_gauge.update_layout(height=450) # Ubah nilai tinggi di sini
        st.plotly_chart(fig_gauge, use_container_width=True)
    else:
        st.warning(f"Data untuk '{selected_gauge_metric_name}' tidak tersedia.")
else:
    st.warning("Tidak ada metrik yang tersedia untuk gauge meter.")

# Row 1: Pie Charts
col1, col2 = st.columns(2)

with col1:
    st.header("Distribusi Kebiasaan Merokok")
    if 'smoking' in df.columns:
        smoking_counts = df['smoking'].value_counts().reset_index()
        smoking_counts.columns = ['Smoking Status', 'Count']
        fig_smoking = px.pie(smoking_counts, values='Count', names='Smoking Status', title='Proporsi Perokok')
        st.plotly_chart(fig_smoking, use_container_width=True)
    else:
        st.warning("Kolom 'smoking' tidak ditemukan.")

with col2:
    st.header("Distribusi Kebiasaan Minum")
    if 'drinking' in df.columns:
        drinking_counts = df['drinking'].value_counts().reset_index()
        drinking_counts.columns = ['Drinking Status', 'Count']
        fig_drinking = px.pie(drinking_counts, values='Count', names='Drinking Status', title='Proporsi Peminum')
        st.plotly_chart(fig_drinking, use_container_width=True)
    else:
        st.warning("Kolom 'drinking' tidak ditemukan.")

# Row 2: Gender vs Smoking/Drinking Bar Chart
st.header("Merokok vs Minum berdasarkan Jenis Kelamin")
if 'sex' in df.columns and 'smoking' in df.columns and 'drinking' in df.columns:
    gender_behavior = df.groupby(['sex', 'smoking', 'drinking']).size().reset_index(name='Count')
    fig_gender_behavior = px.bar(gender_behavior, x='sex', y='Count', color='smoking',
                                 pattern_shape='drinking',
                                 title='Merokok dan Minum berdasarkan Jenis Kelamin',
                                 labels={'sex': 'Jenis Kelamin', 'Count': 'Jumlah Orang'},
                                 barmode='group')
    st.plotly_chart(fig_gender_behavior, use_container_width=True)
else:
    st.warning("Kolom 'sex', 'smoking', atau 'drinking' tidak ditemukan.")

# Row 3: Health Metrics Correlation
st.header("Korelasi Kebiasaan dengan Metrik Kesehatan")

# Define available health metrics from your provided list
health_metrics_options = [
    'SBP', 'DBP', 'BLDS', 'tot_chole', 'HDL_chole', 'LDL_chole',
    'triglyceride', 'hemoglobin', 'urine_protein', 'serum_creatinine',
    'SGOT_AST', 'SGOT_ALT', 'gamma_GTP', 'bmi'
]

# Filter options based on columns actually present in df
available_metrics = [col for col in health_metrics_options if col in df.columns]

if available_metrics and 'smoking' in df.columns and 'drinking' in df.columns:
    selected_metric = st.selectbox(
        "Pilih Metrik Kesehatan:",
        options=available_metrics,
        index=available_metrics.index('BLDS') if 'BLDS' in available_metrics else 0 # Default to BLDS or first available
    )

    fig_health_metric = px.box(df, x='smoking', y=selected_metric, color='drinking',
                                 title=f'Distribusi {selected_metric.replace("_", " ").title()} berdasarkan Kebiasaan Merokok dan Minum',
                                 labels={'smoking': 'Merokok', selected_metric: selected_metric.replace('_', ' ').title(), 'drinking': 'Minum'})
    st.plotly_chart(fig_health_metric, use_container_width=True)
else:
    st.warning("Tidak cukup kolom untuk menampilkan korelasi metrik kesehatan atau kolom kebiasaan.")
    
st.header("Perilaku Merokok & Minum berdasarkan Kelompok Usia 📊")

if 'age_group' in df.columns and 'smoking' in df.columns and 'drinking' in df.columns:
    age_behavior = df.groupby(['age_group', 'smoking', 'drinking']).size().reset_index(name='Jumlah')

    fig_age_behavior = px.bar(
        age_behavior,
        x='age_group',
        y='Jumlah',
        color='smoking',
        barmode='stack',
        facet_col='drinking', # Memisahkan grafik berdasarkan status minum
        title="Distribusi Merokok Berdasarkan Usia dan Status Minum",
        labels={'age_group': 'Kelompok Usia', 'smoking': 'Merokok', 'drinking': 'Minum'}
    )
    st.plotly_chart(fig_age_behavior, use_container_width=True)
else:
    st.warning("Kolom 'age_group', 'smoking', atau 'drinking' tidak ditemukan. Tidak dapat menampilkan visualisasi kelompok usia.")
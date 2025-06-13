import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from user_manager import get_all_health_data, delete_all_health_data # Import the function to get all health data
import io

if not st.session_state.get('authenticated'):
    st.warning('Please login first.')
    st.stop()
st.set_page_config(layout="wide")

st.title("Dashboard Kebiasaan Merokok dan Minum")

# --- Data Loading and Preprocessing ---
current_user = st.session_state.user
# get_all_health_data now returns (age, sex, height, weight, gamma_GTP, smoking_prediction, drinking_prediction, SBP, DBP, BLDS, timestamp)
# We need the timestamp for filtering
user_health_data_raw = get_all_health_data(current_user)

if not user_health_data_raw:
    st.info("Tidak ada riwayat data kesehatan untuk ditampilkan. Silakan masukkan data Anda di halaman 'Smoking and Alcohol Prediction' terlebih dahulu.")
else:

    # Now back to Dashboard.py, assuming get_all_health_data returns 11 columns
    df = pd.DataFrame(user_health_data_raw, columns=[
        'age', 'sex', 'height', 'weight', 'gamma_GTP', 'smoking', 'drinking', 'SBP', 'DBP', 'BLDS', 'timestamp'
    ])

    # Convert 'timestamp' to datetime objects
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Date Filtering Sidebar
    st.sidebar.header("Filter Data Berdasarkan Tanggal")
    min_date = df['timestamp'].min().date()
    max_date = df['timestamp'].max().date()

    date_range = st.sidebar.date_input(
        "Pilih Rentang Tanggal:",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        key="date_filter"
    )

    if len(date_range) == 2:
        start_date, end_date = date_range
        # Filter DataFrame based on selected date range
        df_filtered = df[(df['timestamp'].dt.date >= start_date) & (df['timestamp'].dt.date <= end_date)]
    else:
        df_filtered = df.copy() # No filter applied if date range is incomplete

    if df_filtered.empty:
        st.warning("Tidak ada data untuk rentang tanggal yang dipilih. Sesuaikan filter tanggal atau masukkan data baru.")
        st.stop() # Stop further execution if no data after filtering

    # Convert 'smoking' and 'drinking' to more descriptive labels (0/1 to 'Tidak'/'Ya')
    # Assuming 0 is "Bukan Perokok/Peminum" and 1 is "Perokok/Peminum"
    if 'smoking' in df_filtered.columns:
        df_filtered['smoking'] = df_filtered['smoking'].map({0: 'Tidak', 1: 'Ya'})
    if 'drinking' in df_filtered.columns:
        df_filtered['drinking'] = df_filtered['drinking'].map({0: 'Tidak', 1: 'Ya'})


    # Calculate BMI using 'height' (cm) and 'weight' (kg) for filtered data
    if 'height' in df_filtered.columns and 'weight' in df_filtered.columns:
        df_filtered['height_m'] = df_filtered['height'] / 100 # Convert cm to meters
        df_filtered['bmi'] = df_filtered['weight'] / (df_filtered['height_m'] ** 2)

    # Create age groups for filtered data
    if 'age' in df_filtered.columns:
        bins = [0, 18, 30, 45, 60, 100]
        labels = ['<18', '18-30', '31-45', '46-60', '>60']
        df_filtered['age_group'] = pd.cut(df_filtered['age'], bins=bins, labels=labels, right=False)
    
    # --- Add Save as CSV Button ---
    st.sidebar.markdown("---")
    st.sidebar.header("Unduh Data")

    # Convert DataFrame to CSV in-memory
    csv_buffer = io.StringIO()
    df_filtered.to_csv(csv_buffer, index=False)
    csv_data = csv_buffer.getvalue().encode('utf-8') # Get bytes for download

    st.sidebar.download_button(
        label="Unduh Data yang Difilter (.csv)",
        data=csv_data,
        file_name=f"{current_user}_health_data_filtered_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        help="Unduh data kesehatan Anda yang saat ini ditampilkan dalam format CSV."
    )
    # --- End of Save as CSV Button ---

    # --- Remove History Button ---
    st.sidebar.markdown("---")
    st.sidebar.header("Kelola Riwayat")
    st.sidebar.warning("Aksi ini akan menghapus semua riwayat data kesehatan Anda secara permanen. Tidak dapat dibatalkan.")
    if st.sidebar.button("Hapus Semua Riwayat Data"):
        # Confirmation step using session state
        st.session_state.confirm_delete = True

    if st.session_state.get('confirm_delete'):
        st.sidebar.info("Anda yakin ingin menghapus semua riwayat data kesehatan?")
        col_confirm_yes, col_confirm_no = st.sidebar.columns(2)
        if col_confirm_yes.button("Ya, Hapus Sekarang", key="confirm_yes"):
            delete_all_health_data(current_user)
            st.session_state.confirm_delete = False # Reset confirmation
            st.success("Semua riwayat data kesehatan telah dihapus.")
            st.rerun() # Rerun to show empty dashboard
        if col_confirm_no.button("Tidak, Batalkan", key="confirm_no"):
            st.session_state.confirm_delete = False # Reset confirmation
            st.info("Penghapusan riwayat data dibatalkan.")
            st.rerun() # Rerun to remove confirmation message
    # --- End of Remove History Button ---


    # --- Streamlit App Layout (using df_filtered) ---
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

    # Filter gauge options based on available columns in df_filtered
    available_gauge_options = {}
    for k, v in gauge_configs.items():
        if v['column'] in df_filtered.columns:
            if v['value_type'] == 'percentage_yes' and 'Ya' not in df_filtered[v['column']].unique():
                continue
            available_gauge_options[k] = v
        elif v['column'] == 'bmi' and 'bmi' in df_filtered.columns:
            available_gauge_options[k] = v

    if available_gauge_options:
        selected_gauge_metric_name = st.selectbox(
            "Pilih Metrik untuk Gauge Meter:",
            options=list(available_gauge_options.keys()),
            index=0
        )

        config = available_gauge_options[selected_gauge_metric_name]
        metric_column = config['column']
        metric_value = None

        if config['value_type'] == 'mean':
            if metric_column in df_filtered.columns:
                metric_value = df_filtered[metric_column].mean()
        elif config['value_type'] == 'percentage_yes':
            if metric_column in df_filtered.columns:
                metric_value = (df_filtered[metric_column] == 'Ya').mean() * 100

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
            fig_gauge.update_layout(height=450)
            st.plotly_chart(fig_gauge, use_container_width=True)
        else:
            st.warning(f"Data untuk '{selected_gauge_metric_name}' tidak tersedia dalam rentang tanggal yang dipilih.")
    else:
        st.warning("Tidak ada metrik yang tersedia untuk gauge meter dalam rentang tanggal yang dipilih.")

    # Row 1: Pie Charts
    col1, col2 = st.columns(2)

    with col1:
        st.header("Distribusi Kebiasaan Merokok")
        if 'smoking' in df_filtered.columns:
            smoking_counts = df_filtered['smoking'].value_counts().reset_index()
            smoking_counts.columns = ['Smoking Status', 'Count']
            fig_smoking = px.pie(smoking_counts, values='Count', names='Smoking Status', title='Proporsi Perokok')
            st.plotly_chart(fig_smoking, use_container_width=True)
        else:
            st.warning("Kolom 'smoking' tidak ditemukan.")

    with col2:
        st.header("Distribusi Kebiasaan Minum")
        if 'drinking' in df_filtered.columns:
            drinking_counts = df_filtered['drinking'].value_counts().reset_index()
            drinking_counts.columns = ['Drinking Status', 'Count']
            fig_drinking = px.pie(drinking_counts, values='Count', names='Drinking Status', title='Proporsi Peminum')
            st.plotly_chart(fig_drinking, use_container_width=True)
        else:
            st.warning("Kolom 'drinking' tidak ditemukan.")

    # Row 2: Gender vs Smoking/Drinking Bar Chart
    st.header("Merokok vs Minum berdasarkan Jenis Kelamin")
    if 'sex' in df_filtered.columns and 'smoking' in df_filtered.columns and 'drinking' in df_filtered.columns:
        gender_behavior = df_filtered.groupby(['sex', 'smoking', 'drinking']).size().reset_index(name='Count')
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

    health_metrics_options = [
        'SBP', 'DBP', 'BLDS', 'bmi'
    ]

    available_metrics = [col for col in health_metrics_options if col in df_filtered.columns]

    if available_metrics and 'smoking' in df_filtered.columns and 'drinking' in df_filtered.columns:
        selected_metric = st.selectbox(
            "Pilih Metrik Kesehatan:",
            options=available_metrics,
            index=available_metrics.index('BLDS') if 'BLDS' in available_metrics else 0
        )

        fig_health_metric = px.box(df_filtered, x='smoking', y=selected_metric, color='drinking',
                                     title=f'Distribusi {selected_metric.replace("_", " ").title()} berdasarkan Kebiasaan Merokok dan Minum',
                                     labels={'smoking': 'Merokok', selected_metric: selected_metric.replace('_', ' ').title(), 'drinking': 'Minum'})
        st.plotly_chart(fig_health_metric, use_container_width=True)
    else:
        st.warning("Tidak cukup kolom untuk menampilkan korelasi metrik kesehatan atau kolom kebiasaan dalam rentang tanggal yang dipilih.")

    st.header("Perilaku Merokok & Minum berdasarkan Kelompok Usia 📊")

    if 'age_group' in df_filtered.columns and 'smoking' in df_filtered.columns and 'drinking' in df_filtered.columns:
        age_behavior = df_filtered.groupby(['age_group', 'smoking', 'drinking']).size().reset_index(name='Jumlah')

        fig_age_behavior = px.bar(
            age_behavior,
            x='age_group',
            y='Jumlah',
            color='smoking',
            barmode='stack',
            facet_col='drinking',
            title="Distribusi Merokok Berdasarkan Usia dan Status Minum",
            labels={'age_group': 'Kelompok Usia', 'smoking': 'Merokok', 'drinking': 'Minum'}
        )
        st.plotly_chart(fig_age_behavior, use_container_width=True)
    else:
        st.warning("Kolom 'age_group', 'smoking', atau 'drinking' tidak ditemukan dalam rentang tanggal yang dipilih. Tidak dapat menampilkan visualisasi kelompok usia.")
    st.write(df)

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path

from predict import load_pipeline, predict_crops, FEATURE_RANGES

# --------------------------------------------------------------------------- #
# Page Config
# --------------------------------------------------------------------------- #
st.set_page_config(
    page_title="Quantum Crop Recommendation",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------------------------------- #
# Custom CSS for a professional dark/clinical theme
# --------------------------------------------------------------------------- #
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    #MainMenu, footer, header {visibility: hidden;}
    
    /* Global Typography */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background-color: #0b0f15;
        color: #e5e7eb;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #11151c !important;
        border-right: 1px solid #1f2937;
    }
    
    /* Metric Cards styling */
    [data-testid="stMetric"] {
        background-color: #151a22;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #1f2937;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2);
    }
    [data-testid="stMetricValue"] {
        font-size: 2.2rem;
        font-weight: 700;
        color: #10b981;
        margin-top: 0.5rem;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        color: #9ca3af;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #f3f4f6;
    }
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0px;
        color: #ffffff;
        background: -webkit-linear-gradient(45deg, #10b981, #34d399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding-bottom: 5px;
    }
    .sub-header {
        font-size: 1rem;
        color: #9ca3af;
        margin-top: 5px;
        margin-bottom: 40px;
        font-weight: 400;
        max-width: 800px;
    }
    
    /* Run Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
        color: white !important;
        border: 1px solid #064e3b !important;
        border-radius: 8px !important;
        padding: 0.75rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        transition: all 0.2s ease-in-out !important;
        width: 100% !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 15px rgba(16, 185, 129, 0.3) !important;
    }
    
    /* Empty state card */
    .empty-state {
        background-color: #151a22;
        border: 1px dashed #374151;
        border-radius: 12px;
        padding: 3rem;
        text-align: center;
        color: #9ca3af;
        margin-top: 2rem;
    }
    
    /* Number Input Styling */
    div[data-baseweb="input"] {
        background-color: #0b0f15 !important;
        border: 1px solid #374151 !important;
        border-radius: 6px !important;
    }
    div[data-baseweb="input"]:focus-within {
        border-color: #10b981 !important;
        box-shadow: 0 0 0 1px #10b981 !important;
    }
    .stNumberInput label p {
        color: #d1d5db !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------------------------------- #
# Load Pipeline
# --------------------------------------------------------------------------- #
@st.cache_resource
def get_pipeline():
    try:
        return load_pipeline(Path("models"))
    except Exception as e:
        st.error(f"Could not load model: {e}")
        return None

pipeline = get_pipeline()

if not pipeline:
    st.error("System Error: QSVC Model not found. Run training pipeline first.")
    st.stop()

# --------------------------------------------------------------------------- #
# Synced Input Component
# --------------------------------------------------------------------------- #
def synced_input(label, key, min_val, max_val, default_val, step):
    # Initialize session state for this input if not present
    if key not in st.session_state:
        st.session_state[key] = default_val
        st.session_state[key + "_slider"] = default_val
        st.session_state[key + "_num"] = default_val
        
    def update_from_slider():
        st.session_state[key] = st.session_state[key + "_slider"]
        st.session_state[key + "_num"] = st.session_state[key + "_slider"]
        
    def update_from_num():
        st.session_state[key] = st.session_state[key + "_num"]
        st.session_state[key + "_slider"] = st.session_state[key + "_num"]
        
    st.markdown(f"<p style='color:#d1d5db; font-size:0.85rem; font-weight:500; margin-bottom:5px;'>{label}</p>", unsafe_allow_html=True)
    col1, col2 = st.columns([2.5, 1])
    with col1:
        st.slider(
            label, min_value=min_val, max_value=max_val, step=step,
            key=key + "_slider", on_change=update_from_slider, 
            label_visibility="collapsed"
        )
    with col2:
        st.number_input(
            label, min_value=min_val, max_value=max_val, step=step,
            key=key + "_num", on_change=update_from_num, 
            label_visibility="collapsed", format="%.1f"
        )
    return st.session_state[key]

# --------------------------------------------------------------------------- #
# Sidebar Inputs
# --------------------------------------------------------------------------- #
with st.sidebar:
    st.markdown("<div style='padding: 1rem 0; text-align: center;'><h2 style='color:#10b981; margin:0;'>Input Parameters</h2><p style='color:#9ca3af; font-size:0.8rem; margin-top:5px;'>Use sliders or type exact values</p></div>", unsafe_allow_html=True)
    
    st.markdown("<div style='background-color:#151a22; padding:15px; border-radius:10px; margin-bottom:15px; border:1px solid #1f2937;'>", unsafe_allow_html=True)
    st.markdown("<h4 style='color:#e5e7eb; margin-top:0; margin-bottom:15px;'>Soil Nutrients (kg/ha)</h4>", unsafe_allow_html=True)
    n = synced_input("Nitrogen (N)", "N_val", float(FEATURE_RANGES["N"][0]), float(FEATURE_RANGES["N"][1]), 50.0, 1.0)
    p_val = synced_input("Phosphorus (P)", "P_val", float(FEATURE_RANGES["P"][0]), float(FEATURE_RANGES["P"][1]), 50.0, 1.0)
    k = synced_input("Potassium (K)", "K_val", float(FEATURE_RANGES["K"][0]), float(FEATURE_RANGES["K"][1]), 50.0, 1.0)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div style='background-color:#151a22; padding:15px; border-radius:10px; margin-bottom:15px; border:1px solid #1f2937;'>", unsafe_allow_html=True)
    st.markdown("<h4 style='color:#e5e7eb; margin-top:0; margin-bottom:15px;'>Climate & Environment</h4>", unsafe_allow_html=True)
    temp = synced_input("Temperature (°C)", "temp_val", float(FEATURE_RANGES["temperature"][0]), float(FEATURE_RANGES["temperature"][1]), 25.0, 0.5)
    humidity = synced_input("Humidity (%)", "hum_val", float(FEATURE_RANGES["humidity"][0]), float(FEATURE_RANGES["humidity"][1]), 70.0, 1.0)
    rainfall = synced_input("Rainfall (mm)", "rain_val", float(FEATURE_RANGES["rainfall"][0]), float(FEATURE_RANGES["rainfall"][1]), 100.0, 5.0)
    ph = synced_input("Soil pH", "ph_val", float(FEATURE_RANGES["ph"][0]), float(FEATURE_RANGES["ph"][1]), 6.5, 0.1)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    predict_clicked = st.button("Run Quantum Inference", use_container_width=True, type="primary")

# --------------------------------------------------------------------------- #
# Main Dashboard
# --------------------------------------------------------------------------- #
st.markdown('<div class="main-header">Quantum Support Vector Classifier Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Real-time analytical inference for optimal crop recommendations based on high-dimensional quantum feature mapping.</div>', unsafe_allow_html=True)

if predict_clicked:
    input_data = {
        "N": n, "P": p_val, "K": k,
        "temperature": temp, "humidity": humidity,
        "ph": ph, "rainfall": rainfall
    }
    df_input = pd.DataFrame([input_data])
    
    with st.spinner("Executing statevector kernel simulation..."):
        results = predict_crops(pipeline, df_input)
        row = results.iloc[0]
        
        prob1 = float(row['top1_prob']) * 100
        prob2 = float(row['top2_prob']) * 100
        prob3 = float(row['top3_prob']) * 100
        
        crop1 = row['top1'].title()
        crop2 = row['top2'].title()
        crop3 = row['top3'].title()
        
        nq = pipeline['meta']['num_qubits']
        reps = pipeline['config']['hyperparameters']['reps']
        cval = pipeline['config']['hyperparameters']['C']
        
        # Top Metrics Row
        col1, col2, col3 = st.columns(3)
        col1.metric("Primary Recommendation", crop1, f"{prob1:.1f}% Confidence")
        col2.metric("Secondary Alternative", crop2, f"{prob2:.1f}% Confidence")
        col3.metric("Quantum Architecture", f"{nq}-Qubit ZZFeatureMap", f"Reps: {reps}")
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # Charts Row
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            st.markdown("### Model Confidence Distribution")
            df_plot = pd.DataFrame({
                "Crop": [crop1, crop2, crop3],
                "Probability (%)": [prob1, prob2, prob3]
            })
            fig_bar = px.bar(
                df_plot, 
                x="Probability (%)", 
                y="Crop", 
                orientation='h',
                color="Probability (%)",
                color_continuous_scale="emrld",
                range_x=[0, 100]
            )
            fig_bar.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                margin=dict(l=20, r=20, t=30, b=20),
                coloraxis_showscale=False
            )
            fig_bar.update_yaxes(categoryorder="total ascending")
            st.plotly_chart(fig_bar, use_container_width=True)
            
        with chart_col2:
            st.markdown("### Environmental Profile (Normalized)")
            # Normalize inputs to 0-1 range for radar chart
            norm_vals = []
            feats = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
            for f in feats:
                vmin = float(FEATURE_RANGES[f][0])
                vmax = float(FEATURE_RANGES[f][1])
                val = input_data[f]
                norm_vals.append((val - vmin) / (vmax - vmin) if vmax > vmin else 0)
            
            # Close the radar loop
            norm_vals.append(norm_vals[0])
            radar_cats = ["Nitrogen", "Phosphorus", "Potassium", "Temperature", "Humidity", "pH", "Rainfall", "Nitrogen"]
            
            fig_radar = go.Figure(data=go.Scatterpolar(
              r=norm_vals,
              theta=radar_cats,
              fill='toself',
              fillcolor='rgba(16, 185, 129, 0.4)',
              line=dict(color='#10b981')
            ))
            fig_radar.update_layout(
              polar=dict(
                radialaxis=dict(visible=False, range=[0, 1]),
                bgcolor='rgba(0,0,0,0)'
              ),
              paper_bgcolor='rgba(0,0,0,0)',
              font=dict(color='white'),
              margin=dict(l=40, r=40, t=30, b=20),
              showlegend=False
            )
            st.plotly_chart(fig_radar, use_container_width=True)
            
else:
    st.markdown('<div class="empty-state"><h4>Awaiting Data</h4><p>Adjust the parameters in the sidebar and click <b>Run Quantum Inference</b> to begin analysis.</p></div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    # Show an empty state with some metrics placeholder
    col1, col2, col3 = st.columns(3)
    col1.metric("Primary Recommendation", "--", "--")
    col2.metric("Secondary Alternative", "--", "--")
    col3.metric("Quantum Architecture", f"{pipeline['meta']['num_qubits']}-Qubit ZZFeatureMap", f"Reps: {pipeline['config']['hyperparameters']['reps']}")

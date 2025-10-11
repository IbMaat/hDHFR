import streamlit as st
import pandas as pd
import joblib
import numpy as np
import os

# ================= Custom Styling =================
st.markdown("""
    <style>
    body {
        background-color: #f5f7fa;
        font-family: 'Segoe UI', sans-serif;
    }
    .stButton>button {
        background-color: #2ecc71;
        color: white;
        border: none;
        padding: 10px 22px;
        font-size: 16px;
        font-weight: 500;
        border-radius: 6px;
        transition: 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #27ae60;
        transform: scale(1.03);
    }
    .section {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0px 4px 8px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

# ================= Title =================
st.title("hDHFR Bioactivity Prediction App")
st.markdown("""
This application predicts the bioactivity (pIC₅₀) against the **hDHFR enzyme**
of chemical compounds using pre-trained **QSAR models** built from molecular descriptors.
""")

# ================= Prediction Section (Two Columns) =================
st.markdown("<div class='section'>", unsafe_allow_html=True)
st.header("Model-Based Bioactivity Prediction")

col1, col2 = st.columns(2)

with col1:
    selected_model = st.selectbox(
        "Choose a prediction model:",
        [
            "PubChem fingerprints",
            "Substructure fingerprints",
            "MACCS fingerprints",
        ]
    )
    user_smiles = st.text_input("Enter SMILES string:", "CCCCC")
    if st.button("Predict"):
        st.success(f"Prediction simulated for {selected_model} model.")
        st.info("Real prediction will be calculated when descriptors are available.")

with col2:
    st.image("Logo.png" if os.path.exists("Logo.png") else None, width=300)
    st.markdown("#### Model Info")
    st.write("""
    - Random Forest Regression
    - RFE-RFR feature selection
    - High train/test R² values
    """)

st.markdown("</div>", unsafe_allow_html=True)

# ================= What is hDHFR? (Two Columns) =================
st.markdown("<div class='section'>", unsafe_allow_html=True)
st.header("What is hDHFR?")

col1, col2 = st.columns([2, 1])
with col1:
    st.markdown("""
Dihydrofolate reductase (**DHFR**) is crucial for folate metabolism, catalyzing the reduction 
of DHF to THF, which is essential for DNA synthesis.  
DHFR inhibition is a validated mechanism in anticancer and antimicrobial therapy.
""")
with col2:
    st.image("DHFR_image.png" if os.path.exists("DHFR_image.png") else None, width=200)

st.markdown("</div>", unsafe_allow_html=True)

# ================= Dataset & Model Performance (Two Columns) =================
st.markdown("<div class='section'>", unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    st.header("Dataset")
    st.write("""
    - Curated from **ChEMBL** database  
    - Compounds tested against **hDHFR**  
    - SMILES normalization, duplicate removal, standardization
    """)

with col2:
    st.header("Model Performance")
    st.table(pd.DataFrame({
        "Model": ["PubChem", "Substructure", "MACCS"],
        "Train R²": [0.9934, 0.9849, 0.9924],
        "Test R²": [0.9591, 0.9381, 0.9381]
    }))

st.markdown("</div>", unsafe_allow_html=True)

# ================= Developers / Team =================
st.markdown("<div class='section'>", unsafe_allow_html=True)
col1, col2 = st.columns([2, 1])
with col1:
    st.header("Team / Developers")
    st.markdown("""
**Natural Products Team**  
Laboratory of Life and Health Sciences, Faculty of Medicine and Pharmacy  
**University of Abdelmalek Essaadi, Tangier**
""")
with col2:
    st.image("Team_photo.png" if os.path.exists("Team_photo.png") else None, width=200)

st.markdown("</div>", unsafe_allow_html=True)

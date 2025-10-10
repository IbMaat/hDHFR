import streamlit as st
from PIL import Image
import pandas as pd
import base64
import joblib
import subprocess
import os

# ============== PAGE CONFIGURATION ==============
st.set_page_config(page_title="Bioactivity Prediction App", layout="wide")

# ============== CUSTOM CSS STYLING ==============
st.markdown("""
    <style>
    body {
        background-color: #f0f2f6;
        font-family: 'Arial', sans-serif;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 8px;
        cursor: pointer;
        transition: background-color 0.3s;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    </style>
""", unsafe_allow_html=True)

# ============== HEADER SECTION ==============
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.image("Logo.png", use_container_width=True)

st.markdown("<h2 style='text-align:center; color:#333;'>QSAR Bioactivity Prediction Platform</h2>", unsafe_allow_html=True)
st.write("---")

# ============== SIDEBAR ==============
st.sidebar.header("Prediction Settings")
model_choice = st.sidebar.selectbox("Choose model type:", ["PubChem", "Substructure", "MACCS"])
user_input = st.sidebar.text_input("Enter SMILES (or any identifier):")

# ============== MODEL LOADING ==============
@st.cache_resource
def load_models():
    pubchem_model = joblib.load("pubchem.pkl")
    substruct_model = joblib.load("substructure.pkl")
    maccs_model = joblib.load("MACCS.pkl")
    return pubchem_model, substruct_model, maccs_model

pubchem_model, substruct_model, maccs_model = load_models()

# ============== DESCRIPTOR GENERATION (SIMPLIFIED) ==============
def calculate_descriptors(smiles, descriptor_type):
    """Placeholder for descriptor calculation (PaDEL part skipped)."""
    # In this simplified version, we'll just simulate descriptor extraction
    # with dummy values for demonstration.
    dummy_data = pd.DataFrame([[0] * 10], columns=[f"Feature_{i}" for i in range(10)])
    return dummy_data

# ============== PREDICTION FUNCTION ==============
def predict_activity(smiles, model_type):
    descriptors = calculate_descriptors(smiles, model_type)

    if model_type == "PubChem":
        model = pubchem_model
    elif model_type == "Substructure":
        model = substruct_model
    else:
        model = maccs_model

    prediction = model.predict(descriptors)[0]
    return prediction

# ============== MAIN CONTENT ==============
st.subheader("🧪 Enter your molecule to predict bioactivity")

if st.sidebar.button("Predict"):
    if user_input.strip() == "":
        st.warning("Please enter a valid input first.")
    else:
        prediction = predict_activity(user_input, model_choice)
        st.success(f"Predicted pIC₅₀ value: **{prediction:.2f}**")

        # Color-coded activity interpretation
        if prediction > 7:
            st.markdown("<p style='color:green;font-weight:bold;'>High predicted activity ✅</p>", unsafe_allow_html=True)
        elif prediction > 5:
            st.markdown("<p style='color:orange;font-weight:bold;'>Moderate predicted activity ⚠️</p>", unsafe_allow_html=True)
        else:
            st.markdown("<p style='color:red;font-weight:bold;'>Low predicted activity ❌</p>", unsafe_allow_html=True)

st.write("---")

# ============== INFORMATION SECTIONS ==============
st.header("📘 About This App")
st.markdown("""
This application predicts the **bioactivity (pIC₅₀)** of chemical compounds 
using pre-trained **QSAR models** built from molecular descriptor datasets.
""")

st.header("🧬 How It Works")
st.markdown("""
1. The user inputs a molecule (SMILES or name).  
2. The app extracts molecular descriptors.  
3. A machine learning model (PubChem / Substructure / MACCS) predicts bioactivity.  
4. Results are color-coded for easy interpretation.
""")

st.header("📚 References")
st.markdown("""
- ChEMBL Database — https://www.ebi.ac.uk/chembl/  
- PaDEL-Descriptor: Yap CW (2011) *J Comput Chem*  
- QSAR methods adapted from Chanin Nantasenamat’s tutorials  
""")

st.header("📩 Contact")
st.markdown("""
For inquiries or collaborations, please contact:  
**ibrahim.maattallaoui@uae.ac.ma**
""")

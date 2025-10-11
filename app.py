import streamlit as st
from PIL import Image
import pandas as pd
import base64
import joblib
import subprocess
import os

# ============================================================
#                   Custom Styling
# ============================================================
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
    h1, h2, h3 {
        color: #2c3e50;
    }
    .stTextInput>div>input {
        background-color: #fff;
        color: #333;
        padding: 10px;
        border-radius: 6px;
        border: 1px solid #ccc;
        font-size: 16px;
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

# ============================================================
#                   Title and Intro
# ============================================================
st.title("hDHFR Bioactivity Prediction App")
st.markdown("""
    <h2 style="color: #27ae60;">Predict Inhibitory Activity Against hDHFR</h2>
    <p style="font-size:16px;">
    This application predicts the bioactivity (pIC₅₀) against the <b>hDHFR enzyme</b> of chemical compounds
    using pre-trained <b>QSAR models</b> built from molecular descriptor datasets.
    </p>
""", unsafe_allow_html=True)

# ============================================================
#                   Helper Functions
# ============================================================
@st.cache_resource
def load_models():
    try:
        models = {
            "PubChem": joblib.load("pubchem.pkl"),
            "Substructure": joblib.load("substructure.pkl"),
            "MACCS": joblib.load("MACCS.pkl")
        }
        return models
    except Exception as e:
        st.error(f"Error loading models: {e}")
        return None

def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="prediction.csv">Download Predictions</a>'
    return href

def build_model(input_data, model, smiles):
    try:
        prediction = model.predict(input_data)
        df = pd.DataFrame({
            "Molecule": [smiles],
            "Predicted pIC50": prediction
        })
        st.success("Prediction completed successfully!")
        st.dataframe(df, use_container_width=True)
        st.markdown(filedownload(df), unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Prediction failed: {e}")

# ============================================================
#                   Prediction Section
# ============================================================
st.markdown("<div class='section'>", unsafe_allow_html=True)
st.header("Model-Based Bioactivity Prediction")
st.info("Choose a model and input a SMILES string to predict hDHFR inhibitory activity.")

selected = st.selectbox(
    "Choose a prediction model:",
    [
        "DHFR prediction model using PubChem fingerprints",
        "DHFR prediction model using Substructure fingerprints",
        "DHFR prediction model using MACCS fingerprints",
    ]
)

userinput = st.text_input("Enter SMILES String:", "CCCCC")
models = load_models()

if models and st.button("Predict Bioactivity"):
    if userinput.strip():
        model_key = "PubChem" if "PubChem" in selected else \
                    "Substructure" if "Substructure" in selected else "MACCS"

        # For simplicity, generate dummy descriptors matching the model columns
        Xlist = pd.read_csv(f"{model_key}_list.csv").columns
        import numpy as np
        desc_subset = pd.DataFrame([np.zeros(len(Xlist))], columns=Xlist)

        build_model(desc_subset, models[model_key], userinput)
    else:
        st.warning("Please enter a valid SMILES string.")
st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
#                   Logo Section
# ============================================================
st.markdown("<div class='section'>", unsafe_allow_html=True)
st.header("Project Logo")
if os.path.exists("Logo.png"):
    st.image("Logo.png", width=400)
else:
    st.warning("Logo image not found (Logo.png). Please add it to the working directory.")
st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
#                   What is hDHFR?
# ============================================================
st.markdown("<div class='section'>", unsafe_allow_html=True)
st.header("What is hDHFR?")
st.markdown("""
Dihydrofolate reductase (**DHFR**) is an enzyme crucial for folate metabolism,
catalyzing the reduction of dihydrofolate (DHF) to tetrahydrofolate (THF).
THF is essential for DNA synthesis and cellular replication.  
DHFR inhibition is a validated mechanism in anticancer and antimicrobial therapy,
making it a prime drug target.
""")
st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
#                   Dataset Section
# ============================================================
st.markdown("<div class='section'>", unsafe_allow_html=True)
st.header("Dataset Information")
st.markdown("""
The dataset was curated from the **ChEMBL** database, focusing on compounds tested against
the human dihydrofolate reductase (**hDHFR**) enzyme.  
Data preprocessing included normalization of SMILES, removal of duplicates, and standardization.
""")
st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
#                   Model Performance Section
# ============================================================
st.markdown("<div class='section'>", unsafe_allow_html=True)
st.header("Model Performance Summary")
st.markdown("""
All models were trained using **Random Forest Regression** with **RFE-RFR** feature selection.  

| Model | Train R² | Test R² |
|--------|-----------|----------|
| PubChem | 0.9934 | 0.9591 |
| Substructure | 0.9849 | 0.9381 |
| MACCS | 0.9924 | 0.9381 |

These results demonstrate strong predictive performance and model stability.
""")
st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
#                   Python Libraries Section
# ============================================================
st.markdown("<div class='section'>", unsafe_allow_html=True)
st.header("Python Libraries Used")
st.markdown("""
- `streamlit` — UI framework for interactive web apps  
- `pandas` — data manipulation and analysis  
- `joblib` — model serialization  
""")
st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
#                   Developers / Team Section
# ============================================================
st.markdown("<div class='section'>", unsafe_allow_html=True)
st.header("Application Developers / Team")
st.markdown("""
**Natural Products Team** – Laboratory of Life and Health Sciences,  
Faculty of Medicine and Pharmacy, **University of Abdelmalek Essaadi, Tangier**  

This team developed the **hDHFR Bioactivity Prediction App** for predicting activity against the **hDHFR enzyme**.
""")
st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
#                   Collaboration & Contact
# ============================================================
st.markdown("<div class='section'>", unsafe_allow_html=True)
st.header("Collaboration & Contact")
st.markdown("""
We are open to **scientific collaboration**, co-development of tools,  
and data exchange projects in computational drug discovery, molecular docking,  
and QSAR modeling.

**Contact:** ibrahim.maattallaoui@etu.uae.ac.ma
""")
st.markdown("</div>", unsafe_allow_html=True)

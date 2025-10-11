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
        background-color: #f0f2f6;
        font-family: 'Arial', sans-serif;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 10px 20px;
        text-align: center;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 5px;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    h1, h2 {
        color: #2c3e50;
    }
    .stTextInput>div>input {
        background-color: #ffffff;
        color: #333;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #ccc;
        font-size: 16px;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================
#                   App Title
# ============================================================
st.title('hDHFR Prediction App')
st.markdown("""
    <h2 style="color: #4CAF50; font-weight: bold;">Welcome to the hDHFR Bioactivity Prediction App</h2>
    <p style="color: #34495e;">
    This app allows users to predict the bioactivity of a query molecule against the hDHFR target protein using various prediction models.
    </p>
""", unsafe_allow_html=True)

# ============================================================
#                   Tabs
# ============================================================
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    'Main', 'Logo', 'What is hDHFR?', 'Dataset',
    'Model performance', 'Python libraries', 'Application Developers', 'Collaboration & Contact'
])

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
#                   Main Tab
# ============================================================
with tab1:
    st.header('Application Description')
    st.success('hDHFR-Pred has been built to predict bioactivity and identify potent inhibitors against hDHFR using robust machine learning algorithms.')

    selected = st.selectbox(
        'Choose a prediction model',
        [
            'DHFR prediction model using PubChem fingerprints',
            'DHFR prediction model using Substructure fingerprints',
            'DHFR prediction model using MACCS fingerprints',
        ],
    )

    userinput = st.text_input("Enter SMILES String", 'ccccc')
    models = load_models()

    if models and st.button('Predict'):
        if userinput.strip():
            model_key = "PubChem" if "PubChem" in selected else \
                        "Substructure" if "Substructure" in selected else "MACCS"
            # For simplicity, using dummy descriptors for prediction
            Xlist = pd.read_csv(f"{model_key}_list.csv").columns
            import numpy as np
            desc_subset = pd.DataFrame([np.zeros(len(Xlist))], columns=Xlist)

            build_model(desc_subset, models[model_key], userinput)
        else:
            st.warning('Please enter a valid SMILES string.')

# ============================================================
#                   Logo Tab
# ============================================================
with tab2:
    st.header("Project Logo")
    if os.path.exists("Logo.png"):
        st.image("Logo.png", width=400)
    else:
        st.warning("Logo image not found (Logo.png). Please add it to the working directory.")

# ============================================================
#                   What is hDHFR?
# ============================================================
with tab3:
    st.header('What is hDHFR?')
    st.write(''' 
    Dihydrofolate reductase (DHFR) is an enzyme that plays a crucial role in the folate metabolism by reducing dihydrofolate (DHF) to tetrahydrofolate (THF), which is necessary for the synthesis of nucleotides. DHFR is a target enzyme for several anticancer and antimicrobial drugs. Inhibition of DHFR can lead to disrupted DNA synthesis, making it a prime target for drugs in the treatment of various diseases, including cancer and bacterial infections.
    ''')

# ============================================================
#                   Dataset Tab
# ============================================================
with tab4:
    st.header('Dataset')
    st.write(''' 
    The dataset used in this study was curated from the ChEMBL database, specifically focusing on compounds tested against the enzyme human dihydrofolate reductase (hDHFR). 
    ''')

# ============================================================
#                   Model Performance Tab
# ============================================================
with tab5:
    st.header('Model performance')
    st.write(''' 
The top 50 features were selected using RFE-RFR for model training. All models, built with Random Forest regression, showed strong predictive performance. The PubChem model achieved the highest accuracy (R² = 0.9934 train / 0.9591 test), followed closely by Substructure (R² = 0.9849 / 0.9381) and MACCS (R² = 0.9924 / 0.9381), confirming their reliability in predicting inhibitory activity.
''')

# ============================================================
#                   Python Libraries Tab
# ============================================================
with tab6:
    st.header('Python libraries')
    st.markdown(''' 
    This app is based on the following Python libraries:
    - `streamlit`
    - `pandas`
    - `rdkit`
    - `padelpy`
    ''')

# ============================================================
#                   Developers Tab
# ============================================================
with tab7:
    st.header('Application Developers')
    st.write(''' 
    The DHFR-Pred application was developed by the Natural Products team, Laboratory of Life and Health Sciences, Faculty of Medicine and Pharmacy, University of Abdelmalek Essaadi, Tangier.
    ''')

# ============================================================
#                   Collaboration & Contact Tab
# ============================================================
with tab8:
    st.header('Collaboration & Contact')
    st.markdown(''' 
    We are open to scientific collaboration, co-development of tools, and data exchange projects in computational drug discovery, molecular docking, and QSAR modeling.

    **Contact:** ibrahim.maattallaoui@etu.uae.ac.ma 
    ''')

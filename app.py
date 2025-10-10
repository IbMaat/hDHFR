import streamlit as st
from PIL import Image
import pandas as pd
import base64
import joblib
import subprocess
import os
from rdkit import Chem
from rdkit.Chem import Draw
import shutil


st.set_page_config(page_title="hDHFR Bioactivity Predictor", layout="wide")

# Custom CSS
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
        text-decoration: none;
        display: inline-block;
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



@st.cache_resource
def load_models():
    """Load machine learning models (cached)."""
    pubchem = joblib.load('pubchem.pkl')
    substructure = joblib.load('substructure.pkl')
    maccs = joblib.load('MACCS.pkl')
    return pubchem, substructure, maccs


@st.cache_data
def calculate_descriptors(smiles_input, descriptor_type):
    """Run PaDEL descriptor calculation."""
    with open('molecule.smi', 'w') as f:
        f.write(smiles_input)

    descriptor_type_map = {
        "PubChem": "./PaDEL-Descriptor/PubchemFingerprinter.xml",
        "Substructure": "./PaDEL-Descriptor/SubstructureFingerprinter.xml",
        "MACCS": "./PaDEL-Descriptor/MACCSFingerprinter.xml"
    }
    descriptor_file = f"{descriptor_type}_output.csv"

    if not shutil.which("java"):
        st.error("❌ Java not found! Please install Java Runtime Environment.")
        return None

    bashCommand = (
        f"java -Xms2G -Xmx2G -Djava.awt.headless=true -jar ./PaDEL-Descriptor/PaDEL-Descriptor.jar "
        f"-removesalt -standardizenitro -fingerprints "
        f"-descriptortypes {descriptor_type_map[descriptor_type]} "
        f"-dir ./ -file {descriptor_file}"
    )
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

    return descriptor_file if os.path.exists(descriptor_file) else None


def filedownload(df):
    """Download results as CSV."""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="prediction.csv">📥 Download Predictions</a>'



def build_model(input_data, model, userinput):
    """Predict bioactivity (pIC50)."""
    prediction = model.predict(input_data)
    prediction_output = pd.Series(prediction, name='Predicted pIC50')
    molecule_name = pd.Series([userinput], name='Molecule')

    df = pd.concat([molecule_name, prediction_output], axis=1)
    st.subheader("🔮 Prediction Results")
    st.dataframe(df)

    value = prediction_output.values[0]
    if value > 7:
        st.success(f"High predicted activity (pIC50 = {value:.2f})")
    elif value > 5:
        st.warning(f"Moderate predicted activity (pIC50 = {value:.2f})")
    else:
        st.error(f"Low predicted activity (pIC50 = {value:.2f})")

    st.markdown(filedownload(df), unsafe_allow_html=True)



st.sidebar.header("⚙️ Prediction Settings")

model_choice = st.sidebar.selectbox(
    "Choose prediction model",
    [
        'DHFR model (PubChem fingerprints)',
        'DHFR model (Substructure fingerprints)',
        'DHFR model (MACCS fingerprints)',
    ],
)

userinput = st.sidebar.text_input("Enter SMILES", 'CCCCC')

uploaded_file = st.sidebar.file_uploader("Or upload SMILES file (.txt or .csv)", type=["txt", "csv"])

predict_button = st.sidebar.button("🚀 Predict")


st.title("🧬 hDHFR Bioactivity Prediction App")
st.markdown("""
Welcome to the **hDHFR-Pred** application — a machine learning-powered tool 
for predicting molecular bioactivity (pIC50) against **human dihydrofolate reductase (hDHFR)**.  
Upload a molecule or input a SMILES string to start.
""")


pubchem_model, substructure_model, maccs_model = load_models()

if predict_button:
    if uploaded_file is not None:
        try:
            smiles_list = pd.read_csv(uploaded_file, header=None)[0].tolist()
        except Exception:
            st.error("Invalid file format. Upload a single-column file with SMILES strings.")
            smiles_list = []

        results = []
        for smi in smiles_list:
            descriptor_type = "PubChem" if "PubChem" in model_choice else \
                              "Substructure" if "Substructure" in model_choice else "MACCS"
            descriptor_file = calculate_descriptors(smi, descriptor_type)
            if descriptor_file:
                desc = pd.read_csv(descriptor_file)
                Xlist = list(pd.read_csv(f"{descriptor_type}_list.csv").columns)
                desc_subset = desc[Xlist]
                model = pubchem_model if descriptor_type == "PubChem" else \
                        substructure_model if descriptor_type == "Substructure" else maccs_model
                prediction = model.predict(desc_subset)[0]
                results.append((smi, prediction))
        if results:
            df_results = pd.DataFrame(results, columns=["SMILES", "Predicted pIC50"])
            st.subheader("📊 Batch Prediction Results")
            st.dataframe(df_results)
            st.markdown(filedownload(df_results), unsafe_allow_html=True)

    elif userinput:
        mol = Chem.MolFromSmiles(userinput)
        if mol:
            st.image(Draw.MolToImage(mol, size=(300, 300)), caption="Molecular Structure")

            descriptor_type = "PubChem" if "PubChem" in model_choice else \
                              "Substructure" if "Substructure" in model_choice else "MACCS"
            with st.spinner("🧪 Calculating descriptors..."):
                descriptor_file = calculate_descriptors(userinput, descriptor_type)

            if descriptor_file:
                desc = pd.read_csv(descriptor_file)
                Xlist = list(pd.read_csv(f"{descriptor_type}_list.csv").columns)
                desc_subset = desc[Xlist]

                model = pubchem_model if descriptor_type == "PubChem" else \
                        substructure_model if descriptor_type == "Substructure" else maccs_model
                build_model(desc_subset, model, userinput)
            else:
                st.error("Descriptor calculation failed.")
        else:
            st.error("❌ Invalid SMILES input.")
    else:
        st.warning("Please enter a SMILES string or upload a file.")



tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    ["Logo", "What is hDHFR?", "Dataset", "Model Performance", "Python Libraries", "Developers"]
)

with tab1:
    st.markdown("<h3 style='text-align:center;'>🔷 Project Logo</h3>", unsafe_allow_html=True)
    st.markdown("<div style='text-align:center;'><img src='Logo.png' width='300'></div>", unsafe_allow_html=True)

with tab2:
    st.header("What is hDHFR?")
    st.write("""
    **Dihydrofolate reductase (DHFR)** is an enzyme essential for folate metabolism, 
    catalyzing the reduction of dihydrofolate to tetrahydrofolate — a key step in nucleotide biosynthesis.  
    DHFR is a pharmacological target for anticancer, antibacterial, and antiparasitic drugs.
    """)

with tab3:
    st.header("Dataset")
    st.write("""
    The dataset was curated from **ChEMBL**, focusing on compounds tested against the enzyme 
    **human dihydrofolate reductase (hDHFR)**. Molecular fingerprints were generated using PaDEL-Descriptor.
    """)

with tab4:
    st.header("Model Performance")
    st.write("""
    Models were trained using **Random Forest Regression** with feature selection via **RFE-RFR**.  
    - PubChem model: R² = 0.9934 (train) / 0.9591 (test)  
    - Substructure model: R² = 0.9849 / 0.9381  
    - MACCS model: R² = 0.9924 / 0.9381  
    These scores demonstrate strong predictive reliability.
    """)

with tab5:
    st.header("Python Libraries Used")
    st.markdown("""
    - `streamlit` — Web interface  
    - `pandas` — Data handling  
    - `rdkit` — Molecule visualization  
    - `padelpy` / `PaDEL-Descriptor` — Descriptor generation  
    - `joblib` — Model serialization  
    """)

with tab6:
    st.header("Developers")
    st.write("""
    Developed by **Natural Products Team**,  
    Laboratory of Life and Health Sciences,  
    Faculty of Medicine and Pharmacy, University of Abdelmalek Essaadi, Tangier.  
    """)

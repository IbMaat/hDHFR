import streamlit as st
from PIL import Image
import pandas as pd
import base64
import joblib
import subprocess
import os

# -----------------------------
# Custom CSS
# -----------------------------
st.markdown("""
    <style>
    body {background-color: #f0f2f6; font-family: 'Arial', sans-serif;}
    .stButton>button {
        background-color: #4CAF50; color: white; border: none; padding: 10px 20px;
        text-align: center; font-size: 16px; margin: 4px 2px; cursor: pointer; border-radius: 5px;
    }
    .stButton>button:hover {background-color: #45a049;}
    h1 {color: #2c3e50;}
    h2 {color: #34495e;}
    .stTextInput>div>input {
        background-color: #ffffff; color: #333; padding: 10px; border-radius: 5px;
        border: 1px solid #ccc; font-size: 16px;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------
# App Title and Description
# -----------------------------
st.title('hDHFR: Bioactivity Prediction App')
st.markdown("""
    <h2 style="color: #4CAF50; font-weight: bold;">Welcome to the hDHFR Bioactivity Prediction App</h2>
    <p style="color: #34495e;">Predict the bioactivity (pIC50) of small molecules against human DHFR using machine learning models.</p>
""", unsafe_allow_html=True)

# -----------------------------
# Define Tabs
# -----------------------------
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    'Main', 'About', 'What is DHFR?', 'Dataset', 'Model performance', 'Python libraries', 
    'Collaboration & Contact', 'Limitations'
])

# -----------------------------
# Helper Functions
# -----------------------------
def calculate_descriptors(smiles_input, descriptor_type, descriptor_file=None):
    """Calculate descriptors using PaDEL, handling memory limits."""
    with open('molecule.smi', 'w') as f:
        f.write(smiles_input)

    descriptor_type_map = {
        "PubChem": "./PaDEL-Descriptor/PubchemFingerprinter.xml",
        "Substructure": "./PaDEL-Descriptor/SubstructureFingerprinter.xml",
        "MACCS": "./PaDEL-Descriptor/MACCSFingerprinter.xml"
    }

    descriptor_file = descriptor_file or f"{descriptor_type}_output.csv"
    bashCommand = f"java -Xms512M -Xmx1024M -Djava.awt.headless=true -jar ./PaDEL-Descriptor/PaDEL-Descriptor.jar " \
                  f"-removesalt -standardizenitro -fingerprints -descriptortypes {descriptor_type_map[descriptor_type]} " \
                  f"-dir ./ -file {descriptor_file}"

    try:
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        if process.returncode != 0:
            st.error(f"Descriptor calculation failed: {error.decode()}")
            return None
        return descriptor_file
    except Exception as e:
        st.error(f"Error running PaDEL: {e}")
        return None

def filedownload(df):
    """Generate a CSV download link."""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="prediction.csv">Download Predictions</a>'
    return href

def build_model(input_data, model, smiles_input):
    """Predict and display pIC50."""
    prediction = model.predict(input_data)
    st.header('**Prediction Output**')
    prediction_output = pd.Series(prediction, name='pIC50')
    molecule_name = pd.Series([smiles_input], name='molecule_name')
    df = pd.concat([molecule_name, prediction_output], axis=1)
    st.write(df)
    st.markdown(filedownload(df), unsafe_allow_html=True)

# -----------------------------
# Load Models
# -----------------------------
bioactivity_pubchem_model = joblib.load(open('pubchem.pkl', 'rb'))
bioactivity_substructure_model = joblib.load(open('substructure.pkl', 'rb'))
bioactivity_maccs_model = joblib.load(open('MACCS.pkl', 'rb'))

# -----------------------------
# Main Tab
# -----------------------------
with tab1:
    st.title('Application Description')
    st.success('hDHFR predicts bioactivity of molecules against human DHFR using machine learning.')

    selected = st.selectbox(
        'Choose a prediction model',
        [
            'hDHFR prediction model using PubChem fingerprints',
            'hDHFR prediction model using Substructure fingerprints',
            'hDHFR prediction model using MACCS fingerprints'
        ]
    )

    userinput = st.text_input("Enter SMILES String", 'ccccc')

    if st.button('Predict'):
        if not userinput:
            st.warning('Please enter a valid SMILES string.')
        else:
            descriptor_type = ""
            model = None
            csv_list_file = ""
            if selected == 'hDHFR prediction model using PubChem fingerprints':
                descriptor_type = "PubChem"
                model = bioactivity_pubchem_model
                csv_list_file = 'PubChem_list.csv'
            elif selected == 'hDHFR prediction model using Substructure fingerprints':
                descriptor_type = "Substructure"
                model = bioactivity_substructure_model
                csv_list_file = 'Substructure_list.csv'
            elif selected == 'hDHFR prediction model using MACCS fingerprints':
                descriptor_type = "MACCS"
                model = bioactivity_maccs_model
                csv_list_file = 'MACCS_list.csv'

            with st.spinner("Calculating descriptors..."):
                descriptor_file = calculate_descriptors(userinput, descriptor_type)
            if descriptor_file:
                desc = pd.read_csv(descriptor_file)
                st.header('**Calculated Molecular Descriptors**')
                st.write(desc)

                Xlist = list(pd.read_csv(csv_list_file).columns)
                desc_subset = desc[Xlist]
                st.write(desc_subset)

                build_model(desc_subset, model, userinput)

# -----------------------------
# About Tab
# -----------------------------
with tab2:
    coverimage = Image.open('Logo.png')
    st.image(coverimage)

# -----------------------------
# What is DHFR Tab
# -----------------------------
with tab3:
    st.header('What is DHFR?')
    st.write(''' 
    Dihydrofolate reductase (DHFR) is an enzyme involved in folate metabolism by reducing dihydrofolate (DHF) to tetrahydrofolate (THF), essential for nucleotide synthesis. DHFR is a target for anticancer and antimicrobial drugs. Inhibition disrupts DNA synthesis, useful in treating cancer and bacterial infections.
    ''')

# -----------------------------
# Dataset Tab
# -----------------------------
with tab4:
    st.header('Dataset')
    st.write(''' 
    The dataset used in this study was curated from the ChEMBL database, specifically focusing on compounds tested against human dihydrofolate reductase (hDHFR). It contains non-redundant inhibitors with experimentally determined pIC50 values, providing a reliable foundation for machine learning model development.
    ''')

# -----------------------------
# Model Performance Tab
# -----------------------------
with tab5:
    st.header('Model Performance')
    st.write('''
    Top 50 features selected using RFE-RFR. All models built with Random Forest Regression showed strong performance:

    | Model | R² (Train) | R² (Test) |
    |-------|------------|-----------|
    | PubChem fingerprints | 0.9934 | 0.9591 |
    | Substructure fingerprints | 0.9849 | 0.9381 |
    | MACCS fingerprints | 0.9924 | 0.9381 |
    ''')

# -----------------------------
# Python Libraries Tab
# -----------------------------
with tab6:
    st.header('Python Libraries')
    st.markdown(''' 
    - `streamlit`
    - `pandas`
    - `joblib`
    - `Pillow`
    - `rdkit` (optional)
    - Java (required for PaDEL-Descriptor)
    ''')

# -----------------------------
# Collaboration & Contact Tab
# -----------------------------
with tab7:
    st.header('Collaboration & Contact')
    st.write('''
    We are open to scientific collaboration, co-development of tools, and data exchange projects in computational drug discovery, molecular docking, and QSAR modeling.

    **Contact:** ibrahim.maattallaoui@etu.uae.ac.ma
    ''')

# -----------------------------
# Limitations Tab
# -----------------------------
with tab8:
    st.header('Limitations')
    st.write('''
    - Models only applicable to small molecules.
    - Not tested for macrocycles, peptides, or prodrugs.
    - Molecules outside typical chemical space may produce unreliable predictions.
    - Predictions should be experimentally validated.
    ''')

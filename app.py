import streamlit as st
from PIL import Image
import pandas as pd
import base64
import joblib
import subprocess
import os

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
    h1 {
        color: #2c3e50;
    }
    h2 {
        color: #34495e;
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

# Title and Description
st.title('hDHFR Prediction App')
st.markdown("""
    <h2 style="color: #4CAF50; font-weight: bold;">Welcome to the hDHFR Bioactivity Prediction App</h2>
    <p style="color: #34495e;">This app allows users to predict the bioactivity of a query molecule against the hDHFR target protein using various prediction models.</p>
""", unsafe_allow_html=True)

# Tabs (removed "Citing us", renamed "About" → "Logo")
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    'Main', 'Logo', 'What is hDHFR?', 'Dataset',
    'Model performance', 'Python libraries', 'Application Developers'
])

# Main tab
with tab1:
    st.title('Application Description')
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

    # Load models
    bioactivity_first_model = joblib.load(open('pubchem.pkl', 'rb'))
    bioactivity_second_model = joblib.load(open('substructure.pkl', 'rb'))
    bioactivity_third_model = joblib.load(open('MACCS.pkl', 'rb'))

    def calculate_descriptors(smiles_input, descriptor_type, descriptor_file=None):
        with open('molecule.smi', 'w') as f:
            f.write(smiles_input)

        descriptor_type_map = {
            "PubChem": "./PaDEL-Descriptor/PubchemFingerprinter.xml",
            "Substructure": "./PaDEL-Descriptor/SubstructureFingerprinter.xml",
            "MACCS": "./PaDEL-Descriptor/MACCSFingerprinter.xml"
        }
        descriptor_file = descriptor_file or f"{descriptor_type}_output.csv"
        bashCommand = f"java -Xms2G -Xmx2G -Djava.awt.headless=true -jar ./PaDEL-Descriptor/PaDEL-Descriptor.jar " \
                      f"-removesalt -standardizenitro -fingerprints -descriptortypes {descriptor_type_map[descriptor_type]} " \
                      f"-dir ./ -file {descriptor_file}"

        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        return descriptor_file

    def filedownload(df):
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="prediction.csv">Download Predictions</a>'
        return href

    def build_model(input_data, model, descriptor_type):
        prediction = model.predict(input_data)
        st.header('**Prediction output**')
        prediction_output = pd.Series(prediction, name='pIC50')
        molecule_name = pd.Series([userinput], name='molecule_name')
        df = pd.concat([molecule_name, prediction_output], axis=1)
        st.write(df)
        st.markdown(filedownload(df), unsafe_allow_html=True)

    # Model choices
    if selected == 'DHFR prediction model using PubChem fingerprints':
        st.title('Predict bioactivity of molecules against hDHFR using PubChem fingerprints')
        if st.button('Predict'):
            if userinput:
                with st.spinner("Calculating descriptors..."):
                    descriptor_file = calculate_descriptors(userinput, "PubChem")
                desc = pd.read_csv(descriptor_file)
                st.header('**Calculated molecular descriptors**')
                st.write(desc)
                Xlist = list(pd.read_csv('PubChem_list.csv').columns)
                desc_subset = desc[Xlist]
                build_model(desc_subset, bioactivity_first_model, "PubChem")
            else:
                st.warning('Please enter a valid SMILES string.')

    elif selected == 'DHFR prediction model using Substructure fingerprints':
        st.title('Predict bioactivity of molecules against hDHFR using Substructure fingerprints')
        if st.button('Predict'):
            if userinput:
                with st.spinner("Calculating descriptors..."):
                    descriptor_file = calculate_descriptors(userinput, "Substructure")
                desc = pd.read_csv(descriptor_file)
                st.header('**Calculated molecular descriptors**')
                st.write(desc)
                Xlist = list(pd.read_csv('Substructure_list.csv').columns)
                desc_subset = desc[Xlist]
                build_model(desc_subset, bioactivity_second_model, "Substructure")
            else:
                st.warning('Please enter a valid SMILES string.')

    elif selected == 'DHFR prediction model using MACCS fingerprints':
        st.title('Predict bioactivity of molecules against hDHFR using MACCS fingerprints')
        if st.button('Predict'):
            if userinput:
                with st.spinner("Calculating descriptors..."):
                    descriptor_file = calculate_descriptors(userinput, "MACCS")
                desc = pd.read_csv(descriptor_file)
                st.header('**Calculated molecular descriptors**')
                st.write(desc)
                Xlist = list(pd.read_csv('MACCS_list.csv').columns)
                desc_subset = desc[Xlist]
                build_model(desc_subset, bioactivity_third_model, "MACCS")
            else:
                st.warning('Please enter a valid SMILES string.')

# Logo tab (formerly About)
with tab2:
    st.header('Logo')
    coverimage = Image.open('Logo.png')
    st.image(coverimage)

# What is hDHFR?
with tab3:
    st.header('What is hDHFR?')
    st.write('''
    Dihydrofolate reductase (DHFR) is an enzyme that plays a crucial role in folate metabolism by reducing dihydrofolate (DHF) to tetrahydrofolate (THF),
    essential for nucleotide synthesis. DHFR is a target enzyme for several anticancer and antimicrobial drugs. Inhibition of DHFR can lead to disrupted DNA synthesis,
    making it a prime target in treating diseases such as cancer and bacterial infections.
    ''')

# Dataset
with tab4:
    st.header('Dataset')
    st.write('''
    The dataset was curated from the ChEMBL database, focusing on compounds tested against human dihydrofolate reductase (hDHFR).
    ''')

# Model performance
with tab5:
    st.header('Model performance')
    st.write('''
    Models were trained using Random Forest regression with RFE-RFR feature selection.  
    - **PubChem:** R² = 0.9934 (train) / 0.9591 (test)  
    - **Substructure:** R² = 0.9849 / 0.9381  
    - **MACCS:** R² = 0.9924 / 0.9381  
    These results confirm the reliability of the models for predicting inhibitory activity.
    ''')

# Python libraries
with tab6:
    st.header('Python libraries')
    st.markdown('''
    This app is based on:
    - `streamlit`
    - `pandas`
    - `rdkit`
    - `padelpy`
    ''')

# Application developers
with tab7:
    st.header('Application Developers')
    st.write('''
    The **hDHFR-Pred** application was developed by the *Natural Products Team*,  
    Laboratory of Life and Health Sciences, Faculty of Medicine and Pharmacy,  
    **University of Abdelmalek Essaadi, Tangier.**
    ''')

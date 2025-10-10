import streamlit as st
from PIL import Image
import pandas as pd
import base64
import joblib
import subprocess
import os

# ============================================================
#                   🎨 Custom Styling
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
    .main {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0px 4px 8px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)


# ============================================================
#                   🧬 Title and Intro
# ============================================================
st.title("🧠 hDHFR Bioactivity Prediction App")
st.markdown("""
    <h2 style="color: #27ae60;">Predict Inhibitory Activity Against hDHFR</h2>
    <p style="font-size:16px;">This web app predicts the bioactivity (pIC₅₀) of small molecules against the
    human dihydrofolate reductase (hDHFR) enzyme using machine learning models trained on molecular fingerprints.</p>
""", unsafe_allow_html=True)


# ============================================================
#                   📑 Tab Layout
# ============================================================
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "Main", "Logo", "What is hDHFR?", "Dataset",
    "Model Performance", "Python Libraries", "Application Developers", "🤝 Collaboration & Contact"
])


# ============================================================
#                   ⚙️ Helper Functions
# ============================================================
@st.cache_resource
def load_models():
    """Load ML models once to optimize performance."""
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


def calculate_descriptors(smiles_input, descriptor_type):
    """Generate molecular descriptors using PaDEL-Descriptor."""
    with open("molecule.smi", "w") as f:
        f.write(smiles_input)

    descriptor_map = {
        "PubChem": "./PaDEL-Descriptor/PubchemFingerprinter.xml",
        "Substructure": "./PaDEL-Descriptor/SubstructureFingerprinter.xml",
        "MACCS": "./PaDEL-Descriptor/MACCSFingerprinter.xml"
    }

    output_file = f"{descriptor_type}_output.csv"
    bash_cmd = [
        "java", "-Xms2G", "-Xmx2G", "-Djava.awt.headless=true", "-jar", "./PaDEL-Descriptor/PaDEL-Descriptor.jar",
        "-removesalt", "-standardizenitro", "-fingerprints",
        "-descriptortypes", descriptor_map[descriptor_type],
        "-dir", "./", "-file", output_file
    ]

    with st.spinner("🔍 Calculating molecular descriptors..."):
        process = subprocess.Popen(bash_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

    if process.returncode != 0:
        st.error("Descriptor calculation failed.")
        st.text(stderr.decode())
        return None
    return output_file


def filedownload(df):
    """Generate download link for predictions."""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="prediction.csv">📥 Download Predictions</a>'
    return href


def build_model(input_data, model, smiles):
    """Run predictions and display results."""
    try:
        prediction = model.predict(input_data)
        df = pd.DataFrame({
            "Molecule": [smiles],
            "Predicted pIC50": prediction
        })
        st.success("✅ Prediction completed successfully!")
        st.dataframe(df, use_container_width=True)
        st.markdown(filedownload(df), unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Prediction failed: {e}")


# ============================================================
#                   🧪 Main Tab (Prediction)
# ============================================================
with tab1:
    st.markdown("<div class='main'>", unsafe_allow_html=True)
    st.header("🧩 Model-Based Bioactivity Prediction")
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

    if models and st.button("🚀 Predict Bioactivity"):
        if userinput.strip():
            model_key = "PubChem" if "PubChem" in selected else \
                        "Substructure" if "Substructure" in selected else "MACCS"

            descriptor_file = calculate_descriptors(userinput, model_key)
            if descriptor_file and os.path.exists(descriptor_file):
                desc = pd.read_csv(descriptor_file)
                st.subheader("📊 Calculated Molecular Descriptors")
                st.dataframe(desc.head(), use_container_width=True)

                try:
                    Xlist = pd.read_csv(f"{model_key}_list.csv").columns
                    desc_subset = desc[Xlist]
                    build_model(desc_subset, models[model_key], userinput)
                except Exception as e:
                    st.error(f"Descriptor subset or model error: {e}")
        else:
            st.warning("Please enter a valid SMILES string.")
    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
#                   🖼️ Logo Tab
# ============================================================
with tab2:
    st.header("🧬 Project Logo")
    if os.path.exists("Logo.png"):
        st.image("Logo.png", use_container_width=False, width=400)
    else:
        st.warning("Logo image not found (Logo.png). Please add it to the working directory.")


# ============================================================
#                   📖 What is hDHFR?
# ============================================================
with tab3:
    st.header("🧠 What is hDHFR?")
    st.markdown("""
    Dihydrofolate reductase (**DHFR**) is an enzyme crucial for folate metabolism,
    catalyzing the reduction of dihydrofolate (DHF) to tetrahydrofolate (THF).
    THF is essential for DNA synthesis and cellular replication.  
    DHFR inhibition is a validated mechanism in anticancer and antimicrobial therapy,
    making it a prime drug target.
    """)


# ============================================================
#                   📊 Dataset
# ============================================================
with tab4:
    st.header("📚 Dataset Information")
    st.write("""
    The dataset was curated from the **ChEMBL** database, focusing on compounds tested against
    the human dihydrofolate reductase (**hDHFR**) enzyme.  
    Data preprocessing included normalization of SMILES, removal of duplicates, and standardization.
    """)


# ============================================================
#                   📈 Model Performance
# ============================================================
with tab5:
    st.header("⚙️ Model Performance Summary")
    st.markdown("""
    All models were trained using **Random Forest Regression** with **RFE-RFR** feature selection.  
    | Model | Train R² | Test R² |
    |--------|-----------|----------|
    | PubChem | 0.9934 | 0.9591 |
    | Substructure | 0.9849 | 0.9381 |
    | MACCS | 0.9924 | 0.9381 |

    These results demonstrate strong predictive performance and model stability.
    """)


# ============================================================
#                   🐍 Python Libraries
# ============================================================
with tab6:
    st.header("📦 Python Libraries Used")
    st.markdown("""
    - `streamlit` — UI framework for interactive web apps  
    - `pandas` — data manipulation and analysis  
    - `joblib` — model serialization  
    - `padelpy` — descriptor generation  
    - `rdkit` — cheminformatics utilities
    """)


# ============================================================
#                   👩‍🔬 Developers
# ============================================================
with tab7:
    st.header("👩‍🔬 Application Developers")
    st.markdown("""
    The **hDHFR-Pred** application was developed by the **Natural Products Team**,  
    Laboratory of Life and Health Sciences, Faculty of Medicine and Pharmacy,  
    **University of Abdelmalek Essaadi, Tangier.**
    """)


# ============================================================
#                   🤝 Collaboration & Contact
# ============================================================
with tab8:
    st.header("🤝 Collaboration & Contact")
    st.markdown("""
    We are open to **scientific collaboration**, co-development of tools,  
    and data exchange projects in computational drug discovery, molecular docking,  
    and QSAR modeling.
    
    📬 **Contact:** ibrahim.maattallaoui@etu.uae.ac.ma 
    💡 Let's work together to accelerate drug discovery!
    """)

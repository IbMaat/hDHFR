# hDHFR: Bioactivity Prediction App

hDHFR is a web-based application designed to predict the inhibitory bioactivity (pIC50) of small molecules against human dihydrofolate reductase (hDHFR) using robust machine learning models.

---

## Features

- Predict bioactivity using three different molecular signatures:
  - PubChem fingerprints
  - Substructure fingerprints
  - MACCS fingerprints
- Download prediction results in CSV format
- View calculated molecular descriptors
- Explore dataset information and model performance metrics
- Learn about DHFR and its biological significance
- Understand the limitations and applicability domain of the models
- Access collaboration and contact information


## Limitations

- Models are **applicable only to small, drug-like molecules**.
- Not tested for **macrocycles, peptides, or prodrugs**.
- Molecules with rare or unusual scaffolds may fall **outside the domain of applicability**.
- Predictions are computational and should be **experimentally validated** before drawing conclusions.

---

## Requirements

- Python 3.8 or higher
- Streamlit
- pandas
- joblib
- PIL (Pillow)
- rdkit (optional, only for descriptor calculation if using PaDEL)
- Java (required for PaDEL-Descriptor if generating descriptors)

---

## Installation & Running

1. Clone the repository:

```bash
git clone https://github.com/IbMaat/hDHFR-Bioactivity-Prediction-App.git
cd hDHFR-Bioactivity-Prediction-App


Install dependencies:

pip install -r requirements.txt


Run the app:

streamlit run app.py


Open the app in your browser at http://localhost:8501.

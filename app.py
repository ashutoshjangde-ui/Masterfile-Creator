import streamlit as st
import pandas as pd
import json
from io import BytesIO

st.title("📦 Masterfile Automation Tool")

# File uploaders
onboarding_file = st.file_uploader("Upload Onboarding Sheet (onboarding_real.xlsx)", type="xlsx")
masterfile_file = st.file_uploader("Upload Masterfile Template (masterfile_real.xlsx)", type="xlsx")
mapping_file = st.file_uploader("Upload Mapping File (mapping_real.json)", type="json")

if onboarding_file and masterfile_file and mapping_file:
    # Read files
    onboarding = pd.read_excel(onboarding_file)
    masterfile_template = pd.read_excel(masterfile_file)

    mapping = json.load(mapping_file)

    # Create empty DataFrame with masterfile columns
    filled_masterfile = pd.DataFrame(columns=masterfile_template.columns)

    # Map columns
    for master_col, onboard_col in mapping.items():
        if onboard_col in onboarding.columns:
            filled_masterfile[master_col] = onboarding[onboard_col]
        else:
            filled_masterfile[master_col] = ""  # leave blank if missing

    st.success("✅ Masterfile generated successfully!")

    # Save to Excel in memory for download
    output = BytesIO()
    filled_masterfile.to_excel(output, index=False, engine="openpyxl")
    st.download_button(
        label="⬇️ Download Final Masterfile",
        data=output.getvalue(),
        file_name="final_masterfile_real.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

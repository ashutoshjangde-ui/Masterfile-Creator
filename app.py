import os
import json
from io import BytesIO

import pandas as pd
import streamlit as st

# ---------- App Config ----------
st.set_page_config(page_title="📦 Masterfile Automation Tool", layout="centered")
st.title("📦 Masterfile Automation Tool")

DEFAULT_ONB = "onboarding_real1.xlsx"
DEFAULT_TPL = "masterfile_real1.xlsx"
DEFAULT_MAP = "mapping_real.json"

with st.sidebar:
    st.header("Mode")
    mode = st.radio("Choose input mode:", ["Use local files", "Upload files"], index=0)
    st.caption("Local files must be in the same folder as this app.py")

# ---------- Helpers ----------
def load_local_files():
    """Load local onboarding, masterfile template, and mapping if present."""
    missing = []
    if not os.path.exists(DEFAULT_ONB):
        missing.append(DEFAULT_ONB)
    if not os.path.exists(DEFAULT_TPL):
        missing.append(DEFAULT_TPL)
    if not os.path.exists(DEFAULT_MAP):
        missing.append(DEFAULT_MAP)
    if missing:
        return None, None, None, missing

    onboarding = pd.read_excel(DEFAULT_ONB, dtype=str)
    masterfile_template = pd.read_excel(DEFAULT_TPL, dtype=str)
    with open(DEFAULT_MAP, "r", encoding="utf-8") as f:
        mapping = json.load(f)
    return onboarding, masterfile_template, mapping, []

def load_uploaded(onboarding_file, masterfile_file, mapping_file):
    """Read uploaded files."""
    if not (onboarding_file and masterfile_file and mapping_file):
        return None, None, None, ["Upload all three files."]
    try:
        onboarding = pd.read_excel(onboarding_file, dtype=str)
        masterfile_template = pd.read_excel(masterfile_file, dtype=str)
        mapping = json.loads(mapping_file.read().decode("utf-8"))
        return onboarding, masterfile_template, mapping, []
    except Exception as e:
        return None, None, None, [f"Failed to read uploads: {e}"]

def build_masterfile(onboarding: pd.DataFrame, masterfile_template: pd.DataFrame, mapping: dict) -> pd.DataFrame:
    """Map columns from onboarding -> masterfile template using mapping dict."""
    onboarding = onboarding.fillna("")
    # Create empty DF with masterfile columns in the same order
    filled = pd.DataFrame(columns=masterfile_template.columns)
    for master_col in masterfile_template.columns:
        onboard_col = mapping.get(master_col, "")
        if onboard_col and onboard_col in onboarding.columns:
            filled[master_col] = onboarding[onboard_col]
        else:
            filled[master_col] = ""  # blank if missing
    return filled

# ---------- UI for Upload Mode ----------
if mode == "Upload files":
    onboarding_file = st.file_uploader("Upload Onboarding Sheet (onboarding_real1.xlsx)", type=["xlsx"])
    masterfile_file = st.file_uploader("Upload Masterfile Template (masterfile_real1.xlsx)", type=["xlsx"])
    mapping_file = st.file_uploader("Upload Mapping File (mapping_real.json)", type=["json"])
    run = st.button("⚙️ Generate Masterfile")
    if run:
        onboarding, masterfile_template, mapping, errs = load_uploaded(onboarding_file, masterfile_file, mapping_file)
        if errs:
            for e in errs:
                st.error(e)
        else:
            filled = build_masterfile(onboarding, masterfile_template, mapping)
            st.success("✅ Masterfile generated successfully!")
            out = BytesIO()
            filled.to_excel(out, index=False, engine="openpyxl")
            st.download_button(
                label="⬇️ Download final_masterfile_real.xlsx",
                data=out.getvalue(),
                file_name="final_masterfile_real.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# ---------- UI for Local Files Mode ----------
else:
    st.write(f"Looking for files in this folder:")
    st.code(f"- {DEFAULT_ONB}\n- {DEFAULT_TPL}\n- {DEFAULT_MAP}")
    if st.button("⚙️ Generate Masterfile from local files"):
        onboarding, masterfile_template, mapping, missing = load_local_files()
        if missing:
            st.error("These files were not found:")
            st.code("\n".join(missing))
            st.info("Either place them in the same folder as app.py, or switch to 'Upload files' mode in the sidebar.")
        else:
            try:
                filled = build_masterfile(onboarding, masterfile_template, mapping)
                st.success("✅ Masterfile generated successfully from local files!")
                out = BytesIO()
                filled.to_excel(out, index=False, engine="openpyxl")
                st.download_button(
                    label="⬇️ Download final_masterfile_real.xlsx",
                    data=out.getvalue(),
                    file_name="final_masterfile_real.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            except Exception as e:
                st.error(f"Something went wrong: {e}")

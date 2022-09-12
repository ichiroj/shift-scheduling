from io import StringIO
import numpy as np
import sys
import streamlit as st
from typing import Optional

st.set_page_config(layout="wide")

st.markdown(
    "<h1 style='text-align: center;'>3D Bin Packing Demo</h1>",
    unsafe_allow_html=True
)

run_type = st.sidebar.radio(label="Choose run type:",
                            options=["Random", "File upload"])

solver_type = st.sidebar.radio(label="Choose solver to run problems on:",
                               options=["Constrained Quadratic Model",
                                        "CBC (Python-MIP)",
                                        ])

if solver_type == "Constrained Quadratic Model":
    use_cqm_solver = True
else:
    use_cqm_solver = False

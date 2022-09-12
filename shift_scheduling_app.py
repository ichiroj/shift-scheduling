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

    
import pandas as pd
list1=[[1,2,3], [4,5,6], [7,8,9]]
index1 = ["Row1", "Row2", "Row3"]
columns1 =["Col1", "Col2", "Col3"]
df =pd.DataFrame(data=list1, index=index1, columns=columns1)

def rain_condition(v):
    if v < 1.75:
        return "Dry"
    elif v < 2.75:
        return "Rain"
    return "Heavy Rain"

def make_pretty(styler):
    styler.set_caption("Weather Conditions")
    styler.format(rain_condition)
    #styler.format_index(lambda v: v.strftime("%A"))
    styler.background_gradient(axis=None, vmin=1, vmax=9, cmap="Pastel1")
    return styler

st.dataframe(df.style.pipe(make_pretty))

from io import StringIO
import numpy as np
import sys
import streamlit as st
from typing import Optional

from shift_scheduling import (Variables, build_cqm, call_solver, make_df)



def solve_shift_scheduling(opts: dict):
    vars = Variables(opts)
    cqm = build_cqm(opts, vars)
    best_feasible = call_solver(cqm, opts)
    df = make_df(best_feasible, opts, vars)
    st.dataframe(df)
    
st.set_page_config(layout="wide")
st.markdown(
    "<h1 style='text-align: center;'>Shift Scheduling Demo</h1>",
    unsafe_allow_html=True
)

solver_type = st.sidebar.radio(label="Choose solver to run problems on:",
                               options=["Constrained Quadratic Model",
                                        "CBC (Python-MIP)",
                                        ])
if solver_type == "Constrained Quadratic Model":
    use_cqm_solver = True
else:
    use_cqm_solver = False

run_type = st.sidebar.radio(label="Choose run type:",
                            options=["Random", "File upload"])

"""
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
"""

run_button = st.sidebar.button("Run")

workers_range = st.sidebar.slider("人数", min_value=5, max_value=26, value=20)
days_range = st.sidebar.slider("日数", min_value=28, max_value=31, value=30)
fst_dow = st.sidebar.selectbox("曜日", ['月','火','水','木','金','土','日'])

#col1, col2 = st.columns([1, 2])
#with col1:
#    pass
    #st.dataframe(df.style.pipe(make_pretty))
#with col2:
if run_button:

    options = {
        'use_cqm_solver': False,
        'time_limit': 120,
        'num_workers': 20,
        'num_days': 29,
        'fst_dow': 5,
    }

    options['num_workers'] = workers_range
    options['num_days'] = days_range
    options['fst_dow'] = int(fst_dow)

    solve_shift_scheduling(options)



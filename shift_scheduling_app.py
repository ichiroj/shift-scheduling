from io import StringIO
import numpy as np
import sys
import streamlit as st
from typing import Optional

from shift_scheduling import (Variables, build_cqm, call_solver, make_df, dow_chr, wd_chr)

def solve_shift_scheduling(opts: dict):
    vars = Variables(opts)
    cqm = build_cqm(opts, vars)
    best_feasible = call_solver(cqm, opts)
    df = make_df(best_feasible, opts, vars)
    df = df.style.applymap(lambda v: 'background-color: red;' if v == wd_chr[0] else None)
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

run_button = st.sidebar.button("Run")

workers_range = st.sidebar.slider("人数", min_value=5, max_value=26, value=20)
days_range = st.sidebar.slider("日数", min_value=28, max_value=31, value=30)
fst_dow = st.sidebar.selectbox("曜日", dow_chr)

if run_button:

    options = {
        'time_limit': 120,
    }

    options['use_cqm_solver'] = use_cqm_solver

    options['num_workers'] = workers_range
    options['num_days'] = days_range
    options['fst_dow'] = int(fst_dow)

    solve_shift_scheduling(options)

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

    st.dataframe(data=(df.style.applymap(lambda v: 'background-color: #fdd8d8;' if v == wd_chr[0] else 'background-color: #d9d0f4;')
                               .set_table_styles([{'selector':'*', 'props':'text-align: center;'}])))
    
st.set_page_config(layout="wide")
st.markdown(
    "<h1 style='text-align: center;'>Shift Scheduling Demo</h1>",
    unsafe_allow_html=True
)

solver_type = st.sidebar.radio(label="量子コンピュータを：",
                               options=["使う (LeapHybridCQMSampler)",
                                        "使わない (Python-MIP)"],
                               index=1)
if solver_type == "使う (LeapHybridCQMSampler)":
    use_cqm_solver = True
else:
    use_cqm_solver = False

time_limit = st.sidebar.number_input(label="時間制限（秒）", value=20)

workers_range = st.sidebar.slider("人数：", min_value=5, max_value=26, value=20)
days_range = st.sidebar.slider("日数：", min_value=28, max_value=31, value=30)
fst_dow_chr = st.sidebar.selectbox("開始曜日：", dow_chr)

chk_consecutive = st.sidebar.checkbox("？日連続勤務をしたら１日休みを割り当てる", value=True)
if chk_consecutive:
    consecutive_days = st.sidebar.slider("連続勤務日数：", min_value=3, max_value=6, value=5)
else:
    consecutive_days = 0

run_button = st.sidebar.button("Run")

if run_button:

    options = {
        'time_limit': 120,
    }

    options['use_cqm_solver'] = use_cqm_solver
    options['time_limit'] = time_limit

    options['num_workers'] = workers_range
    options['num_days'] = days_range
    options['fst_dow'] = dow_chr.index(fst_dow_chr)

    options['chk_consecutive'] = chk_consecutive
    options['consecutive_days'] = consecutive_days

    solve_shift_scheduling(options)

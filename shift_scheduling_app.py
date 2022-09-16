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
    "<h1 style='text-align: center;'>シフトスケジュール　デモ</h1>",
    unsafe_allow_html=True
)

with st.expander("【 条件の種類 】"):
    st.markdown(
        """
        1. ３～６日連続勤務で１日休み（全員／個別）
        2. 
        """
    )

with st.sidebar.expander("【 量子コンピュータ設定 】"):
    solver_type = st.radio(label="量子コンピュータを：",
                                options=["使う (LeapHybridCQMSampler)",
                                            "使わない (Python-MIP)"],
                                index=1)
    if solver_type == "使う (LeapHybridCQMSampler)":
        use_cqm_solver = True
    else:
        use_cqm_solver = False

    time_limit = st.number_input(label="時間制限（秒）：", value=20)

with st.sidebar.expander("【 基本設定 】"):
    workers_range = st.slider("人数：", min_value=5, max_value=26, value=20)
    workers_list = [chr(ord('A') + w) for w in range(workers_range)]
    days_range = st.slider("日数：", min_value=28, max_value=31, value=30)
    fst_dow_chr = st.selectbox("開始曜日：", dow_chr)

with st.sidebar.expander("【 ３～６日連続勤務で１日休み 】"):
    cond01_all_chk = st.checkbox("全員")
    cond01_all_days = st.slider("連続勤務日数（全員）：", min_value=3, max_value=6, value=5)
    st.markdown("<hr/>", unsafe_allow_html=True)
    cond01_sel_chk = st.checkbox("個別")
    cond01_sel_days = st.slider("連続勤務日数（個別）：", min_value=3, max_value=6, value=5)
    cond01_sel_wrks = st.multiselect("対象者選択：",  workers_list)



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

    options['cond01_all_chk'] = cond01_all_chk
    options['cond01_all_days'] = cond01_all_days
    options['cond01_sel_chk'] = cond01_sel_chk
    options['cond01_sel_days'] = cond01_sel_days
    options['cond01_sel_wrks'] = cond01_sel_wrks

    solve_shift_scheduling(options)

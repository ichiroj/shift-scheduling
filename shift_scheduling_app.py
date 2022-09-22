from io import StringIO
import numpy as np
import sys
import streamlit as st
from typing import Optional

from shift_scheduling import (Variables, build_cqm, call_solver, make_df, dow_chr, wd_chr, options)

def solve_shift_scheduling(opts: dict):
    vars = Variables(opts)
    cqm = build_cqm(opts, vars)
    best_feasible = call_solver(cqm, opts)
    df = make_df(best_feasible, opts, vars)

    st.dataframe(data=(df.style.applymap(lambda v: 'background-color: #fdd8d8;' if v == wd_chr[0] else 'background-color: #d9d0f4;')
                               .set_table_styles([{'selector':'*', 'props':'text-align: center;'}])))
    
st.set_page_config(layout="wide")
st.markdown(
    "<h1 style='text-align: center;'>シフトスケジュール　テスト</h1>",
    unsafe_allow_html=True
)

with st.expander("【 条件の種類 】"):
    st.markdown(
        """
        #### 休日
        1. ３～６日連続勤務で１日休み（全員／個別）
        2. 土日連休を月１～４回以上割当（全員／個別）
        3. 土日を休みにする（全員／個別）
        4. 休みを月４～１０回割り当てる（全員／個別）
        5. 休→出→休の飛び石連休はなし
        6. 休みを週に１～６回以上割当（全員／個別）
        #### 出勤
        7. １日の出勤人数はＸ人以上（平日／土日）
        8. 月の出勤日数は４～２４日以上（全員／個別）
        9. 週の出勤日数は１～６日以上（全員／個別）
        #### 組合せ
        10. 一緒に勤務させる
        11. 一緒に勤務させない
        #### 日・曜日指定
        12. 特定の日を休みにする（個別）
        13. 特定の曜日を休みにする（個別）
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
    obj_sign = st.radio(label="できるだけ多くする：",
                                options=["出勤を", "休みを"])

with st.sidebar.expander("【 ３～６日連続勤務で１日休み 】"):
    cond01_all_chk = st.checkbox("全員", key="cond01_all_chk")
    cond01_all_days = st.slider("連続勤務日数（全員）：", min_value=3, max_value=6, value=5, key="cond01_all_days")
    st.markdown("<hr/>", unsafe_allow_html=True)
    cond01_sel_chk = st.checkbox("個別", key="cond01_sel_chk")
    cond01_sel_days = st.slider("連続勤務日数（個別）：", min_value=3, max_value=6, value=5, key="cond01_sel_days")
    cond01_sel_wrks = st.multiselect("対象者選択：",  workers_list, key="cond01_sel_wrks")

with st.sidebar.expander("【 土日連休を月１～４回以上割当 】"):
    cond02_all_chk = st.checkbox("全員", key="cond02_all_chk")
    cond02_all_cnt = st.slider("回数（全員）：", min_value=1, max_value=4, value=1, key="cond02_all_cnt")
    st.markdown("<hr/>", unsafe_allow_html=True)
    cond02_sel_chk = st.checkbox("個別", key="cond02_sel_chk")
    cond02_sel_cnt = st.slider("回数（個別）：", min_value=1, max_value=4, value=1, key="cond02_sel_cnt")
    cond02_sel_wrks = st.multiselect("対象者選択：",  workers_list, key="cond02_sel_wrks")

with st.sidebar.expander("【 土日を休みにする 】"):
    cond03_all_chk = st.checkbox("全員", key="cond03_all_chk")
    cond03_sel_chk = st.checkbox("個別", key="cond03_sel_chk")
    cond03_sel_wrks = st.multiselect("対象者選択：",  workers_list, key="cond03_sel_wrks")

with st.sidebar.expander("【 休みを月４～１０回割り当てる 】"):
    cond04_all_chk = st.checkbox("全員", key="cond04_all_chk")
    cond04_all_cnt = st.slider("回数（全員）：", min_value=4, max_value=10, value=8, key="cond04_all_cnt")
    st.markdown("<hr/>", unsafe_allow_html=True)
    cond04_sel_chk = st.checkbox("個別", key="cond04_sel_chk")
    cond04_sel_cnt = st.slider("回数（個別）：", min_value=4, max_value=10, value=8, key="cond04_sel_cnt")
    cond04_sel_wrks = st.multiselect("対象者選択：",  workers_list, key="cond04_sel_wrks")

with st.sidebar.expander("【 休→出→休の飛び石連休はなし 】"):
    cond05_chk = st.checkbox("飛び石連休はなし", key="cond05_chk")

with st.sidebar.expander("【 休みを週に１～６回以上割当 】"):
    cond06_all_chk = st.checkbox("全員", key="cond06_all_chk")
    cond06_all_days = st.slider("日数（全員）：", min_value=1, max_value=6, value=2, key="cond06_all_days")
    st.markdown("<hr/>", unsafe_allow_html=True)
    cond06_sel_chk = st.checkbox("個別", key="cond06_sel_chk")
    cond06_sel_days = st.slider("日数（個別）：", min_value=1, max_value=6, value=2, key="cond06_sel_days")
    cond06_sel_wrks = st.multiselect("対象者選択：",  workers_list, key="cond06_sel_wrks")

with st.sidebar.expander("【 １日の出勤人数はＸ人以上 】"):
    cond07_wrk_chk = st.checkbox("平日", key="cond07_wrk_chk")
    cond07_wrk_cnt = st.slider("人数（平日）：", min_value=1, max_value=workers_range, value=workers_range-4, key="cond07_wrk_cnt")
    st.markdown("<hr/>", unsafe_allow_html=True)
    cond07_hol_chk = st.checkbox("土日", key="cond07_hol_chk")
    cond07_hol_cnt = st.slider("人数（土日）：", min_value=1, max_value=workers_range, value=workers_range-4, key="cond07_hol_cnt")

with st.sidebar.expander("【 月の出勤日数は４～２４日以上 】"):
    cond08_all_chk = st.checkbox("全員", key="cond08_all_chk")
    cond08_all_days = st.slider("出勤日数（全員）：", min_value=4, max_value=24, value=20, key="cond08_all_days")
    st.markdown("<hr/>", unsafe_allow_html=True)
    cond08_sel_chk = st.checkbox("個別", key="cond08_sel_chk")
    cond08_sel_days = st.slider("出勤日数（個別）：", min_value=4, max_value=24, value=20, key="cond08_sel_days")
    cond08_sel_wrks = st.multiselect("対象者選択：",  workers_list, key="cond08_sel_wrks")

with st.sidebar.expander("【 週の出勤日数は１～６日以上 】"):
    cond09_all_chk = st.checkbox("全員", key="cond09_all_chk")
    cond09_all_days = st.slider("出勤日数（全員）：", min_value=1, max_value=6, value=5, key="cond09_all_days")
    st.markdown("<hr/>", unsafe_allow_html=True)
    cond09_sel_chk = st.checkbox("個別", key="cond09_sel_chk")
    cond09_sel_days = st.slider("出勤日数（個別）：", min_value=1, max_value=6, value=5, key="cond09_sel_days")
    cond09_sel_wrks = st.multiselect("対象者選択：",  workers_list, key="cond09_sel_wrks")

with st.sidebar.expander("【 一緒に勤務させる 】"):
    cond10_chk = st.checkbox("一緒に勤務させる", key="cond10_chk")
    cond10_wrks_A = st.multiselect("一緒に勤務するグループA：",  workers_list, key="cond10_wrks_A")
    cond10_wrks_B = st.multiselect("一緒に勤務するグループB：",  workers_list, key="cond10_wrks_B")
    cond10_wrks_C = st.multiselect("一緒に勤務するグループC：",  workers_list, key="cond10_wrks_C")

with st.sidebar.expander("【 一緒に勤務させない 】"):
    cond11_chk = st.checkbox("一緒に勤務させない", key="cond11_chk")
    cond11_wrks_A = st.multiselect("一緒に勤務させないグループA：",  workers_list, key="cond11_wrks_A")
    cond11_wrks_B = st.multiselect("一緒に勤務させないグループB：",  workers_list, key="cond11_wrks_B")
    cond11_wrks_C = st.multiselect("一緒に勤務させないグループC：",  workers_list, key="cond11_wrks_C")

with st.sidebar.expander("【 特定の日を休みにする 】"):
    cond12_chk = st.checkbox("特定の日を休みにする", key="cond12_chk")
    cond12_days = st.multiselect("日選択：", [d+1 for d in range(days_range)], key="cond12_days")
    cond12_wrks = st.multiselect("対象者選択：",  workers_list, key="cond12_wrks")

with st.sidebar.expander("【 特定の曜日を休みにする 】"):
    cond13_chk = st.checkbox("特定の曜日を休みにする", key="cond13_chk")
    cond13_dows = st.multiselect("曜日選択：", dow_chr, key="cond13_dows")
    cond13_wrks = st.multiselect("対象者選択：",  workers_list, key="cond13_wrks")

run_button = st.sidebar.button("Run")

if run_button:

    options['use_cqm_solver'] = use_cqm_solver
    options['time_limit'] = time_limit

    options['num_workers'] = workers_range
    options['num_days'] = days_range
    options['fst_dow'] = dow_chr.index(fst_dow_chr)
    if obj_sign == '出勤を':
        options['obj_sign'] = -1
    else:
        options['obj_sign'] = +1

    g_dict = globals()
    for k in options.keys():
        if 'cond' in k:
            options[k] = g_dict[k]

    solve_shift_scheduling(options)

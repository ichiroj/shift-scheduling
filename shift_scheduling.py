from dwave.system import LeapHybridCQMSampler
from dimod import quicksum, ConstrainedQuadraticModel, Binary, SampleSet

import numpy as np
import pandas as pd
import itertools

from mip_solver import MIPCQMSolver

wrk_chr = [chr(ord('A')+w) for w in range(26)]
dow_chr = ['月','火','水','木','金','土','日']
wd_chr = ['－', '〇']

options = {
    'use_cqm_solver': False,
    'time_limit': 20,
    'num_workers': 20,
    'num_days': 30,
    'fst_dow': 0,
    'obj_sign': -1,

    # 1. ３～６日連続勤務で１日休み（全員／個別）
    'cond01_all_chk': False,
    'cond01_all_days': 5,
    'cond01_sel_chk': False,
    'cond01_sel_days': 5,
    'cond01_sel_wrks': [],

    # 2. 土日連休を月１～４回以上割当（全員／個別）
    'cond02_all_chk': False,
    'cond02_all_cnt': 1,
    'cond02_sel_chk': False,
    'cond02_sel_cnt': 1,
    'cond02_sel_wrks': [],

    # 3. 土日を休みにする（全員／個別）
    'cond03_all_chk': False,
    'cond03_sel_chk': False,
    'cond03_sel_wrks': [],

    # 4. 休みを月４～１０回割り当てる（全員／個別）
    'cond04_all_chk': False,
    'cond04_all_cnt': 8,
    'cond04_sel_chk': False,
    'cond04_sel_cnt': 8,
    'cond04_sel_wrks': [],

    # 5. 休→出→休の飛び石連休はなし
    'cond05_chk': False,

    # 6. 休みを週に１～６回以上割当（全員／個別）
    'cond06_all_chk': False,
    'cond06_all_days': 2,
    'cond06_sel_chk': False,
    'cond06_sel_days': 2,
    'cond06_sel_wrks': [],

    # 7. １日の出勤人数はＸ人以上（平日／土日）
    'cond07_wrk_chk': False,
    'cond07_wrk_cnt': 16,
    'cond07_hol_chk': False,
    'cond07_hol_cnt': 16,

    # 8. 月の出勤日数を４～２４日以上（全員／個別）
    'cond08_all_chk': False,
    'cond08_all_days': 20,
    'cond08_sel_chk': False,
    'cond08_sel_days': 20,
    'cond08_sel_wrks': [],

    # 9. 週の出勤日数は１～６日以上（全員／個別）
    'cond09_all_chk': False,
    'cond09_all_days': 5,
    'cond09_sel_chk': False,
    'cond09_sel_days': 5,
    'cond09_sel_wrks': [],

    # 10. 一緒に勤務させる
    'cond10_chk': False,
    'cond10_wrks_A': [],
    'cond10_wrks_B': [],
    'cond10_wrks_C': [],

    # 11. 一緒に勤務させない
    'cond11_chk': False,
    'cond11_wrks_A': [],
    'cond11_wrks_B': [],
    'cond11_wrks_C': [],

    # 12. 一緒に勤務させない
    'cond12_chk': False,
    'cond12_days': [],
    'cond12_wrks': [],

    # 13. 一緒に勤務させない
    'cond13_chk': False,
    'cond13_dows': [],
    'cond13_wrks': [],
}

class Variables:
    def __init__(self, opts: dict):
        num_workers = opts['num_workers']
        num_days = opts['num_days']

        self.wd = {(w, d): Binary(f'worker_{w}_day_{d}') for w in range(num_workers) for d in range(num_days)}
        if opts['cond02_all_chk'] or opts['cond02_sel_chk']:
            self.wwe = {(w, we): Binary(f'worker_{w}_weekend_{we}') for w in range(num_workers) for we in range(4)}
        #if opts['cond11_chk']:
        #    self.dww = {(d, w1, w2): Binary(f'day_{d}_worker1_{w1}_weekend2_{w2}')
        #        for d in range(num_days) for w1 in range(num_workers) for w2 in range(num_workers)}

def add_constraints(cqm: ConstrainedQuadraticModel, opts: dict, vars: Variables):
    num_workers = opts['num_workers']
    num_days = opts['num_days']
    fst_dow = opts['fst_dow']

    # 1. ３～６日連続勤務で１日休み
    for w in range(num_workers):
        if opts['cond01_sel_chk'] and chr(ord('A')+w) in opts['cond01_sel_wrks']:
            days = opts['cond01_sel_days']
        elif opts['cond01_all_chk']:
            days = opts['cond01_all_days']
        else:
            continue

        for d in range(num_days - days):
            cqm.add_constraint(quicksum(vars.wd[w,d + i] for i in range(days + 1)) <= days)

    # 2. 土日連休を月１～４回以上割り当てる
    fst_sat = (12 - fst_dow) % 7
    for w in range(num_workers):
        if opts['cond02_sel_chk'] and chr(ord('A')+w) in opts['cond02_sel_wrks']:
            we_cnt = opts['cond02_sel_cnt']
        elif opts['cond02_all_chk']:
            we_cnt = opts['cond02_all_cnt']
        else:
            continue

        for we in range(4):
            cqm.add_constraint(2 * vars.wwe[w, we]  - (1 - vars.wd[w, we * 7 + fst_sat]) - (1 - vars.wd[w, we * 7 + fst_sat + 1]) <= 0)
            cqm.add_constraint((1 - vars.wwe[w, we]) - vars.wd[w, we * 7 + fst_sat] - vars.wd[w, we * 7 + fst_sat + 1] <= 0)
        cqm.add_constraint(quicksum(vars.wwe[w, we] for we in range(4)) >= we_cnt)

    # 3. 土日を休みにする
    for w in range(num_workers):
        for d in range(num_days):
            if (fst_dow + d) % 7 >= 5:
                if opts['cond03_sel_chk'] and chr(ord('A')+w) in opts['cond03_sel_wrks']:
                    cqm.add_constraint(vars.wd[w,d] == 0)
                elif opts['cond03_all_chk']:
                    cqm.add_constraint(vars.wd[w,d] == 0)

    # 4. 休みを月４～１０回割り当てる
    for w in range(num_workers):
        if opts['cond04_sel_chk'] and chr(ord('A')+w) in opts['cond04_sel_wrks']:
            cqm.add_constraint(quicksum(vars.wd[w,d] for d in range(num_days)) <= num_days - opts['cond04_sel_cnt'])
        elif opts['cond04_all_chk']:
            cqm.add_constraint(quicksum(vars.wd[w,d] for d in range(num_days)) <= num_days - opts['cond04_all_cnt'])

    # 5. 休→出→休の飛び石連休はなし
    if opts['cond05_chk']:
        for w in range(num_workers):
            for d in range(num_days - 2):
                cqm.add_constraint(vars.wd[w,d] - vars.wd[w,d+1] + vars.wd[w,d+2] >= 0)  
    
    # 6. 休みを週に１～６回以上割当（全員／個別）
    for w in range(num_workers):
        for wk in range(4):
            if opts['cond06_sel_chk'] and chr(ord('A')+w) in opts['cond06_sel_wrks']:
                cqm.add_constraint(quicksum(vars.wd[w,d + wk * 7] for d in range(7)) <= 7 - opts['cond06_sel_days'])
            elif opts['cond06_all_chk']:
                cqm.add_constraint(quicksum(vars.wd[w,d + wk * 7] for d in range(7)) <= 7 - opts['cond06_all_days'])

    # 7. １日の出勤人数はＸ人以上（平日／土日）
    for d in range(num_days):
        if opts['cond07_wrk_chk'] and (fst_dow + d) % 7 <= 4:
            cqm.add_constraint(quicksum(vars.wd[w,d] for w in range(num_workers)) >= opts['cond07_wrk_cnt'])
        elif opts['cond07_hol_chk'] and (fst_dow + d) % 7 >= 5:
            cqm.add_constraint(quicksum(vars.wd[w,d] for w in range(num_workers)) >= opts['cond07_hol_cnt'])

    # 8. 月の出勤日数を４～２４日以上（全員／個別）
    for w in range(num_workers):
        if opts['cond08_sel_chk'] and chr(ord('A')+w) in opts['cond08_sel_wrks']:
            cqm.add_constraint(quicksum(vars.wd[w,d] for d in range(num_days)) >= opts['cond08_sel_days'])
        elif opts['cond08_all_chk']:
            cqm.add_constraint(quicksum(vars.wd[w,d] for d in range(num_days)) >= opts['cond08_all_days'])
    
    # 9. 週の出勤日数は１～６日以上（全員／個別）
    for w in range(num_workers):
        for wk in range(4):
            if opts['cond09_sel_chk'] and chr(ord('A')+w) in opts['cond09_sel_wrks']:
                cqm.add_constraint(quicksum(vars.wd[w,d + wk * 7] for d in range(7)) >= opts['cond09_sel_days'])
            elif opts['cond09_all_chk']:
                cqm.add_constraint(quicksum(vars.wd[w,d + wk * 7] for d in range(7)) >= opts['cond09_all_days'])

    # 10. 一緒に勤務させる
    if opts['cond10_chk']:
        for d in range(num_days):
            for grp_chr in [opts['cond10_wrks_A'], opts['cond10_wrks_B'], opts['cond10_wrks_C']]:
                grp_num = list(map(lambda x: wrk_chr.index(x), grp_chr))
                for cmb in itertools.combinations(grp_num, 2):
                    cqm.add_constraint(vars.wd[cmb[0],d] - vars.wd[cmb[1],d] == 0)  
    
    # 11. 一緒に勤務させない
    if opts['cond11_chk']:
        for d in range(num_days):
            for grp_chr in [opts['cond11_wrks_A'], opts['cond11_wrks_B'], opts['cond11_wrks_C']]:
                grp_num = list(map(lambda x: wrk_chr.index(x), grp_chr))
                for cmb in itertools.combinations(grp_num, 2):
                    #cqm.add_constraint(2 * vars.dww[d,cmb[0],cmb[1]] - vars.wd[cmb[0],d] - (1 - vars.wd[cmb[1],d]) <= 0)  
                    #cqm.add_constraint(2 * (1 - vars.dww[d,cmb[0],cmb[1]]) - (1 - vars.wd[cmb[0],d]) - vars.wd[cmb[1],d] <= 0) 
                    cqm.add_constraint(vars.wd[cmb[0],d] + vars.wd[cmb[1],d] - 1 <= 0) 

    # 12. 特定の日を休みにする（個別）
    if opts['cond12_chk']:
        for w in list(map(lambda x: wrk_chr.index(x), opts['cond12_wrks'])):
            for d in opts['cond12_days']:
                cqm.add_constraint(vars.wd[w,d-1] == 0) 

    # 13. 特定の曜日を休みにする（個別）
    if opts['cond13_chk']:
        for w in list(map(lambda x: wrk_chr.index(x), opts['cond13_wrks'])):
            for dow in list(map(lambda x: dow_chr.index(x), opts['cond13_dows'])):
                for d in [x for x in range(num_days) if ((x + fst_dow) % 7) == dow]:
                    cqm.add_constraint(vars.wd[w,d] == 0) 

def define_objective(cqm: ConstrainedQuadraticModel, opts: dict, vars: Variables):
    num_workers = opts['num_workers']
    num_days = opts['num_days']
    obj_sign = opts['obj_sign']
    cqm.set_objective(quicksum(obj_sign * vars.wd[w, d] for w in range(num_workers) for d in range(num_days)))

def build_cqm(opts: dict, vars: Variables) -> ConstrainedQuadraticModel:
    cqm = ConstrainedQuadraticModel()
    add_constraints(cqm, opts, vars)
    define_objective(cqm, opts, vars)
    return cqm

def call_solver(cqm: ConstrainedQuadraticModel, opts: dict) -> SampleSet:
    use_cqm_solver = opts['use_cqm_solver']
    time_limit = opts['time_limit']

    if use_cqm_solver:
        sampler = LeapHybridCQMSampler()
        res = sampler.sample_cqm(cqm, time_limit=time_limit, label='Shift Scheduling')
    else:
        sampler = MIPCQMSolver()
        res = sampler.sample_cqm(cqm, time_limit=time_limit)

    res.resolve()
    feasible_sampleset = res.filter(lambda d: d.is_feasible)

    try:
        best_feasible = feasible_sampleset.first.sample
        return best_feasible
    except ValueError:
        raise RuntimeError(
            "答えが得られませんでした。制限時間を増やすか条件を調整してください。"
        )

def make_df(sample: SampleSet, opts: dict, vars: Variables) -> pd.DataFrame:
    num_workers = opts['num_workers']
    num_days = opts['num_days']
    fst_dow = opts['fst_dow']

    wd_tbl = [[wd_chr[int(vars.wd[w,d].energy(sample))] for d in range(num_days)] for w in range(num_workers)]
    rows = [chr(ord('A') + w) for w in range(num_workers)]
    cols = [str(d + 1) + ' (' + dow_chr[(d + fst_dow) % 7] + ')' for d in range(num_days)]

    df = pd.DataFrame(data=wd_tbl, index=rows, columns=cols)
    return df

if __name__ == '__main__':

    vars = Variables(options)
    cqm = build_cqm(options, vars)
    best_feasible = call_solver(cqm, options)
    df = make_df(best_feasible, options, vars)
    print(df)

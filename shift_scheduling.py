from dwave.system import LeapHybridCQMSampler
from dimod import quicksum, ConstrainedQuadraticModel, Binary, SampleSet

import numpy as np
import pandas as pd

from mip_solver import MIPCQMSolver

dow_chr = ['月','火','水','木','金','土','日']
wd_chr = ['－', '〇']

options = {
    'use_cqm_solver': False,
    'time_limit': 120,
    'num_workers': 20,
    'num_days': 30,
    'fst_dow': 0,
}

class Variables:
    def __init__(self, opts: dict):
        num_workers = opts['num_workers']
        num_days = opts['num_days']

        self.wd = {(w, d): Binary(f'worker_{w}_day_{d}') for w in range(num_workers) for d in range(num_days)}
        #self.wwe = {(w, we): Binary(f'worker_{w}_weekend_{we}') for w in range(num_workers) for we in range(num_weekends)}


def add_constraints(cqm: ConstrainedQuadraticModel, opts: dict, vars: Variables):
    num_workers = opts['num_workers']
    num_days = opts['num_days']

    # 5日連続勤務をしたら、1日休みを割り当てる
    for w in range(num_workers):
        for d in range(num_days - 5):
            cqm.add_constraint(quicksum(vars.wd[w,d + i] for i in range(6)) <= 5)

def define_objective(cqm: ConstrainedQuadraticModel, opts: dict, vars: Variables):
    num_workers = opts['num_workers']
    num_days = opts['num_days']

    cqm.set_objective(quicksum(-vars.wd[w, d] for w in range(num_workers) for d in range(num_days)))

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
    #print(feasible_sampleset)

    try:
        best_feasible = feasible_sampleset.first.sample
        return best_feasible
    except ValueError:
        raise RuntimeError(
            "Sampleset is empty, try increasing time limit or " +
            "adjusting problem config."
        )

def make_df(sample: SampleSet, opts: dict, vars: Variables) -> pd.DataFrame:
    num_workers = opts['num_workers']
    num_days = opts['num_days']
    fst_dow = opts['fst_dow']

    wd_tbl = [[wd_chr[int(vars.wd[w,d].energy(sample))] for d in range(num_days)] for w in range(num_workers)]
    rows = [chr(ord('A') + w) for w in range(num_workers)]
    cols = [dow_chr[(d + fst_dow) % 7] + str(d // 7 + 1) for d in range(num_days)]

    df = pd.DataFrame(data=wd_tbl, index=rows, columns=cols)
    return df

if __name__ == '__main__':

    vars = Variables(options)
    cqm = build_cqm(options, vars)
    best_feasible = call_solver(cqm, options)
    df = make_df(best_feasible, options, vars)
    print(df)

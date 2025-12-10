import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from gurobipy import Model, GRB, quicksum
from collections import defaultdict


def solver(S, T, H, C, U, t_pref, D, p, outputflag):
    model = Model('aalbor_u')

    # =========================
    #   DATA DUPLICATION
    # =========================
    n_workshops = len(T)
    T1 = list(range(n_workshops))
    T2 = [t + n_workshops for t in T1]
    T = T1 + T2
    U = U + U
    D = D + D

    # =========================
    #        VARIABLES
    # =========================
    z = model.addVars(T, vtype=GRB.BINARY, name="z")      # 1 if workshop i is held, 0 otherwise
    y = model.addVars(T, H, vtype=GRB.BINARY, name="y")   # 1 if workshop i is held in time slot h, 0 otherwise
    w = model.addVars(S, T, vtype=GRB.BINARY, name="w")   # 1 if student s is assigned to workshop i

    # =========================================================
    #                    CONSTRAINTS
    # =========================================================

    # ---------- Facility Location ----------
    for t in T:
        if D[t] == 1:  # full-day workshop
            model.addConstr(
                quicksum(y[t, h] for h in H) == 2 * z[t],
                name=f"full_day_taller[{t}]"
            )
        else:
            model.addConstr(
                quicksum(y[t, h] for h in H) == z[t],
                name = f"assign_timeslot[{t}]"
            )

    for h in H:
        model.addConstr(
            quicksum(y[t, h] for t in T) <= C[h],
            name = f"timeslot_capacity[{h}]"
        )

    # ---------- Student Assignment ----------
    # each student in at least 1 workshop
    for s in S:
        model.addConstr(
            quicksum(w[s, t] for t in T) >= 1,
            name = f"student_assignment[{s}]"
        )

    # workshop capacity is not exceeded if the workshop is held
    for t in T:
        model.addConstr(
            quicksum(w[s, t] for s in S) <= U[t] * z[t],
            name=f"cap_workshop[{t}]"
        )

    # prevents a student from attending 2 workshops in parallel
    for s in S:
        for h in H:
            model.addConstr(
                quicksum(w[s, t] * y[t, h] for t in T if D[t] == 0) <= 1,
                name = f"schedule_conflict[{s},{h}]"
            )

    # ---------- Extra ----------
    # complete daily load
    for s in S:
        # sum of assigned units: half-day = 1, full-day = 2
        assigned_units = quicksum(w[s, t] * (1 + D[t]) for t in T)

        # everyone must complete 2 units
        model.addConstr(
            assigned_units == 2,
            name=f"complete_2_units[{s}]"
        )

    # only assign students to workshops that are actually held
    for s in S:
        for t in T:
            model.addConstr(
                w[s, t] <= z[t],
                name=f"assign_only_if_held[{s},{t}]"
            )

    # NOT the same workshop (prevents duplicates in AM/PM)
    for s in S:
        for i in range(n_workshops):
            model.addConstr(
                w[s, i] + w[s, i + n_workshops] <= 1
            )

    # =========================================================
    #                  OBJECTIVE FUNCTION
    # =========================================================
    model.setObjective(
        quicksum(
            p[i] * quicksum(
                w[s, t_pref[s][i + 1]] +
                w[s, t_pref[s][i + 1] + n_workshops]
                for s in S
            )
            for i in range(3)
        ),
        GRB.MAXIMIZE
    )

    # =========================================================
    #                      SOLVER
    # =========================================================
    model.Params.TimeLimit = 1800       # 30 min
    model.Params.OutputFlag = outputflag
    model.Params.Seed = 69420
    model.optimize()

    return model, y, z, w


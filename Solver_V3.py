import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from gurobipy import Model, GRB, quicksum
from collections import defaultdict


def solver(S, T, H, C, U, t_pref, D, p, outputflag):
    model = Model('aalbor_u')

    # =========================
    #   DUPLICACIÓN DE DATOS
    # =========================
    n_talleres = len(T)
    T1 = list(range(n_talleres))
    T2 = [t + n_talleres for t in T1]
    T = T1 + T2
    U = U + U
    D = D + D

    # =========================
    #        VARIABLES
    # =========================
    z = model.addVars(T, vtype=GRB.BINARY, name="z")      # 1 si el taller i se dicta, 0 si no
    y = model.addVars(T, H, vtype=GRB.BINARY, name="y")   # 1 si el taller i se dicta en el horario h, 0 si no
    w = model.addVars(S, T, vtype=GRB.BINARY, name="w")   # 1 si el estudiante s se asigna al taller i

    # =========================================================
    #                    RESTRICCIONES
    # =========================================================

    # ---------- Facility Location ----------
    for t in T:
        if D[t] == 1:  # taller de día completo
            model.addConstr(
                quicksum(y[t, h] for h in H) == 2 * z[t],
                name=f"full_day_taller[{t}]"
            )
        else:
            model.addConstr(
                quicksum(y[t, h] for h in H) == z[t],
                name=f"asign_horario[{t}]"
            )

    for h in H:
        model.addConstr(
            quicksum(y[t, h] for t in T) <= C[h],
            name=f"capacidad_horario[{h}]"
        )

    # ---------- Asignación de Estudiantes ----------
    # cada estudiante en al menos 1 taller
    for s in S:
        model.addConstr(
            quicksum(w[s, t] for t in T) >= 1,
            name=f"asign_est[{s}]"
        )

    # no se sobrepasa la capacidad del taller si es que este se da
    for t in T:
        model.addConstr(
            quicksum(w[s, t] for s in S) <= U[t] * z[t],
            name=f"cap_taller[{t}]"
        )

    # evita que un estudiante esté en 2 talleres en paralelo
    for s in S:
        for h in H:
            model.addConstr(
                quicksum(w[s, t] * y[t, h] for t in T if D[t] == 0) <= 1,
                name=f"conflicto_horario[{s},{h}]"
            )

    # ---------- Extra ----------
    # completar la carga diaria
    for s in S:
        # suma de unidades asignadas: medio día=1, día completo=2
        unidades_asignadas = quicksum(w[s, t] * (1 + D[t]) for t in T)

        # todos deben cumplir 2 unidades
        model.addConstr(
            unidades_asignadas == 2,
            name=f"completar_2_unidades[{s}]"
        )

    # solo asigno a talleres que se den
    for s in S:
        for t in T:
            model.addConstr(
                w[s, t] <= z[t],
                name=f"solo_si_se_dicta[{s},{t}]"
            )

    # NO el mismo taller (evita duplicar en AM/PM)
    for s in S:
        for i in range(n_talleres):
            model.addConstr(
                w[s, i] + w[s, i + n_talleres] <= 1
            )

    # =========================================================
    #                  FUNCIÓN OBJETIVO
    # =========================================================
    model.setObjective(
        quicksum(
            p[i] * quicksum(
                w[s, t_pref[s][i + 1]] +
                w[s, t_pref[s][i + 1] + n_talleres]
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


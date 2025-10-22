import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from gurobipy import Model, GRB, quicksum
from collections import defaultdict

def generate_col_nums(data):
    ans = {}
    c = 0
    for col in data.columns:
        ans[col] = c
        c += 1
    return ans

def get_dict(data, row):
    ans = {}
    # PROVISOR #
    ans[1] = 0
    ans[2] = 0
    ans[3] = 0
    names = generate_col_nums(data)           #asocia a cada taller un id 0, 1, ...
    for col in data.columns:
        if not np.isnan(data.iloc[row][col]): #si no es Nan, es decir, si está en su top 3
            ans[int(data.iloc[row][col])] = names[col]
    return ans

def ver_talleres(z):
    for i in range(len(z)):
        if (z[i].X) == 1.0:
            print(f"El taller {i} fue elegido para realizarse")
        else:
            print(f"El taller {i} no se realizará")

def talleres_horarios(y):
    talleres_AM = []
    talleres_PM = []
    for key, var in y.items():
        #print(key, var.X)
        if (var.X) == 1.0:
            if (key[1]) == 1:
                print(f"El taller {key[0]} se da en el horario PM")
                talleres_PM.append(key[0])
            else:
                print(f"El taller {key[0]} se da en el horario AM")  
                talleres_AM.append(key[0])

    return talleres_AM, talleres_PM

def ver_asignaciones(w):
    dic_asignaciones_realizadas = {}
    e = -1
    lista = []
    for key, var in w.items():
        if var.X == 1.0:
            #print(key, var.X)
            estudiante = key[0]
            if (estudiante == e):
                lista.append(key[1])
            else:            
                dic_asignaciones_realizadas[e] = lista
                e = estudiante
                lista = []
                lista.append(key[1])
            print(f"El estudiante {key[0]} fue asignado al taller {key[1]}")
    del dic_asignaciones_realizadas[-1] 

    return dic_asignaciones_realizadas

def get_par(pref):

    # --- Dimensiones ---
    n_students  = len(pref)        # number of students in master AAL
    n_workshops = pref.shape[1]    # number of workshops in master AAL

    S = [n for n in range(n_students)]   # numera a los estudiantes
    T = [n for n in range(n_workshops)]  # numera a los talleres

    # --- Horarios ---
    H = [0, 1]                           # AM (0) o PM (1)
                                        # Revisar siempre que sea válido, es decir, que el total de vacantes
                                        # para la mañana y la tarde sea >= que la cantidad de estudiantes.

    # --- Capacidades ---
    C = [3, 3]                           # capacidad de talleres por horario (AM, PM)
    U = [20 for _ in range(n_workshops)]# capacidad de cada taller (todos con 150 cupos)

    # --- Preferencias ---
    t_pref = [get_dict(pref, n) for n in range(n_students)]

    # --- Duración de talleres ---
    D = [0 for _ in range(n_workshops)]  # 1 si el taller es de día completo, 0 si no

    # --- Pesos ---
    p = [10, 5, 3]                       # pesos para cada preferencia

    return (S, T, H, C, U, t_pref, D, p)

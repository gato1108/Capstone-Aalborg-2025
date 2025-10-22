import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from gurobipy import Model, GRB, quicksum
from collections import defaultdict

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

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
    ans[1] = 0
    ans[2] = 0
    ans[3] = 0
    names = generate_col_nums(data)           #associate each workshop with an ID 0, 1, …
    for col in data.columns:
        if not np.isnan(data.iloc[row][col]): #if it is not NaN, i.e., if it is in their top 3 choices
            ans[int(data.iloc[row][col])] = names[col]
    return ans

def view_workshops(z):
    for i in range(len(z)):
        if (z[i].X) == 1.0:
            print(f"Workshop {i} was selected to be held")
        else:
            print(f"Workshop {i} will not be held")

def view_workshops_mod(z, m):
    for i in range(len(z)):
        if (z[i].X) == 1.0:
            print(f"Workshop {i % m}.{i // m} was selected to be held")
        else:
            print(f"Workshop {i%m}.{i//m} will not be held")

def workshop_schedules(y):
    workshops_AM = []
    workshops_PM = []
    for key, var in y.items():
        if (var.X) == 1.0:
            if (key[1]) == 1:
                print(f"Workshop {key[0]} is held in the PM time slot")
                workshops_PM.append(key[0])
            else:
                print(f"Workshop {key[0]} is held in the AM time slot") 
                workshops_AM.append(key[0])

    return workshops_AM, workshops_PM

def view_assignments(w):
    assignments_made_dict = {}
    e = -1
    list = []
    for key, var in w.items():
        if var.X == 1.0:
            #print(key, var.X)
            student = key[0]
            if (student == e):
                list.append(key[1])
            else:            
                assignments_made_dict[e] = list
                e = student
                list = []
                list.append(key[1])
            print(f"Student {key[0]} was assigned to workshop {key[1]}")
    assignments_made_dict[e] = list # add the last student
    del assignments_made_dict[-1] 

    return assignments_made_dict

def get_pair(pref):

    # --- Dimensions ---
    n_students  = len(pref)        # number of students in master AAL
    n_workshops = pref.shape[1]    # number of workshops in master AAL

    S = [n for n in range(n_students)]   # number the students
    T = [n for n in range(n_workshops)]  # number the workshops

    # --- Schedules ---
    H = [0, 1]                           # AM (0) or PM (1)
                                        # Always check that it is valid, i.e., that the total number of seats
                                        # in the morning and afternoon is >= the number of students.

    # --- Capacities ---
    C = [3, 3]                           # capacity of workshops by time slot (AM, PM)
    U = [20 for _ in range(n_workshops)] # capacity of each workshop

    # --- Preferences ---
    t_pref = [get_dict(pref, n) for n in range(n_students)]

    # --- Workshop duration ---
    D = [0 for _ in range(n_workshops)]  # 1 if the workshop is full-day, 0 if not

    # --- Weights ---
    p = [10, 5, 3]                       # weights for each preference

    return (S, T, H, C, U, t_pref, D, p)

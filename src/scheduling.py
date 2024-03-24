from constraint import Problem
import numpy as np
import pandas as pd

def split_values(values):
    if isinstance(values, str):
        values = values.split(', ')
    return values

def get_availabilities(unavailable, default):
    if not isinstance(unavailable, list):
        available = default
    else:
        available = list(set(default) - set(unavailable))
    return available

def get_schedules(people, shifts):
    people.unavailable = people.unavailable.apply(split_values)
    necessary = people.needed.apply(split_values).explode()
    availabilities = people.unavailable.apply(lambda x: get_availabilities(x, shifts)).explode()

    domains = {}
    for shift in shifts:
        needed = necessary[necessary == shift].index
        if len(needed):
            domain = needed.tolist()
        else:
            available = availabilities[availabilities == shift].index
            domain = available.tolist()
        domains[shift] = domain
    
    problem = Problem()

    for shift in shifts:
        problem.addVariable(variable=shift, domain=domains[shift])
    
    solutions = np.array(problem.getSolutions())

    unique_people = {num: [] for num in range(1, len(people) + 1)}
    for i, solution in enumerate(solutions):
        num_people = len(set(solution.values()))
        unique_people[num_people].append(i)

    unique_people = {key: np.array(val) for key, val in unique_people.items()}
    for val in unique_people.values():
        np.random.shuffle(val)

    idxs = []
    for key in sorted(unique_people, reverse=True):
        idxs += list(unique_people[key])
    
    solutions = solutions[np.array(idxs)]

    return solutions
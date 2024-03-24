from constraint import Problem
import numpy as np
import pandas as pd
import streamlit as st


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

# from scheduling import get_schedules

default_masses = np.load('data/masses.npy')
example_people = pd.read_csv('data/example_people.csv', dtype=str)

def set_default_masses():
    np.save('data/masses.npy', masses)

def generate_schedules():
    schedules = get_schedules(people, masses)
    return schedules

st.title('Mass Singer Scheduling')

st.header('Mass Times')
st.write(f"""The default mass times are {', '.join(default_masses)}.
         To change these, set them below.
""")
new_masses = st.text_input('Enter new mass times in the box separated by a comma and a space.')
masses = default_masses if new_masses == '' else new_masses.split(', ')
st.write(f"The mass times that will be used are {', '.join(masses)}")
st.button('Make these times the default', on_click=set_default_masses)

st.header('Availabilities')
st.write("""To get started, upload a csv file with the following information or manually enter it below.
         The first column (person) will be each person's name.
         The second column (unavailable) will be the mass/masses they are not available for.
         The third column (needed) will be the mass/masses they are required for.
         The numbers for the second and third column must match one of the mass times from above. 
         An example file can be seen below. The <NA> cells are just empty cells.
         """)

enter_manually = st.toggle('Enter Manually')
if not enter_manually:
    st.table(example_people)
    people_file = st.file_uploader('CSV File')
    if people_file is not None:
        people = pd.read_csv(people_file, index_col='person', dtype=str)
        st.write('Your file:')
        st.write(people)
else:
    st.text_input('Input here')

gen_schedules = st.button('Generate Schedules!')
if gen_schedules:
    schedules = generate_schedules()
    schedules = pd.DataFrame.from_records(schedules)
    st.table(schedules)

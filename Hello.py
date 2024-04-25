import streamlit as st
import requests
import random

# Function to fetch population data from eurostat API
def fetch_population_data():
    url = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/tps00001?format=JSON&time=2023&geo=BE&geo=BG&geo=CZ&geo=DK&geo=DE&geo=EE&geo=IE&geo=EL&geo=ES&geo=FR&geo=HR&geo=IT&geo=CY&geo=LV&geo=LT&geo=LU&geo=HU&geo=MT&geo=NL&geo=AT&geo=PL&geo=PT&geo=RO&geo=SI&geo=SK&geo=FI&geo=SE&indic_de=JAN&lang=en"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        population_values = data['value']
        geo_index_to_code = {str(v): k for k, v in data['dimension']['geo']['category']['index'].items()}
        geo_code_to_name = data['dimension']['geo']['category']['label']
        population_data = {geo_code_to_name[geo_index_to_code[k]]: v for k, v in population_values.items() if k in geo_index_to_code}
        return population_data
    else:
        st.error(f"Failed to retrieve data: {response.status_code}")
        return {}

def generate_question(population_data):
    correct_country, correct_population = random.choice(list(population_data.items()))
    incorrect_answers = set()
    while len(incorrect_answers) < 3:
        method = random.choice(['percent', 'fixed', 'factor'])
        if method == 'percent':
            adjustment = random.choice([0.9, 0.95, 1.05, 1.1])
            new_population = int(correct_population * adjustment)
        elif method == 'fixed':
            adjustment = random.randint(100000, 500000)
            new_population = correct_population + random.choice([-1, 1]) * adjustment
        elif method == 'factor':
            adjustment = random.choice([0.85, 0.9, 0.95, 1.05, 1.1, 1.2])
            new_population = int(correct_population * adjustment)
        if new_population != correct_population:
            incorrect_answers.add(new_population)
    options = list(incorrect_answers) + [correct_population]
    random.shuffle(options)
    question = f"What is the population of {correct_country}?"
    return question, options, correct_population

def set_new_question():
    st.session_state.question, st.session_state.options, st.session_state.correct_answer = generate_question(st.session_state.data)

st.title('Population Quiz')

if 'data' not in st.session_state:
    st.session_state.data = fetch_population_data()

# Main block to handle quiz setup and response
if st.session_state.data:
    if 'init' not in st.session_state or st.session_state.init:
        set_new_question()
        st.session_state.init = False  # Flag to not reset question on each run, unless "Next Question" is pressed

    st.subheader(st.session_state.question)
    option_indices = [f"{idx + 1}: {option}" for idx, option in enumerate(st.session_state.options)]
    user_choice = st.radio("Choose the correct answer:", option_indices, key='user_choice')

    if st.button("Submit"):
        st.session_state.submitted = True  # Track that submit was pressed
        if int(user_choice.split(': ')[0]) == st.session_state.options.index(st.session_state.correct_answer) + 1:
            st.success("Correct!")
        else:
            st.error("Incorrect!")
        st.write(f"The correct population is {st.session_state.correct_answer}.")

    if 'submitted' in st.session_state and st.session_state.submitted:
        if st.button("Next Question"):
            set_new_question()  # This resets the question, options, and correct answer
            st.session_state.submitted = False  # Reset the submitted flag
else:
    st.error("Unable to load population data.")
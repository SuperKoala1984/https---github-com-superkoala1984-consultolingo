import streamlit as st
import requests
import random
import matplotlib.pyplot as plt

# Function to fetch population data
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

# Function to generate all questions at once
def generate_questions(population_data):
    questions = []
    for _ in range(10):
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
        questions.append((question, options, correct_population))
    return questions

def display_results():
    st.subheader("Quiz Results")
    correct_count = st.session_state.score
    incorrect_count = 10 - correct_count
    labels = ['Correct Answers', 'Incorrect Answers']
    sizes = [correct_count, incorrect_count]
    explode = (0.1, 0)  # explode 1st slice
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%', startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    st.pyplot(fig1)
    st.write(f"Final Score: {st.session_state.score}/10")

    if st.button("Restart Quiz"):
        st.session_state.clear()  # Clears the entire session state
        st.experimental_rerun()  # Rerun the app to reinitialize the state

def main():
    st.title('European Population Quiz')

    if 'questions' not in st.session_state or not st.session_state.questions:
        population_data = fetch_population_data()
        st.session_state.questions = generate_questions(population_data)
        st.session_state.question_count = 0
        st.session_state.score = 0

    if st.session_state.questions:
        if st.session_state.question_count < 10:
            question, options, correct_answer = st.session_state.questions[st.session_state.question_count]
            st.subheader(f"Question {st.session_state.question_count + 1}: {question}")
            user_choice = st.radio("Choose the correct answer:",
                                   [f"{idx + 1}: {option}" for idx, option in enumerate(options)],
                                   key='user_choice')
            if st.button("Submit"):
                if user_choice:
                    if int(user_choice.split(': ')[0]) == options.index(correct_answer) + 1:
                        st.success("Correct!")
                        st.session_state.score += 1
                    else:
                        st.error("Incorrect!")
                        st.write(f"The correct population is {correct_answer}.")

                    st.session_state.question_count += 1
                    if st.session_state.question_count < 10:
                        st.button("Next Question")  # This button does nothing but trigger rerender.
                    else:
                        st.session_state.show_results = True
                        st.experimental_rerun()
                else:
                    st.error("Please choose an answer to proceed!")
        elif st.session_state.show_results:
            display_results()

if __name__ == "__main__":
    main()

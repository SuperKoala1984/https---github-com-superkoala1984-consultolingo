import streamlit as st
import requests
import random
import matplotlib.pyplot as plt

# Funktion, um die Bevölkerungsdaten zu erhalten. Wird definiert um danach in den Fragen darauf zurückgreifen zu können.
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

# Funktion, um alle Fragen auf ein Mal zu generieren
def generate_questions(population_data):
    questions = []
    for _ in range(10): # es sollen nur 10 Fragen pro Runde generiert werden
        correct_country, correct_population = random.choice(list(population_data.items()))
        incorrect_answers = set()
        while len(incorrect_answers) < 3: # 3/4 Auswahlmöglichkeiten sollen falsch sein, also werden solange keine 3 falschen Antworten existieren, solche generiert
            method = random.choice(['percent', 'fixed', 'factor']) # falsche Antworten werden zufällig durch 3 verschiedene Methoden generiert, welche unten definiert sind
            if method == 'percent':
                adjustment = random.choice([0.7, 0.85, 1.25, 1.3]) # Multiplikator wird zufällig gewählt
                new_population = int(correct_population * adjustment) # Generierung falscher Antwort anhand von prozentualer Abweichung
            elif method == 'fixed':
                adjustment = random.randint(300000, 500000) # Betrag wird zufällig gewählt
                new_population = correct_population + random.choice([-1, 1]) * adjustment # Generierung falscher Antwort indem ein fixer Betrag addiert oder subtrahiert wird
            elif method == 'factor':
                adjustment = random.choice([0.6, 0.7, 0.8, 1.15, 1.2, 1.35]) # Multiplikator wird zufällig gewählt
                new_population = int(correct_population * adjustment) # Generierung falscher Antwort durch Multiplikation mit einem Multiplikationsfaktor
            if new_population != correct_population:
                incorrect_answers.add(new_population)
        options = list(incorrect_answers) + [correct_population]
        random.shuffle(options) # richtige & falsche Antworten sollen nicht immer an derselben Stelle stehen, daher werden sie zufällig gemischt
        question = f"What is the population of {correct_country}?"
        questions.append((question, options, correct_population))
    return questions

def display_results(): # Funktion, um die Resultate anschaulich aufzuzeigen in einem Pie Chart
    st.subheader("Quiz Results") # Titel der Darstellung
    correct_count = st.session_state.score # Anzahl richtige Antworten, die während der Beantwortung gezählt wurden
    incorrect_count = 10 - correct_count # Anzahl falsche Antworten (Abgeleitet durch 10 - Anzahl richtige Antworten, da der Code nur die richtigen Antworten gezählt hat)
    labels = ['Correct Answers', 'Incorrect Answers'] # Titel der slices
    sizes = [correct_count, incorrect_count] # Grösse der slices
    explode = (0.1, 0)  # erstes sclice exploden
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%', startangle=90)
    ax1.axis('equal')   # equal Seitenverhältnis stellt sicher, dass der Pie Chart als Kreis gezeichnet wird
    st.pyplot(fig1)
    st.write(f"Final Score: {st.session_state.score}/10") # gibt Anzahl richtige Antworten von 10 gestellten Fragen an

    if st.button("Restart Quiz"): # button, um das Quiz erneut zu lösen
        st.session_state.clear()  # Löscht den gesamten session state
        st.experimental_rerun()  # Rückkehr der App um den state zu reinitialisieren

def main():
    st.title('European Population Quiz')

    if 'questions' not in st.session_state or not st.session_state.questions:
        population_data = fetch_population_data()
        st.session_state.questions = generate_questions(population_data)
        st.session_state.question_count = 0
        st.session_state.score = 0

    if st.session_state.questions:
        if st.session_state.question_count < 10: # 10 Fragen wurden noch nicht gestellt, daher wird eine weitere Frage angezeigt
            question, options, correct_answer = st.session_state.questions[st.session_state.question_count]
            st.subheader(f"Question {st.session_state.question_count + 1}: {question}")
            user_choice = st.radio("Choose the correct answer:",
                                   [f"{idx + 1}: {option}" for idx, option in enumerate(options)],
                                   key='user_choice')
            if st.button("Submit"): # Button, um Auswahl/Antwort abzugeben
                if user_choice: # Funktion, um der App zu erklären, was sie bei richtigen oder falschen Antworten zu tun hat
                    if int(user_choice.split(': ')[0]) == options.index(correct_answer) + 1:
                        st.success("Correct!") # Feedback, dass die Frage korrekt beantwortet wurde
                        st.session_state.score += 1 # Score wird um 1 erhöht
                    else:
                        st.error("Incorrect!") # Feedback, dass die Frage falsch beantwortet wurde
                        st.write(f"The correct population is {correct_answer}.") # So sehen Teilnehmende die korrekte Antwort und können aus Fehlern lernen

                    st.session_state.question_count += 1
                    if st.session_state.question_count < 10: # Dieser button wird nur angezeigt, wenn noch keine 10 Fragen gestellt wurden
                        st.button("Next Question")  # Dieser button hat keine Funktion, ausser den rerender auszulösen.
                    else:
                        st.session_state.show_results = True # Wenn 10 Fragen erreicht wurden, werden die Resultate anhand der oben vorgegebenen Funktion dargestellt
                        st.experimental_rerun()
                else:
                    st.error("Please choose an answer to proceed!") # Sollten User keine Antwort ausgesucht haben, werden sie dazu aufgefordert, um fortfahren zu können
        elif st.session_state.show_results: # 10 Fragen sind schon erreicht, also werden die Resultate angezeigt
            display_results() # Um die Resultate zu veranschaulichen

if __name__ == "__main__":
    main()

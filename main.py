import os
import re
import random

import streamlit as st
import openai
import json

# Set the temperature for OpenAI to generate a response
temp = 0.5
system_message = f"""
    You are a {{year_group}} {{subject}} teacher in the English National Curriculum.
    You communicate by asking multiple choice questions with 4 options. The questions have only one correct answer.
    You ask one question at a time. Be direct, nothing but the question.
    You wait for the student to answer.
    Then you give a short explanation on the answer.
    Special instructions:
    - Insert a blank line between the question and the answers.
    - Your feedback should always start with either 'Correct' of 'Incorrect'.
    - Don't prompt for an answer.
    - Change the letter of the correct answer between questions.

    Now ask questions about the following topic:
    {{topic}}
    """

st.set_page_config(page_title='BSG Revision Quizz', page_icon=':robot:')
st.image('BSG-RGB.jpg', width=300)
st.header('BSG Revision Quizz')

st.session_state.debug = False

if 'topic_list' not in st.session_state:
    st.session_state.topic_list = {}
    st.session_state.subject_list = {}
    for yg in ('Year 10', 'Year 11'):
        # get filename from Year Group (e.g. Year 10 --> 'year10.json')
        file_name = f'{yg.lower().replace(" ", "")}.json'
        try:
            with open(file_name, 'r') as file:
                st.session_state.topic_list[yg] = json.load(file)
            st.session_state.subject_list[yg] = sorted(st.session_state.topic_list[yg].keys())
        except FileNotFoundError:
            # Handle the case when the file is not found
            st.error(f"File '{file_name}' not found. Skipping...", icon="🚨")
        except json.JSONDecodeError:
            # Handle the case when there is an issue decoding the JSON file
            st.error(f"Error decoding JSON file '{file_name}'. Skipping...", icon="🚨")

year_group_list = ('Year 7', 'Year 8', 'Year 9', 'Year 10', 'Year 11', 'Year 12', 'Year 13')
openai.api_key = os.getenv('OPENAI_API_KEY')

if 'started' not in st.session_state or not st.session_state.started:
    if openai.api_key is None:
        st.text_input('Please enter your OpenAI API key')
    st.markdown("""
        Please select the subject and topic you want to review.
    """)

if 'started' in st.session_state and st.session_state.started:
    is_started = True
else:
    is_started = False

col1, col2 = st.columns(2)
with col1:
    selection_mode = st.radio('Subject selection:', ('From list', 'Manual selection'), disabled=is_started)
with col2:
    if selection_mode == 'Manual selection':
        year_group = st.selectbox('Year group:', year_group_list, index=4,
                                  disabled=(is_started or selection_mode == 'From list'))
    else:
        year_group = st.selectbox('Year group:', ('Year 10', 'Year 11'),
                                  disabled=(is_started or selection_mode == 'Manual selection'))

col1, col2 = st.columns(2)

if selection_mode == 'From list':
    with col1:
        selected_subject = st.selectbox('Subject', st.session_state.subject_list[year_group],
                                        key='selected_subject',
                                        disabled=is_started)
    with col2:
        selected_topic = st.selectbox('Topic', sorted(st.session_state.topic_list[year_group][selected_subject]),
                                      key='selected_topic',
                                      disabled=is_started)
else:
    with col1:
        selected_subject = st.text_input('Subject', key='selected_subject', disabled=is_started)
    with col2:
        selected_topic = st.text_input('Topic', key='selected_topic', disabled=is_started)


def send_message(text):
    """
    text: [str] message to be sent to ChatGPT
    """
    if st.session_state.debug:
        content = f'''"{text[-1]['content']}" has been submitted to ChatGPT'''
    else:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=text,
                temperature=temp,
            )
            content = response['choices'][0]['message']['content']
        except Exception as e:
            content = 'Error: ' + str(e)
    return content


def init():
    """
    Initialize the session state.
    Set the system prompt and get the first question
    :return:
    """
    st.session_state.started = True
    st.session_state.num_question = 1
    st.session_state.student_score = 0
    st.session_state.level = random.choice(['easy', 'intermediate', 'difficult'])
    prompt = system_message.format(year_group=year_group, subject=selected_subject, topic=selected_topic)
    st.session_state.quiz = [{'role': 'system',
                              'content': prompt},
                             {'role': 'user',
                              'content': f'First question (difficulty: {st.session_state.level})'}]
    init_question = send_message(st.session_state.quiz)
    st.session_state.quiz.append({'role': 'assistant', 'content': init_question})
    st.session_state.stage = 'question'
    return init_question


def display_question(offset):
    if st.session_state.num_question > 1:
        st.write(f'Your score: {st.session_state.student_score}/{st.session_state.num_question - 1}')
    st.markdown(f"## Question {st.session_state.num_question}")
    st.markdown(f"*Difficulty: {st.session_state.level}*")
    question = st.session_state.quiz[-offset]['content']
    # Replace all occurrences of a letter followed by a dot and a space with a new line character followed by the
    # same letter and dot
    question = re.sub(r'([A-Z][).]) ', r'\r\1 ', question)
    st.markdown(question)


def submit_answer():
    if st.session_state.answer == 'END':
        st.session_state.num_question = 12
        return 'END'
    else:
        answer = f'I think answer {st.session_state.answer} is Correct.'
        st.session_state.quiz.append({'role': 'user', 'content': answer})
        st.session_state.stage = 'answered'


def get_feedback():
    response = send_message(st.session_state.quiz)
    if response[0] == 'C':
        st.session_state.student_score += 1
    st.session_state.quiz.append({'role': 'assistant', 'content': response})
    return response


def get_next_question():
    st.session_state.level = random.choice(['easy', 'intermediate', 'difficult'])
    correct = random.choice(['A', 'B', 'C', 'D'])
    next_question_text = f"Next question (difficulty: {st.session_state.level}, correct answer: {correct})"
    st.session_state.quiz.append({'role': 'user', 'content': next_question_text})
    st.session_state.num_question += 1
    response = send_message(st.session_state.quiz)
    st.session_state.quiz.append({'role': 'assistant', 'content': response})
    return


# ------- It all really starts here --------
# If the quiz has not started, show the 'Start Quiz' button and initialize the quiz
if 'started' not in st.session_state or st.session_state.stage == 'init':
    # Initializing the quiz...
    st.session_state.stage = 'init'
    st.session_state.started = False
    st.button('Start Quiz', key='start_quiz', on_click=init)
# If the quiz has started, show the current question, get the answer
elif 'started' in st.session_state and st.session_state.stage == 'question' and st.session_state.num_question < 11:
    # displaying question
    display_question(1)
    st.session_state.answer = st.radio('What is your answer?',
                                       options=('A', 'B', 'C', 'D', 'END'),
                                       horizontal=True)
    st.button('Submit answer', on_click=submit_answer)
elif 'started' in st.session_state and st.session_state.stage == 'answered':
    # displaying feedback and fetching next question
    display_question(2)
    feedback = get_feedback()
    st.markdown(f'Your answer is: {st.session_state.answer}')
    st.markdown('---')
    st.markdown(f'### Feedback for question {st.session_state.num_question}')
    st.write(feedback)
    if st.session_state.num_question == 10:
        st.session_state.num_question += 1
        st.session_state.stage = 'question'
        st.button('View results')
    else:
        with st.spinner('Waiting for next question...'):
            get_next_question()
        st.session_state.stage = 'question'
        st.button('Next Question', key='next_question')
else:
    # Quiz complete, display all answered questions
    st.markdown(f'Quiz Complete!\nYour score is {st.session_state.student_score}/{st.session_state.num_question - 1}')
    st.markdown('---')
    st.markdown('## Thank you for using ChatGPT!')
    st.markdown('Here are the questions to review:')
    for i in range(2, len(st.session_state.quiz), 4):
        st.markdown(f'#### Question {round((i - 1) / 4) + 1}')
        st.markdown(st.session_state.quiz[i]['content'])
        if i + 1 < len(st.session_state.quiz):
            answer_letter = re.findall(r"\s[A-D]\s", st.session_state.quiz[i + 1]['content'])[0]
            st.markdown(f'**Your answer**: {answer_letter}')
        else:
            st.markdown('**Your answer**: None')
        if i + 2 < len(st.session_state.quiz):
            st.markdown(f'#### Feedback for question {round((i - 1) / 4) + 1}')
            st.markdown(st.session_state.quiz[i + 2]['content'])
    st.markdown('You can reload this page to start again.')
# st.session_state.quiz

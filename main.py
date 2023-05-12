import os
import streamlit as st
import openai
import json

system_message = """
    You are a Year 11 {subject} teacher in the English National Curriculum.
    You communicate by asking multiple choice questions with 4 options. The questions have only one correct answer.
    You ask one question at a time. Be direct, nothing but the question.
    You wait for the student to answer.
    Then you give a short feedback on the answer.
    Special instructions:
    - Insert a blank line between the question and the answers.
    - Insert a blank line after each answer item.
    - Your feedback should always start with either 'Correct' of 'Incorrect'.
    - don't prompt for an answer.

    Now ask questions about the following topic:
    {topic}
"""

st.set_page_config(page_title='BSG Revision Quizz', page_icon=':robot:')
st.image('BSG-RGB.jpg', width=300)
st.header('BSG Revision Quizz')

st.session_state.debug = False

if 'topic_list' not in st.session_state:
    with open('topics.json', 'r') as file:
        st.session_state.topic_list = json.load(file)
    st.session_state.subject_list = st.session_state.topic_list.keys()

#year_group_list = ('Year 7', 'Year 8', 'Year 9', 'Year 10', 'Year 11', 'Year 12', 'Year 13')
openai.api_key = os.getenv('OPENAI_API_KEY')

if 'started' not in st.session_state or not st.session_state.started:
    st.markdown("""
        Please select the subject and topic you want to review.
    """)

col1, col2 = st.columns(2)

with col1:
    if 'started' in st.session_state and st.session_state.started:
        selected_subject = st.selectbox('Subject', st.session_state.subject_list, key='selected_subject', disabled=True)
    else:
        selected_subject = st.selectbox('Subject', st.session_state.subject_list, key='selected_subject')
with col2:
    if 'started' in st.session_state and st.session_state.started:
        selected_topic = st.selectbox('Topic', st.session_state.topic_list[selected_subject], key='selected_topic', disabled=True)
    else:
        selected_topic = st.selectbox('Topic', st.session_state.topic_list[selected_subject], key='selected_topic')


def send_message(text):
    '''
    text: [str] message to be sent to ChatGPT
    '''
    if st.session_state.debug:
        content = f'''"{text[-1]['content']}" has been submitted to ChatGPT'''
    else:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=text,
            temperature=0.3,
        )
        content = response['choices'][0]['message']['content']
    # messages.append({"role": "user", "content": content})
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
    prompt = system_message.format(subject=selected_subject, topic=selected_topic)
    st.session_state.quiz = [{'role': 'system',
                              'content': prompt},
                             {'role': 'user',
                              'content': 'First question'}]
    init_question = send_message(st.session_state.quiz)
    st.session_state.quiz.append({'role': 'assistant', 'content': init_question})
    st.session_state.stage = 'question'
    return init_question


def display_question(offset):
    if st.session_state.num_question > 1:
        st.write(f'Your score: {st.session_state.student_score}/{st.session_state.num_question -1}')
    st.markdown(f"## Question {st.session_state.num_question}")
    st.write(st.session_state.quiz[-offset]['content'])


#def add_answer(choice):


def submit_answer():
    if st.session_state.answer == 'END':
        st.session_state.num_question = 12
        return 'END'
    else:
        answer = f'I think answer {st.session_state.answer} is Correct.'
        st.session_state.quiz.append({'role': 'user', 'content': answer})
        st.session_state.stage = 'answered'
        # Add to messages/dialogue history
        # Send to ChatGPT and get feedback


def get_feedback():
    response = send_message(st.session_state.quiz)
    if response[0] == 'C':
        st.session_state.student_score += 1
    st.session_state.quiz.append({'role': 'assistant', 'content': response})
    return response


def get_next_question():
    st.session_state.quiz.append({'role': 'user', 'content': 'Next question'})
    st.session_state.num_question += 1
    response = send_message(st.session_state.quiz)
    st.session_state.quiz.append({'role': 'assistant', 'content': response})
    return


# if 'quiz' in st.session_state:
#     st.session_state.quiz
#     st.write(f'qnum {st.session_state.num_question}')
#     st.session_state


# ------- It all really starts here --------
# If the quiz has not started, show the 'Start Quiz' button and initialize the quiz
if 'started' not in st.session_state or st.session_state.stage == 'init':
    # st.write('Initializing the quiz...')
    st.session_state.stage = 'init'
    st.session_state.started = False
    st.button('Start Quiz', key='start_quiz', on_click=init)
    # st.write('Creating the first question...')
# If the quiz has started, show the current question, get the answer
elif 'started' in st.session_state and st.session_state.stage == 'question' and st.session_state.num_question < 11:
    # st.write('displaying question')
    display_question(1)
    st.session_state.answer = st.radio('What is your answer?',
                             options=('A', 'B', 'C', 'D', 'END'),
                             horizontal=True)
    st.button('Submit answer', on_click=submit_answer)
elif 'started' in st.session_state and st.session_state.stage == 'answered':
    # st.write('displaying feedback')
    display_question(2)
    feedback = get_feedback()
    st.markdown(f'Your answer is: {st.session_state.answer}')
    st.markdown('---')
    st.markdown(f'### Feedback for question {st.session_state.num_question}')
    st.write(feedback)
    st.button('Next Question', key='next_question')
# elif 'started' in st.session_state and st.session_state.stage == 'feedback':
    st.session_state.stage = 'question'
    get_next_question()
else:
    st.markdown(f'Quiz Complete!\nYour score is {st.session_state.student_score}/{st.session_state.num_question -1}')


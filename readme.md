# BSG Revision Quizz

This is a Python application that generates multiple-choice exam questions for revision purposes. It uses the Streamlit framework for the user interface and the OpenAI GPT-3.5 language model for generating questions and feedback.

## Description

The application allows ChatGPT to interact with students by asking multiple-choice questions related to a specific subject and topic. The questions are generated using the OpenAI GPT-3.5 language model, and the students can choose their answers from four options. After submitting an answer, the application provides immediate feedback on its correctness.

## Features

- Students can select the year group, subject, and topic for the revision quiz.
- Questions are generated dynamically based on the selected parameters.
- Students can choose their answers from multiple-choice options.
- Immediate feedback is provided on the correctness of the answers.
- The application keeps track of the student's score throughout the quiz.
- At the end of the quiz, the student's score is displayed, along with the questions, chosen answers, and feedback for review.

## Installation

1. Clone the repository:

   ```shell
   git clone https://github.com/your-username/bsg-revision-quizz.git
   ```

2. Install the dependencies:

   ```shell
   pip install -r requirements.txt
   ```

3. Set up the OpenAI API key:

* Rename the .env.example file to .env.
* Replace the OPENAI_API_KEY value in the .env file with your OpenAI API key.

## Usage

1. Run the application:

   ```shell
    streamlit run main.py
   ```

2. Open the provided URL in your web browser.

3. Select the subject and topic for the revision quiz.

4. Click the "Start Quiz" button to begin the quiz.

5. For each question, choose the answer from the available options and click the "Submit answer" button.

6. After submitting an answer, the application will provide immediate feedback on its correctness.

7. Continue answering questions until the end of the quiz.

8. At the end of the quiz, the student's score and the questions with chosen answers and feedback will be displayed for review.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or create a pull request on the GitHub repository.

## License

This project is licensed under the MIT License. See the [LICENSE](https://chat.openai.com/LICENSE) file for more information.

Feel free to modify the `readme.md` file according to your needs and include any additional information you want.
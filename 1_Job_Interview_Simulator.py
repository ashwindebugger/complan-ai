import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List
from openai import OpenAI


load_dotenv()
client = OpenAI()

st.set_page_config(page_title="Job Interview Simulator", page_icon="📈")


def generate_questions(job_role, work_experience):
    model = ChatOpenAI(model="gpt-4o-mini")

    system_template = (
        "You are an intelligent competency diagnostic system. Ask a series of questions to the job seeker "
        "to test their competence, and based on their scores, recommend jobs to them."
    )

    human_prompt = f"Assume the given job seeker is a {job_role} with {work_experience} years of experience. Generate me a set of 5 questions to test their competence."

    prompt_template = ChatPromptTemplate.from_messages(
        [("system", system_template), ("user", human_prompt)]
    )

    parser = StrOutputParser()

    chain = prompt_template | model | parser

    try:
        response = chain.invoke({"job_role": job_role, "work_experience": work_experience})
        return response
    except Exception as e:
        st.error(f"Error generating questions: {e}")
        return ""

def get_questions(context):
    model = ChatOpenAI(model="gpt-4o-mini")

    class Questions(BaseModel):
        set_of_questions: List[str] = Field(description="List of questions to test the competence of the job seeker")

    parser = PydanticOutputParser(pydantic_object=Questions)
    format_instructions = parser.get_format_instructions()

    human_prompt = f"Here is the context: {context}. Extract the set of questions from the given context in order to test the competence of the job seeker. Generate the questions in the following format: {format_instructions}"
    prompt = PromptTemplate(
        template="You are an intelligent information extractor. Extract the set of questions from the given context to test the competence of the job seeker in a List format.\n{format_instructions}\n{human_prompt}\n",
        input_variables=["human_prompt"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    
    chain = prompt | model | parser

    try:
        response = chain.invoke({"human_prompt": human_prompt})
        return response
    except Exception as e:
        st.error(f"Error extracting questions: {e}")
        return ""
    
def calculate_score(answers, job_role, work_experience):
    model = ChatOpenAI(model="gpt-4o-mini")

    human_prompt = f"Assume the given job seeker is a {job_role} with {work_experience} years of experience. Calculate the score of the job seeker based on their answers to the questions. Here is the set of answers provided by the job seeker for each question: {answers}.Each question can be scored out of 5 points, leading to a maximum possible score of 25 points as only a set of 5 questions and ansers are provided."

    prompt = PromptTemplate(
        template="You are an intelligent competency diagnostic system. You are required to calculate the score of the job seeker based on their answers to the questions based on their job role and work experience.\n {human_prompt}",
        input_variables=["human_prompt"],
    )

    parser = StrOutputParser()

    chain = prompt | model | parser

    try:
        response = chain.invoke({"human_prompt": human_prompt})
        return response
    except Exception as e:
        st.error(f"Error generating scores: {e}")
        return ""

def main():
    if 'questions' not in st.session_state:
        st.session_state.questions = []
    if 'final_answers' not in st.session_state:
        st.session_state.final_answers = {}
    if 'job_role' not in st.session_state:
        st.session_state.job_role = ""
    if 'work' not in st.session_state:
        st.session_state.work = ""

    st.title("Job Interview Simulator")
    with st.sidebar:
        st.session_state.job_role = st.text_input("Enter your job role")
        st.session_state.work = st.text_input("Enter your work experience")

    st.write("Please enter your job role and work experience to generate a set of questions to test your competence")


    if st.button("Generate Questions"):
        response = generate_questions(st.session_state.job_role, st.session_state.work)
        res = get_questions(response)
        if res:
            st.session_state.questions = res.set_of_questions

    for i,question in enumerate(st.session_state.questions):
        st.write(question)
        # response = client.audio.speech.create(
        #     model="tts-1",
        #     voice="shimmer",
        #     input=f"{question}",
        # )
        # response.stream_to_file(f"output{i}.mp3")
        st.audio(f"output{i}.mp3", format="audio/mp3")
        answer = st.text_input("Enter your answer", key=question)
        st.session_state.final_answers[question] = answer

    if len(st.session_state.final_answers) == 5:
        if st.button("Submit Answers"):
            response = calculate_score(st.session_state.final_answers, st.session_state.job_role, st.session_state.work)
            st.write(response)

if __name__ == "__main__":
    main()

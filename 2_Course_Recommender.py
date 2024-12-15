import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.memory import ConversationBufferMemory
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import DeepLake
from langchain.chains import ConversationalRetrievalChain
from dotenv import load_dotenv

load_dotenv()

def get_pdf_text(pdf):
    text = ""
    pdfReader = PdfReader(pdf)
    for page in pdfReader.pages:
        text += page.extract_text()
    return text

def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=750,
        chunk_overlap=50,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks

def get_vectorstore(text_chunks):
    dataset_path = "./my_deeplake_candidate/"
    vectorstore = DeepLake.from_texts(text_chunks,dataset_path=dataset_path, embedding=GoogleGenerativeAIEmbeddings(model="models/embedding-001"))
    return vectorstore

def get_conversation_chain(vectorstore):
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro")
    memory = ConversationBufferMemory(memory_key='chat_history',return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        memory=memory,
        retriever=vectorstore.as_retriever(),
    )
    return conversation_chain

def generate_courses(job_role, work_experience, resume):
    raw_text = get_pdf_text(resume)

    text_chunks = get_text_chunks(raw_text)

    vectorstore = get_vectorstore(text_chunks)

    chain = get_conversation_chain(vectorstore)
    prompt3 = f'''You are an experienced Human Resource Manager and Courses recommendor who is specialized in analyzing the job resumes of the candidate and suggest them courses to imporove their skills.
    You have been asked to analyze and extract the skills in the resume of a candidate, and get the required skills that are necessary for the job role {job_role}. Output should contain only the skills wiith comparison with the candidate skills and the required skills for the job role.'''
    prompt = f'''You are an experienced Human Resource Manager and Courses recommendor who is specialized in analyzing the job resumes of the candidate and suggest them courses to imporove their skills.
    You have been asked to analyze and extract the skills in the resume of a candidate. Output should contain only the skills.'''
    response1 = chain({'question':prompt})
    prompt2 = f"Based on the job role {job_role} and work experience {work_experience} and skills possessed by them are {response1}, suggest the courses that the candidate should take to improve their skills and provide some course links on certain topics and format the response properly."
    response = chain({'question':prompt2})
    response2 = chain({'question':prompt3})
    st.subheader("Skills Gap Analysis:")
    st.write(response2['answer'])
    DeepLake.force_delete_by_path("./my_deeplake_candidate")
    st.subheader("Courses to improve skills:")
    st.write(response['answer'])

def start():
    st.title("Course Recommender")
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro")
    with st.sidebar:
        job_role = st.text_input("Job Role")
        work_experience = st.text_input("Work Experience")
        resume = st.file_uploader("Upload Resume")

    submit = st.button("Submit")
    if submit:
        with st.spinner('Processing...'):
            generate_courses(job_role, work_experience, resume)
            


if __name__ == "__main__":
    start()
import streamlit as st
import google.generativeai as genai
from io import BytesIO
from PyPDF2 import PdfReader
from docx import Document
import re
import time,json  # Import time to simulate progress in the example

# Function to load API key from JSON file
def load_api_key():
    with open('config.json', 'r') as f:
        config = json.load(f)
    return config.get('GEMINI_API_KEY')

GEMINI_API_KEY = load_api_key()

# Configure the Generative AI client
genai.configure(api_key=GEMINI_API_KEY)

def extract_text_from_pdf(file):
    pdf_reader = PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

def extract_text_from_docx(file):
    doc = Document(file)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

def extract_text_from_txt(file):
    return file.read().decode('utf-8')

def extract_text_from_document(file, file_type):
    if file_type == 'pdf':
        return extract_text_from_pdf(file)
    elif file_type == 'docx':
        return extract_text_from_docx(file)
    elif file_type == 'txt':
        return extract_text_from_txt(file)
    else:
        return ""

def chunk_text(text, max_chunk_size=2000):
    # Split text into chunks of a maximum size
    return [text[i:i + max_chunk_size] for i in range(0, len(text), max_chunk_size)]

def process_document(text):
    model = genai.GenerativeModel('gemini-pro')
    chunks = chunk_text(text)
    responses = []
    
    for chunk in chunks:
        # Simulate processing time for the example
        time.sleep(1)
        response = model.generate_content(f"Analyze this document chunk: {chunk}")
        responses.append(response.text)
    
    return " ".join(responses)

def categorize_question(question):
    question = question.lower()
    
    if any(phrase in question for phrase in ['explain', 'detail', 'in-depth', 'elaborate']):
        return 'detailed'
    elif any(phrase in question for phrase in ['summarize', 'brief', 'short']):
        return 'summary'
    elif any(phrase in question for phrase in ['compare', 'contrast']):
        return 'comparison'
    else:
        return 'general'

def ask_question(question, context):
    category = categorize_question(question)
    
    if category == 'detailed':
        prompt = f"Provide a detailed explanation based on the context: {context} Question: {question}"
    elif category == 'summary':
        prompt = f"Provide a brief summary based on the context: {context} Question: {question}"
    elif category == 'comparison':
        prompt = f"Compare and contrast based on the context: {context} Question: {question}"
    else:
        prompt = f"Answer the following question based on the context: {context} Question: {question}"
    
    model = genai.GenerativeModel('gemini-pro')
    # Simulate response generation time for the example
    time.sleep(2)
    response = model.generate_content(prompt)
    return response.text

def main():
    st.title('Document Q&A with AI')

    if 'processed_text' not in st.session_state:
        st.session_state.processed_text = ""
        st.session_state.questions_answers = []

    uploaded_file = st.file_uploader("Choose a document", type=['pdf', 'docx', 'txt'])
    if uploaded_file is not None:
        file_type = uploaded_file.type.split('/')[1]
        document_text = extract_text_from_document(uploaded_file, file_type)

        if st.button('Upload and Process Document'):
            with st.spinner('Processing document...'):
                try:
                    st.session_state.processed_text = process_document(document_text)
                    st.session_state.questions_answers = []
                    st.success('Document processed successfully!')
                except Exception as e:
                    st.error(f'Failed to process document: {e}')

    if st.session_state.processed_text:
        st.write("Ask your questions below:")

        # Display previous questions and answers
        for i, (question, answer) in enumerate(st.session_state.questions_answers):
            with st.expander(f'**Question {i + 1}:** {question}', expanded=False):
                st.write(f'**Answer {i + 1}:** {answer}')

        question = st.text_input('Your question', key='new_question')
        if question:
            with st.spinner('Generating response...'):
                try:
                    answer = ask_question(question, st.session_state.processed_text)
                    st.session_state.questions_answers.append((question, answer))
                    st.write(f'**Answer to your question:** {answer}')
                except Exception as e:
                    st.error(f'Failed to get answer: {e}')

    # Attribution Section
    st.write("---")  # Add a horizontal line for separation
    st.write("### Developed by UCI")
    st.write("This application was developed by **Aditya** and **Mahir**, under the **UCI** organization.")
    st.write("We hope you find this tool useful for your document analysis needs!")

if __name__ == "__main__":
    main()

import streamlit as st
import time
import json
import fitz
import datetime
import os
from langchain.llms import OpenAI
from langchain import PromptTemplate
from gtts import gTTS
import base64
import requests
from langchain.retrievers.you import YouRetriever
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from openai import OpenAI

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# Function to play audio in Streamlit
def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio controls autoplay="true">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(
            md,
            unsafe_allow_html=True,
        )

def get_ai_snippets_for_query(query):
    headers = {"X-API-Key": "96c6405a-eeac-42b5-9007-1a227a4db540<__>1ODef1ETU8N2v5f4zPTEJeNK"}
    params = {"query": query}
    return requests.get(
        f"https://api.ydc-index.io/search?query={query}",
        params=params,
        headers=headers,
    ).json()

def perform_rag(query):
    headers = {"X-API-Key": "team24<__>979f653e-c873-4ccd-b6df-8c7d21d6d621"}
    params = {"query": query}
    return requests.get(
        f"https://api.ydc-index.io/rag?query={query}",
        params=params,
        headers=headers,
    ).json()

# Function to generate audio from text
def generate_audio(text, language='en', audio_file_name='output_audio.mp3'):
    myobj = gTTS(text=text, lang=language, slow=False)
    myobj.save(audio_file_name)

# Main Streamlit App
st.title("Create a podcast from PDF")

# Upload PDF
pdf_upload = st.file_uploader("Upload a PDF", type=["pdf"])

# Process PDF
if pdf_upload is not None:
    with open("uploaded_pdf.pdf", "wb") as file:
        file.write(pdf_upload.getvalue())

    # Extract text from the PDF
    extracted_text = extract_text_from_pdf("uploaded_pdf.pdf")

    # Use AI model to generate summary
    snippets = ""
    citations = ""
    for i in range(5):
        newSnippet = get_ai_snippets_for_query("Tell me about "+ extracted_text[:100])['hits'][i]
        snippets += newSnippet['description'] 
        citations += "{i}. " + newSnippet['title'] + "url: " + newSnippet['url'] + "\n "
    summary_prompt = f"Summarize the following text into a 5-minute podcast script:\n\n{extracted_text} and insert the following sentences: {snippets} where it makes sense. Add [[]] around the snippets."

    client = OpenAI()
    llm = client.chat.completions.create(
        model='gpt-4-1106-preview',
        messages=[{"role": "system", "content": summary_prompt}]
    )
    
    summary = llm.choices[0].message.content



    # Save summary to a text file
    with open("summary.txt", "w") as file:
        file.write(summary)
    
    extra = perform_rag("Tell me the latest about this topic" + extracted_text[:100])
    print("EXTRA: ", extra)
    # Show summary
    st.text_area("Podcast Summary", summary, height=300)
    st.text_area("\n YOU.com: ", extra['answer'])
    st.text_area("\n Citations: ", citations)

# # Generate and Play Audio
# if st.button("Create Podcast"):
#     with open("summary.txt", "r") as file:
#         summary = file.read()
#     generate_audio(summary)
#     autoplay_audio('./output_audio.mp3')
from elevenlabs import generate, play, set_api_key
set_api_key(os.environ['xi_api_key'])

def generate_elevenlabs_audio(textIn, audio_file_name='outout_audio.mp3'):
    audioOut = generate(
        text=textIn,
        voice="Matthew",
        model="eleven_monolingual_v1"
    )
    return audioOut

# Generate and Play Audio
if st.button("Create Podcast"):
    with open("summary.txt", "r") as file:
        summary = file.read()
    out = generate_elevenlabs_audio(summary)
    st.audio(out)






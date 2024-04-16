import os

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()

raw_text = ""
with open("data/course.txt", "r", encoding="utf-8") as f:
    raw_text = f.read()

text_splitter = CharacterTextSplitter(
    separator="\n",
    chunk_size=800,
    chunk_overlap=200,
)
texts = text_splitter.split_text(raw_text)

embeddings = OpenAIEmbeddings()
db = FAISS.from_texts(texts, embeddings)
db.save_local("faiss_index")

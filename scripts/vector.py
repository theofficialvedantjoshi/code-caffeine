from dotenv import load_dotenv
from langchain_community.vectorstores.faiss import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter

load_dotenv()

raw_text = ""
with open("data/courses.txt", "r", encoding="utf-8") as f:
    raw_text = f.read()


text_splitter = CharacterTextSplitter(
    separator="\n",
    chunk_size=900,
    chunk_overlap=100,
)
texts = text_splitter.split_text(raw_text)

embeddings = OpenAIEmbeddings()
db = FAISS.from_texts(texts, embeddings)
db.save_local("faiss_index")

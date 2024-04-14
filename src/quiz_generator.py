import json

import pdfplumber
from dotenv import load_dotenv
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import ChatPromptTemplate
from langchain_community.vectorstores.faiss import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_openai.chat_models import ChatOpenAI
from langchain_text_splitters import CharacterTextSplitter

load_dotenv()


def gen_quiz(raw_text, topic, num_questions, type_of_question):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
    )
    texts = text_splitter.split_text(raw_text)

    embeddings = OpenAIEmbeddings()
    db = FAISS.from_texts(texts, embeddings)

    prompt_template = """You are QUizGPT, a chatbot that is an expert at creating quizes.
    Your responses are accurate, and detailed. Generate a quiz with number questions given by the user and in the format given by the user based on the following: {context}.
    Make the level of the questions intermediate to advanced.
    Do not ask straightforward and easy questions.
    Don't create any false information on your own.
    """

    if type_of_question == "mcq":
        user_input = f"""Generate a quiz with {num_questions} questions on {topic} in {type_of_question} format. Also, provide answers to each question at the end of the quiz. Format it as json object with the following structure: 
        str number (indexed from 1): 
            str question: str,
            List options: List[str],
            str answer: str
        
        Strictly return 0 questions if the topic is not relevant to the context and state the question field as "Not relevant to the context".
    """
    else:
        user_input = f"""Generate a quiz with {num_questions} questions on {topic} in {type_of_question} format. Also, provide answers to each question at the end of the quiz. Format it as json object with the following structure: 
        str number (indexed from 1): 
            str question: str,
            str answer: str

        Strictly return 0 questions if the topic is not relevant to the context and state the question field as "Not relevant to the context".

    """
    llm = ChatOpenAI(name="gpt-3.5-turbo")
    prompt = ChatPromptTemplate.from_template(prompt_template)
    chain = load_qa_chain(llm=llm, chain_type="stuff")
    docs = db.similarity_search(user_input)
    answer = chain.invoke(
        {"input_documents": docs, "question": user_input, "prompt": prompt}
    )
    print(answer["output_text"])
    try:
        return json.loads(answer["output_text"])
    except:
        gen_quiz(raw_text, topic, num_questions, type_of_question)


if __name__ == "__main__":
    pdf = pdfplumber.open("files/campbell.pdf")
    raw_text = ""
    for page in pdf.pages:
        raw_text += page.extract_text()
    print(gen_quiz(raw_text, "Calvin Cycle", 2, "fill in the blank"))
    print(gen_quiz(raw_text, "Calvin Cycle", 2, "mcq"))

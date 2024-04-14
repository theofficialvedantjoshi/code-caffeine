import os

from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.retrieval import create_retrieval_chain
from langchain.prompts import ChatPromptTemplate
from langchain_community.chat_message_histories.in_memory import ChatMessageHistory
from langchain_community.vectorstores.faiss import FAISS
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_openai.chat_models import ChatOpenAI
from langchain_text_splitters import CharacterTextSplitter
from dotenv import load_dotenv
from src.data_extractor import extract_info

load_dotenv()

llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0,
)


history = ""


def chat_bot(user_input, history):
    raw_text = extract_info(user_input)
    if history:
        raw_text += extract_info(history)
    embeddings = OpenAIEmbeddings()
    text_splitter = CharacterTextSplitter(
        separator="\n\n",
        chunk_size=10000,
        chunk_overlap=400,
    )
    texts = text_splitter.split_text(raw_text)

    embeddings = OpenAIEmbeddings()
    retriever = FAISS.from_texts(texts, embeddings).as_retriever()
    contextualize_q_system_prompt = """Given a chat history and the latest user question
    which might reference context in the chat history, formulate a standalone question
    which can be understood without the chat history. Do NOT answer the question,
    just reformulate it if needed and otherwise return it as is."""
    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

    history_aware_retriever = create_history_aware_retriever(
        llm,
        retriever,
        contextualize_q_prompt,
    )

    qa_system_prompt = """You are CourseGPT, a chatbot that is an expert at telling college students information about their courses.
    Your responses are accurate, and crisp. Use the json text that contains information regarding course codes and each course codes units,names, classroom sections, exams details, course description and course books.
    Use the text below:
    ({context}).

    Give an exact answer to the user's question based on the context.
    """
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", qa_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    store = {}

    def get_session_history(session_id: str) -> BaseChatMessageHistory:
        if session_id not in store:
            store[session_id] = ChatMessageHistory()
        return store[session_id]

    conversational_rag_chain = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )
    return conversational_rag_chain.invoke(
        {"input": user_input}, config={"configurable": {"session_id": "abc123"}}
    )["answer"]


while True:
    user_input = input("\033[31m" + "You:\033[0m ")
    if user_input.lower() == "exit":
        break
    answer = chat_bot(user_input, history)
    history = history + "\n" + "user input: " + user_input + "\n" + "answer " + answer
    print(f"\033[36m\nCourseGPT:\033[0m \033[34m{answer}\033[0m\n")

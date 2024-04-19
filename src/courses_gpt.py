import os

from dotenv import load_dotenv
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

load_dotenv()

embeddings = OpenAIEmbeddings()
llm = ChatOpenAI(name="gpt-3.5-turbo", api_key=os.environ["OPENAI_API_KEY"])
retriever = FAISS.load_local(
    "faiss_index", embeddings, allow_dangerous_deserialization=True
).as_retriever()


def init_chat_bot():
    contextualize_q_system_prompt = """Given a chat history and the latest user question
    which might reference context in the chat history, formulate a standalone question
    which can be understood without the chat history. Do NOT answer the question,
    just reformulate it if needed and otherwise return it as is. Try to keep the most recent message as the focus of the question if related."""
    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )

    qa_system_prompt = """You are CourseGPT, a chatbot that is an expert at telling college students information about their courses.
    Your responses are friendly, accurate and crisp. Use the text below to answer the user's questions:
    ({context}).
    ---
    This contains information regarding courses offered by BITS Pilani, Hyderabad Campus; namely, course code, units, name, classroom sections, exams details, course description and course books.
    If you need more information, ask the user for more details.
    Strictly do not make up any information. If you don't know the answer, you can say that you don't know."""
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

    return conversational_rag_chain


def respond(conversational_rag_chain: RunnableWithMessageHistory, user_input):
    return conversational_rag_chain.invoke(
        {"input": user_input}, config={"configurable": {"session_id": "abc123"}}
    )["answer"]


if __name__ == "__main__":
    init_chat_bot()

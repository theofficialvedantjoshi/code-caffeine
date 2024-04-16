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
from dotenv import load_dotenv

load_dotenv()

embeddings = OpenAIEmbeddings()
llm = ChatOpenAI(name="gpt-3.5-turbo", api_key=os.environ["OPENAI_API_KEY"])
retriever = FAISS.load_local(
    "faiss_index", embeddings, allow_dangerous_deserialization=True
).as_retriever()


def chat_bot():
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
        llm, retriever, contextualize_q_prompt
    )

    qa_system_prompt = """You are CourseGPT, a chatbot that is an expert at telling college students information about their courses.
    Your responses are accurate, and crisp. Use the json text that contains information regarding course codes and each course codes units,names, classroom sections, exams details, course description and course books.
    Use the text below:
    ({context}).
    ----------------------------------------
    Give an exact answer to the user's question based on the context."""
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

    while True:
        user_input = input("\033[31m" + "You:\033[0m ")
        if user_input.lower() == "exit":
            break
        answer = conversational_rag_chain.invoke(
            {"input": user_input}, config={"configurable": {"session_id": "abc123"}}
        )["answer"]
        print(f"\033[36m\nCoursesGPT:\033[0m \033[34m{answer}\033[0m\n")


if __name__ == "__main__":
    chat_bot()

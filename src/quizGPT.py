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

    qa_system_prompt = """You are QUizGPT, a friendly chatbot that is an expert at creating quizes.
    Your responses are accurate, and detailed. Generate a quiz with number questions given by the user and in the format given by the user based on the ({context}).
    Make the level intermediate to advanced.
    Do not ask straightforward and easy questions.
    Don't create any false information on your own.
    Provide answers to each question at the end of the quiz.
    ---
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

    while True:
        topic = input("\033[31m" + "Enter Topic:\033[0m ")
        num_questions = input("\033[31m" + "Enter Number of Questions:\033[0m ")
        type_of_question = input("\033[31m" + "Enter Type of Question:\033[0m ")
        user_input = f"Generate a quiz with {num_questions} questions on {topic} in {type_of_question} format."
        answer = conversational_rag_chain.invoke(
            {"input": user_input}, config={"configurable": {"session_id": "abc123"}}
        )["answer"]
        print(f"\033[36m\nQuizGPT:\033[0m \033[34m{answer}\033[0m\n")


if __name__ == "__main__":
    chat_bot()

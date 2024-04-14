from typing import List, Optional

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_text_splitters import TokenTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()


def extract_info(question):
    class Courseinformation(BaseModel):
        """Information about courses in a university."""

        code: str = Field(
            ..., description="Course code of the course. Example: 'CS F111', 'CS F211'"
        )
        name: str = Field(
            ..., description="Name of the course. Example: 'Data Structures'"
        )
        units: str = Field(..., description="Number of units of the course")
        sections: List[str] = Field(
            ...,
            description="Sections of the course in dictionary form Example: 'Section L1 Instructor: XYZ Room: XYZ Days: D1, D2 Hours: hours'",
        )

        description: str = Field(..., description="Description of the course")
        books: str = Field(..., description="Course Books of the course")

    class ExtractionData(BaseModel):
        """Exctracted Course information from the text file"""

        course_info: List[Courseinformation]

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are an expert at identifying and exctracting information of courses from text"""
                "Only extract information for the relevant to a course. Do not include any irrelevant information.",
            ),
            # MessagesPlaceholder('examples'), # Keep on reading through this use case to see how to use examples to improve performance
            ("human", "{text}"),
        ]
    )

    llm = ChatOpenAI(
        # Consider benchmarking with a good model to get
        # a sense of the best possible quality.
        model="gpt-3.5-turbo",
        # Remember to set the temperature to 0 for extractions!
        temperature=0,
    )

    extractor = prompt | llm.with_structured_output(
        schema=ExtractionData,
        method="function_calling",
        include_raw=False,
    )
    text_splitter = TokenTextSplitter(
        # Controls the size of each chunk
        chunk_size=900,
        # Controls overlap between chunks
        chunk_overlap=100,
    )
    raw_text = ""
    with open("data/course.txt", "r", encoding="utf-8") as f:
        raw_text = f.read()
    texts = text_splitter.split_text(raw_text)

    vectorstore = FAISS.from_texts(texts, embedding=OpenAIEmbeddings())
    retriever = vectorstore.as_retriever()
    rag_extractor = {
        "text": retriever
        | (lambda docs: docs[0].page_content)  # fetch content of top doc
    } | extractor

    results = rag_extractor.invoke(question)
    return str(results)

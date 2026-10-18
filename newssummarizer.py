from dotenv import load_dotenv
load_dotenv()
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq

search_tool = TavilySearchResults(max_result = 5)
llm = ChatGroq(
    model="openai/gpt-oss-20b"
)
prompt = ChatPromptTemplate.from_template(
    """
You are a helpful assistant
summarize the following news into clear bullet points

{news}
"""
)

seq = prompt | llm | StrOutputParser()

news_result = search_tool.run("Latest AI news of 2026")

result = seq.invoke({"news" : news_result})
print(result)
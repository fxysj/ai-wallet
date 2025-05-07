#内存服务信息
from langchain.chains.retrieval import create_retrieval_chain
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import  settings
pre = "./chrom_dir"
em = OpenAIEmbeddings(base_url=settings.OPENAI_API_BASE_URL,api_key=settings.OPENAI_API_KEY)
# Documents=[
# Document(page_content="你是是什么",  metadata={"source": "https://example.com"}),
# Document(page_content="你是是什么",  metadata={"source": "https://example.com"}),
# Document(page_content="你是是什么",  metadata={"source": "https://example.com"}),
# Document(page_content="你是是什么",  metadata={"source": "https://example.com"}),
# Document(page_content="你是是什么",  metadata={"source": "https://example.com"}),
# Document(page_content="你是是什么",  metadata={"source": "https://example.com"}),
# Document(page_content="你是是什么",  metadata={"source": "https://example.com"}),
# Document(page_content="你是是什么",  metadata={"source": "https://example.com"}),
# Document(page_content="你是是什么",  metadata={"source": "https://example.com"})
# ]
# #进行切分
# splitTextSpliter = RecursiveCharacterTextSplitter(
#     chunk_size=1000,
#     chunk_overlap=200,
# )
# splicDockes = splitTextSpliter.split_documents(documents=Documents)
#文档数据


v = Chroma(persist_directory=pre,embedding_function=em)
re = v.as_retriever
# create_retrieval_chain()
# print(v.similarity_search_with_score("你好",k=1,filter={
#     "source":"https"
# }))
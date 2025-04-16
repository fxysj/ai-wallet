from typing import Any, Dict, Iterable

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from langchain_community.embeddings import DeterministicFakeEmbedding
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_elasticsearch import ElasticsearchRetriever
from langchain_openai import ChatOpenAI


def create_index(
    es_client: Elasticsearch,
    index_name: str,
    text_field: str,
    dense_vector_field: str,
    num_characters_field: str,
):
    es_client.indices.create(
        index=index_name,
        mappings={
            "properties": {
                text_field: {"type": "text"},
                dense_vector_field: {"type": "dense_vector"},
                num_characters_field: {"type": "integer"},
            }
        },
    )
def index_data(
    es_client: Elasticsearch,
    index_name: str,
    text_field: str,
    dense_vector_field: str,
    embeddings: Embeddings,
    texts: Iterable[str],
    refresh: bool = True,
) -> None:
    create_index(
        es_client, index_name, text_field, dense_vector_field, num_characters_field
    )
    vectors = embeddings.embed_documents(list(texts))

    requests = [
        {
            "_op_type": "index",
            "_index": index_name,
            "_id": i,
            text_field: text,
            dense_vector_field: vector,
            num_characters_field: len(text),
        }
        for i, (text, vector) in enumerate(zip(texts, vectors))
    ]
    bulk(es_client, requests)

    if refresh:
        es_client.indices.refresh(index=index_name)

    return len(requests)

def vector_query(search_query: str) -> Dict:
    vector = embeddings.embed_query(search_query)  # same embeddings as for indexing
    return {
        "knn": {
            "field": dense_vector_field,
            "query_vector": vector,
            "k": 5,
            "num_candidates": 10,
        }
    }

if __name__ == '__main__':
    es_url = "http://localhost:9200"
    es_client = Elasticsearch(hosts=[es_url])
    es_client.info()
    embeddings = DeterministicFakeEmbedding(size=3)
    index_name = "test-langchain-retriever"
    text_field = "text"
    dense_vector_field = "fake_embedding"
    num_characters_field = "num_characters"
    texts = [
        "foo",
        "bar",
        "world",
        "hello world",
        "hello",
        "foo bar",
        "bla bla foo",
    ]
    index_data(es_client, index_name, text_field, dense_vector_field, embeddings, texts)

    vector_retriever = ElasticsearchRetriever.from_es_params(
        index_name=index_name,
        body_func=vector_query,
        content_field=text_field,
        url=es_url,
    )
    # vector_retriever.invoke("foo")

    prompt = ChatPromptTemplate.from_template(
        """Answer the question based only on the context provided.

    Context: {context}

    Question: {question}"""
    )

    llm = ChatOpenAI(model="gpt-4o-mini")


    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)


    chain = (
            {"context": vector_retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
    )
    # 如果你想要更“口语化”地理解，可以想象这个流程像在流水线上：
    #
    # 用户提问 👉 检索知识库 👉 整理答案线索 👉 放入提问模版 👉 送去问大模型 👉 拿到回答并返回


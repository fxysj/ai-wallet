import hashlib
import os

from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance

from app.config import settings


class RagService:
    def __init__(self):
        self.path = "/tmp/langchain_qdrant"
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        print("Initializing RagService")
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-large",api_key=settings.OPENAI_API_KEY,base_url=settings.OPENAI_API_BASE_URL)
        self.client = QdrantClient(path=self.path)
        self.collection_name = "rag_tikee_collection"

        # 注意：防止重复创建 Collection
        if self.collection_name not in [col.name for col in self.client.get_collections().collections]:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=3072, distance=Distance.COSINE),
            )

        self.vector_store = QdrantVectorStore(
            client=self.client,
            collection_name=self.collection_name,
            embedding=self.embeddings,
        )

    async def load_url_and_ingest(self, url: str):
        """从用户提供的 URL 加载网页，切割并入库到向量数据库"""
        print(f"Loading URL: {url}")
        loader = WebBaseLoader(url)
        documents = loader.load()
        print(documents)

        print(f"Loaded {len(documents)} documents.")

        # 使用递归字符切分器，它会基于段落和句子进行切割
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,  # 每个块的大小
            chunk_overlap=50,  # 每个块之间的重叠部分
            length_function=len,  # 计算文本长度的函数
            separators=["\n\n", "\n", " "],  # 优先按段落、换行符和空格切割
        )
        split_docs = text_splitter.split_documents(documents)

        print(f"Split into {len(split_docs)} chunks.")

        # 入库到 Qdrant
        self.vector_store.add_documents(split_docs)

        print(f"Ingested {len(split_docs)} documents into Qdrant.")

        return {"message": "Success", "chunks": len(split_docs)}

    async def load_url_and_upsert(self, url: str):
        """从用户提供的 URL 加载网页，按块去重后批量入库"""
        print(f"Loading URL: {url}")
        loader = WebBaseLoader(url)
        documents = loader.load()

        print(f"Loaded {len(documents)} documents.")

        # 使用递归字符切分器，它会基于段落和句子进行切割
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,  # 每个块的大小
            chunk_overlap=50,  # 每个块之间的重叠部分
            length_function=len,  # 计算文本长度的函数
            separators=["\n\n", "\n", " "],  # 优先按段落、换行符和空格切割
        )
        split_docs = text_splitter.split_documents(documents)

        print(f"Split into {len(split_docs)} chunks.")

        processed = 0
        for doc in split_docs:
            text = doc.page_content.strip()
            if not text:
                continue

            # 生成当前文本块的 embedding
            embedding = self.embeddings.embed_query(text)

            # 在向量库里按向量搜索，找有没有相似的
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=embedding,
                limit=1,
                score_threshold=0.90,  # 相似度阈值，可以调
            )

            # 如果搜索到相似内容，需要先删除
            if search_result:
                point_id = search_result[0].id
                print(f"Found similar document, deleting point_id={point_id}")
                self.client.delete(
                    collection_name=self.collection_name,
                    points_selector={"points": [point_id]}
                )

            # 给每个文档生成一个唯一ID（比如用 hash）
            point_id = hashlib.md5(text.encode('utf-8')).hexdigest()

            # 新增
            self.vector_store.add_documents([doc], ids=[point_id])
            processed += 1

        print(f"Upserted {processed} documents into Qdrant.")
        return {"message": "Success", "upserted_chunks": processed}

    async def similarity_search(self, query: str, top_k: int = 4, score_threshold: float = 0.3):
        # 生成查询的向量
        matches = []
        try:

            # 使用相似度搜索
            results = self.vector_store.similarity_search(
                query=query,  # 查询文本
                k=top_k,  # 返回最相似的前 k 个文档
                score_threshold=None  # 设置得分阈值
            )
            print(f"Search results: {results}")
            for result in results:
                matches.append({"metadata":result.metadata})
        except Exception as e:
            print(f"Error during similarity search: {str(e)}")
            return {"message": "Search error", "matches": matches}

        return matches

    async def query(self, query_text: str, top_k: int = 5, score_threshold: float = 0.75):
        """
        根据用户输入的 query_text 查询相似文档
        :param query_text: 查询的文本
        :param top_k: 返回最相似的前 top_k 个文档
        :param score_threshold: 相似度得分阈值（1表示完全相同）
        :return: list of matched documents
        """
        if not query_text.strip():
            return {"message": "Query text cannot be empty", "matches": []}

        # 生成查询的 embedding
        embedding = self.embeddings.embed_query(query_text)

        # 调用 qdrant 进行向量搜索
        try:
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=embedding,
                limit=top_k,
                score_threshold=score_threshold,
                with_payload=True,  # 把存储的原文 payload 也取回来
            )
        except Exception as e:
            print(f"Error during search: {str(e)}")
            return {"message": "Search error", "matches": []}

        matches = []
        for result in search_results:
            payload = result.payload or {}
            page_content = payload.get('page_content', '')  # 看你的文档字段名字，这里是默认
            matches.append({
                "id": result.id,
                "score": result.score,
                "page_content": page_content,
            })

        return {
            "message": "Success",
            "matches": matches
        }



if __name__ == '__main__':
    rag_service = RagService()
    import asyncio
    # asyncio.run(rag_service.load_url_and_ingest("https://python.langchain.com/v0.2/docs/integrations/vectorstores/qdrant/"))
    asyncio.run(rag_service.similarity_search("Qdrant是什么"))



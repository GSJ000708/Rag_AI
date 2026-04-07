"""向量数据库服务"""
import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any
from app.config import get_settings
from app.core.embeddings import EmbeddingService
from loguru import logger
from rank_bm25 import BM25Okapi
import uuid
import os


class VectorDBService:
    """向量数据库服务"""

    def __init__(self):
        self.settings = get_settings()
        self.embedding_service = EmbeddingService()

        # 确保持久化目录存在
        os.makedirs(self.settings.chroma_persist_dir, exist_ok=True)

        # 初始化 Chroma 客户端（持久化模式）
        self.client = chromadb.PersistentClient(
            path=self.settings.chroma_persist_dir
        )

        # 获取或创建集合
        self.collection = self.client.get_or_create_collection(
            name=self.settings.chroma_collection_name,
            metadata={"hnsw:space": "cosine"}
        )

        # BM25 索引（内存中）
        self._bm25_corpus: List[List[str]] = []  # tokenized 文档
        self._bm25_docs: List[Dict[str, Any]] = []  # 原始文档和元数据
        self._bm25: BM25Okapi = None

        # 启动时从 ChromaDB 重建 BM25 索引
        self._rebuild_bm25_index()

        logger.info(f"VectorDB initialized: {self.settings.chroma_persist_dir}")

    # ------------------------------------------------------------------ #
    #  BM25 内部方法
    # ------------------------------------------------------------------ #

    def _tokenize(self, text: str) -> List[str]:
        """简单分词：按字符切分（兼容中文）"""
        return list(text.lower())

    def _rebuild_bm25_index(self):
        """从 ChromaDB 加载所有文档，重建 BM25 索引"""
        try:
            results = self.collection.get()
            if not results["documents"]:
                return
            self._bm25_corpus = [self._tokenize(doc) for doc in results["documents"]]
            self._bm25_docs = [
                {"content": results["documents"][i], "metadata": results["metadatas"][i]}
                for i in range(len(results["documents"]))
            ]
            self._bm25 = BM25Okapi(self._bm25_corpus)
            logger.info(f"BM25 index rebuilt: {len(self._bm25_corpus)} chunks")
        except Exception as e:
            logger.warning(f"BM25 index rebuild failed: {e}")

    def _update_bm25_index(self, texts: List[str], metadatas: List[Dict[str, Any]]):
        """增量更新 BM25 索引（新增文档时调用）"""
        for text, meta in zip(texts, metadatas):
            self._bm25_corpus.append(self._tokenize(text))
            self._bm25_docs.append({"content": text, "metadata": meta})
        if self._bm25_corpus:
            self._bm25 = BM25Okapi(self._bm25_corpus)

    def _bm25_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """BM25 检索，返回带排名的结果"""
        if not self._bm25 or not self._bm25_docs:
            return []
        tokenized_query = self._tokenize(query)
        scores = self._bm25.get_scores(tokenized_query)
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        return [
            {
                "content": self._bm25_docs[i]["content"],
                "metadata": self._bm25_docs[i]["metadata"],
                "bm25_score": float(scores[i]),
            }
            for i in top_indices
            if scores[i] > 0
        ]

    @staticmethod
    def _rrf_fusion(
        vector_results: List[Dict[str, Any]],
        bm25_results: List[Dict[str, Any]],
        k: int = 60,
        top_k: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        Reciprocal Rank Fusion（RRF）融合两个排序列表。
        score = Σ 1 / (k + rank)
        """
        rrf_scores: Dict[str, float] = {}
        doc_map: Dict[str, Dict[str, Any]] = {}

        for rank, doc in enumerate(vector_results, start=1):
            key = doc["content"]
            rrf_scores[key] = rrf_scores.get(key, 0) + 1 / (k + rank)
            doc_map[key] = doc

        for rank, doc in enumerate(bm25_results, start=1):
            key = doc["content"]
            rrf_scores[key] = rrf_scores.get(key, 0) + 1 / (k + rank)
            if key not in doc_map:
                doc_map[key] = doc

        sorted_keys = sorted(rrf_scores, key=lambda x: rrf_scores[x], reverse=True)[:top_k]
        results = []
        for key in sorted_keys:
            doc = dict(doc_map[key])
            doc["score"] = rrf_scores[key]
            results.append(doc)
        return results

    # ------------------------------------------------------------------ #
    #  公开方法
    # ------------------------------------------------------------------ #

    def add_documents(
        self,
        texts: List[str],
        metadatas: List[Dict[str, Any]],
        document_id: str,
    ) -> int:
        """添加文档到向量数据库"""
        try:
            ids = [f"{document_id}_{i}" for i in range(len(texts))]
            embeddings = self.embedding_service.embed_texts(texts)

            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
            )

            # 同步更新 BM25 索引
            self._update_bm25_index(texts, metadatas)

            logger.info(f"Added {len(texts)} chunks for document {document_id}")
            return len(texts)

        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise Exception(f"向量数据库添加失败: {str(e)}")

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        混合检索：向量语义检索 + BM25 关键词检索，RRF 融合排序。
        """
        try:
            fetch_k = top_k * 2  # 各自多取一些，融合后再截断

            # 1. 向量检索
            query_embedding = self.embedding_service.embed_text(query)
            raw = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=min(fetch_k, self.collection.count() or 1),
            )
            vector_results = []
            if raw["documents"] and raw["documents"][0]:
                for i in range(len(raw["documents"][0])):
                    vector_results.append({
                        "content": raw["documents"][0][i],
                        "metadata": raw["metadatas"][0][i],
                        "score": 1 - raw["distances"][0][i],
                    })

            # 2. BM25 检索
            bm25_results = self._bm25_search(query, top_k=fetch_k)

            # 3. RRF 融合
            if bm25_results:
                results = self._rrf_fusion(vector_results, bm25_results, top_k=top_k)
                logger.info(f"Hybrid search (vector={len(vector_results)}, bm25={len(bm25_results)}) -> {len(results)} results")
            else:
                results = vector_results[:top_k]
                logger.info(f"Vector-only search -> {len(results)} results")

            return results

        except Exception as e:
            logger.error(f"Search error: {e}")
            raise Exception(f"向量检索失败: {str(e)}")

    def delete_document(self, document_id: str) -> bool:
        """删除文档"""
        try:
            results = self.collection.get(where={"document_id": document_id})
            if results["ids"]:
                self.collection.delete(ids=results["ids"])
                logger.info(f"Deleted document {document_id} ({len(results['ids'])} chunks)")
                # 删除后重建 BM25 索引
                self._rebuild_bm25_index()
                return True
            else:
                logger.warning(f"Document {document_id} not found")
                return False

        except Exception as e:
            logger.error(f"Delete error: {e}")
            raise Exception(f"文档删除失败: {str(e)}")

    def get_all_documents(self) -> List[Dict[str, Any]]:
        """获取所有文档信息"""
        try:
            results = self.collection.get()
            docs_map = {}
            for i, metadata in enumerate(results["metadatas"]):
                doc_id = metadata.get("document_id")
                if doc_id not in docs_map:
                    docs_map[doc_id] = {
                        "document_id": doc_id,
                        "filename": metadata.get("filename", "unknown"),
                        "file_size": metadata.get("file_size", 0),
                        "upload_time": metadata.get("upload_time", ""),
                        "chunks_count": 0,
                    }
                docs_map[doc_id]["chunks_count"] += 1
            return list(docs_map.values())

        except Exception as e:
            logger.error(f"Get documents error: {e}")
            raise Exception(f"获取文档列表失败: {str(e)}")

    def get_collection_count(self) -> int:
        """获取集合中的文档数量"""
        try:
            return self.collection.count()
        except Exception:
            return 0

import json
import os

from app.database.connection import init_db
from app.database.models import IAKnowledge
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from sqlalchemy import text


class KnowledgeService:

    def __init__(self):
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="gemini-embedding-001",
            google_api_key=os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        )

    def _is_sqlite(self, db) -> bool:
        return db.get_bind().dialect.name == "sqlite"

    def _ensure_sqlite_table(self, db):
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS ia_knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ia_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                embedding TEXT NOT NULL
            )
        """))

    def add_chunk(self, ia_id: int, chunk: str):
        """Salva um chunk de texto com seu embedding no banco."""
        db = init_db()
        try:
            embedding = self.embeddings.embed_query(chunk)

            if self._is_sqlite(db):
                self._ensure_sqlite_table(db)
                db.execute(
                    text("""
                        INSERT INTO ia_knowledge (ia_id, content, embedding)
                        VALUES (:ia_id, :content, :embedding)
                    """),
                    {
                        "ia_id": ia_id,
                        "content": chunk,
                        "embedding": json.dumps(embedding),
                    }
                )
            else:
                knowledge = IAKnowledge(
                    ia_id=ia_id,
                    content=chunk,
                    embedding=embedding
                )
                db.add(knowledge)

            db.commit()

        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def similarity_search(self, ia_id: int, query: str, k: int = 5):
        db = init_db()
        try:
            if self._is_sqlite(db):
                self._ensure_sqlite_table(db)
                result = db.execute(
                    text("""
                        SELECT content
                        FROM ia_knowledge
                        WHERE ia_id = :ia_id
                          AND lower(content) LIKE :query
                        ORDER BY id DESC
                        LIMIT :k
                    """),
                    {
                        "ia_id": ia_id,
                        "query": f"%{query.lower()}%",
                        "k": k,
                    }
                ).fetchall()

                if not result:
                    result = db.execute(
                        text("""
                            SELECT content
                            FROM ia_knowledge
                            WHERE ia_id = :ia_id
                            ORDER BY id DESC
                            LIMIT :k
                        """),
                        {"ia_id": ia_id, "k": k}
                    ).fetchall()

                return [row.content for row in result]

            query_embedding = self.embeddings.embed_query(query)

            sql = text("""
            WITH semantic_search AS (

                SELECT
                    id,
                    content,

                    1 - (
                        embedding <=> CAST(:embedding AS vector)
                    ) AS semantic_score

                FROM ia_knowledge

                WHERE ia_id = :ia_id

                ORDER BY embedding <=> CAST(:embedding AS vector)

                LIMIT 50
            ),

            keyword_search AS (

                SELECT
                    id,

                    ts_rank(
                        content_tsv,
                        plainto_tsquery(
                            'portuguese',
                            :query
                        )
                    ) AS keyword_score

                FROM ia_knowledge

                WHERE ia_id = :ia_id

                ORDER BY keyword_score DESC

                LIMIT 50
            )

            SELECT
                s.content,

                (
                    0.7 * s.semantic_score +
                    0.3 * COALESCE(
                        k.keyword_score,
                        0
                    )
                ) AS final_score

            FROM semantic_search s

            LEFT JOIN keyword_search k
                ON s.id = k.id

            ORDER BY final_score DESC

            LIMIT :k
            """)

            result = db.execute(
                sql,
                {
                    "embedding": query_embedding,
                    "query": query,
                    "ia_id": ia_id,
                    "k": k
                }
            )

            return [row.content for row in result]

        finally:
            db.close()

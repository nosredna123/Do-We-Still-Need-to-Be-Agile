import axios from "axios";
import { prisma } from "../database/index.js";
import { pool } from "../config/pgvector.js";
import { registerType, toSql } from "pgvector/pg";

export class ChunkService {

    // ---------- (A) Fazer embedding da query usando Flask ----------
    async embedQuery(query: string): Promise<number[]> {
        const resp = await axios.post("http://127.0.0.1:5000/embed", {
            text: query
        });

        return resp.data.results; // array de floats
    }

    // ---------- (B) Busca vetorial ----------
    async searchRelevantChunks(query: string, topicId: number, k = 5) {
        const vector = await this.embedQuery(query);

        const client = await pool.connect();
        try {
            registerType(client);

            const result = await client.query(
            `
            SELECT 
                e.chunk_id,
                mc.text,
                mc.index AS chunk_index,
                (e.embedding <-> $1) AS distance
            FROM embeddings."MaterialEmbedding" e
            JOIN embeddings."MaterialChunk" mc 
                ON mc.id = e.chunk_id
            JOIN public."Transcript" t
                ON t.id = mc.transcript_id
            WHERE t."topicId" = $2
            ORDER BY e.embedding <-> $1
            LIMIT $3;
            `,
            [toSql(vector), topicId, k]
        );

            let context = ""
            result.rows.forEach((row) => {
                context += row.text
            })
            return context;

        } finally {
            client.release();
        }
    }


    // ---------- (1) Buscar transcrições do tópico ----------
    async getTranscriptsByTopic(topicId: number) {
        return prisma.transcript.findMany({
            where: { topicId: topicId },
        });
    }

    // ---------- (2) Chunking ----------
    chunkText(text: string, maxTokens = 350): string[] {
        // chunk simples baseado em tamanho
        const words = text.split(" ");
        const chunks: string[] = [];
        let current = [];

        for (const w of words) {
            current.push(w);
            if (current.join(" ").length > maxTokens) {
                chunks.push(current.join(" "));
                current = [];
            }
        }
        if (current.length > 0) chunks.push(current.join(" "));

        return chunks;
    }

    // ---------- (3) Mandar chunk para o Flask gerar embedding ----------
    async getEmbeddingFromFlask(chunk: string): Promise<number[]> {
        console.log(chunk)
        const resp = await axios.post("http://127.0.0.1:5000/embed", {
            text: chunk
        });
        return resp.data.results;
    }

    // ---------- (4) Salvar chunk ----------
    async saveChunk(transcript_id: number, chunk: string, index: number) {
        return prisma.materialChunk.create({
            data: {
                transcript_id: transcript_id,
                text: chunk,
                index
            }
        });
    }

    // ---------- (5) Salvar embedding ----------
    async saveEmbedding(chunkId: number, embedding: number[]) {
        const client = await pool.connect();

    try {
        // registre o pgvector neste client
        registerType(client);

        await client.query(
        `INSERT INTO embeddings."MaterialEmbedding" (chunk_id, embedding)
        VALUES ($1, $2)`,
        [chunkId, toSql(embedding)]
        );
        } finally {
            client.release();
        }
    }

    // ---------- (6) Pipeline completo ----------
    async processTranscripts(topicId: number) {
        const transcripts = await this.getTranscriptsByTopic(topicId);

        const results = [];

        for (const t of transcripts) {
            const chunks = this.chunkText(t.content);

            for (let i = 0; i < chunks.length; i++) {
                const chunkText = String(chunks[i]);

                const createdChunk = await this.saveChunk(t.id, chunkText, i);

                const embedding = await this.getEmbeddingFromFlask(chunkText);

                const createdEmbedding = await this.saveEmbedding(
                    createdChunk.id,
                    embedding
                );

                results.push({
                    chunk: createdChunk,
                    embedding: createdEmbedding
                });
            }
        }

        return results;
    }
}

export const chunkService = new ChunkService();
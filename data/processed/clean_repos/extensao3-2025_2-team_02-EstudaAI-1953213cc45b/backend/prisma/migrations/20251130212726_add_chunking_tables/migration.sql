-- CreateSchema
CREATE SCHEMA IF NOT EXISTS "embeddings";

-- CreateTable
CREATE TABLE "embeddings"."MaterialChunk" (
    "id" SERIAL NOT NULL,
    "transcript_id" INTEGER NOT NULL,
    "index" INTEGER NOT NULL,
    "text" TEXT NOT NULL,

    CONSTRAINT "MaterialChunk_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "embeddings"."MaterialEmbedding" (
    "id" SERIAL NOT NULL,
    "chunk_id" INTEGER NOT NULL,
    "embedding" vector(384) NOT NULL,

    CONSTRAINT "MaterialEmbedding_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "MaterialEmbedding_chunk_id_key" ON "embeddings"."MaterialEmbedding"("chunk_id");

-- AddForeignKey
ALTER TABLE "embeddings"."MaterialChunk" ADD CONSTRAINT "MaterialChunk_transcript_id_fkey" FOREIGN KEY ("transcript_id") REFERENCES "public"."Transcript"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "embeddings"."MaterialEmbedding" ADD CONSTRAINT "MaterialEmbedding_chunk_id_fkey" FOREIGN KEY ("chunk_id") REFERENCES "embeddings"."MaterialChunk"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

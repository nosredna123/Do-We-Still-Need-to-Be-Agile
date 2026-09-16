/*
  Warnings:

  - A unique constraint covering the columns `[material_id]` on the table `Transcript` will be added. If there are existing duplicate values, this will fail.
  - Added the required column `material_id` to the `Transcript` table without a default value. This is not possible if the table is not empty.

*/
-- AlterTable
ALTER TABLE "Transcript" ADD COLUMN     "material_id" INTEGER NOT NULL;

-- CreateIndex
CREATE UNIQUE INDEX "Transcript_material_id_key" ON "Transcript"("material_id");

-- AddForeignKey
ALTER TABLE "Transcript" ADD CONSTRAINT "Transcript_material_id_fkey" FOREIGN KEY ("material_id") REFERENCES "Material"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

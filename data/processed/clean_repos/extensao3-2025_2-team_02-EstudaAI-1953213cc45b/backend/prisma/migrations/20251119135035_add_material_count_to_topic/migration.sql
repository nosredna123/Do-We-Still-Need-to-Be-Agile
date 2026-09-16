/*
  Warnings:

  - Added the required column `material_count` to the `Topic` table without a default value. This is not possible if the table is not empty.

*/
-- AlterTable
ALTER TABLE "Topic" ADD COLUMN     "material_count" INTEGER NOT NULL;

/*
  Warnings:

  - Added the required column `order_index` to the `StudyPlanChecklistItem` table without a default value. This is not possible if the table is not empty.

*/
-- AlterTable
ALTER TABLE "StudyPlanChecklistItem" ADD COLUMN     "order_index" INTEGER NOT NULL;

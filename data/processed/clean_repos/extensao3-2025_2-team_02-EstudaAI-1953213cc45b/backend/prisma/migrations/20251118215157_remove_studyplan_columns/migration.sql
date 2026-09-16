/*
  Warnings:

  - You are about to drop the column `complementary_materials` on the `StudyPlan` table. All the data in the column will be lost.
  - You are about to drop the column `justifications` on the `StudyPlan` table. All the data in the column will be lost.
  - You are about to drop the column `roadmap` on the `StudyPlan` table. All the data in the column will be lost.

*/
-- AlterTable
ALTER TABLE "StudyPlan" DROP COLUMN "complementary_materials",
DROP COLUMN "justifications",
DROP COLUMN "roadmap";

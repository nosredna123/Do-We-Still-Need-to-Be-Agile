/*
  Warnings:

  - Made the column `title` on table `Topic` required. This step will fail if there are existing NULL values in that column.

*/
-- AlterTable
ALTER TABLE "Reminder" ALTER COLUMN "due_date" DROP NOT NULL;

-- AlterTable
ALTER TABLE "Topic" ALTER COLUMN "title" SET NOT NULL,
ALTER COLUMN "title" SET DEFAULT '';

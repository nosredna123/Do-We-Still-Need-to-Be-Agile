/*
  Warnings:

  - You are about to drop the column `discipline_id` on the `Topic` table. All the data in the column will be lost.
  - You are about to drop the `Discipline` table. If the table is not empty, all the data it contains will be lost.
  - Added the required column `subject_id` to the `Topic` table without a default value. This is not possible if the table is not empty.

*/
-- DropForeignKey
ALTER TABLE "public"."Discipline" DROP CONSTRAINT "Discipline_userId_fkey";

-- DropForeignKey
ALTER TABLE "public"."Topic" DROP CONSTRAINT "Topic_discipline_id_fkey";

-- AlterTable
ALTER TABLE "Topic" DROP COLUMN "discipline_id",
ADD COLUMN     "subject_id" INTEGER NOT NULL;

-- DropTable
DROP TABLE "public"."Discipline";

-- CreateTable
CREATE TABLE "Subject" (
    "id" SERIAL NOT NULL,
    "userId" INTEGER NOT NULL,
    "name" TEXT NOT NULL,

    CONSTRAINT "Subject_pkey" PRIMARY KEY ("id")
);

-- AddForeignKey
ALTER TABLE "Subject" ADD CONSTRAINT "Subject_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Topic" ADD CONSTRAINT "Topic_subject_id_fkey" FOREIGN KEY ("subject_id") REFERENCES "Subject"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

/*
  Warnings:

  - You are about to drop the `StudyPlanChecklist` table. If the table is not empty, all the data it contains will be lost.

*/
-- DropForeignKey
ALTER TABLE "public"."StudyPlanChecklist" DROP CONSTRAINT "StudyPlanChecklist_plan_id_fkey";

-- DropTable
DROP TABLE "public"."StudyPlanChecklist";

-- CreateTable
CREATE TABLE "StudyPlanChecklistItem" (
    "id" SERIAL NOT NULL,
    "plan_id" INTEGER NOT NULL,
    "title" VARCHAR(30) NOT NULL,
    "description" VARCHAR(30) NOT NULL,
    "completed" BOOLEAN NOT NULL DEFAULT false,

    CONSTRAINT "StudyPlanChecklistItem_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "StudyPlanChecklistItem_plan_id_key" ON "StudyPlanChecklistItem"("plan_id");

-- AddForeignKey
ALTER TABLE "StudyPlanChecklistItem" ADD CONSTRAINT "StudyPlanChecklistItem_plan_id_fkey" FOREIGN KEY ("plan_id") REFERENCES "StudyPlan"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- CreateTable
CREATE TABLE "StudyPlanChecklist" (
    "id" SERIAL NOT NULL,
    "plan_id" INTEGER NOT NULL,
    "title" VARCHAR(30) NOT NULL,
    "description" VARCHAR(30) NOT NULL,
    "completed" BOOLEAN NOT NULL DEFAULT false,

    CONSTRAINT "StudyPlanChecklist_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "StudyPlanChecklist_plan_id_key" ON "StudyPlanChecklist"("plan_id");

-- AddForeignKey
ALTER TABLE "StudyPlanChecklist" ADD CONSTRAINT "StudyPlanChecklist_plan_id_fkey" FOREIGN KEY ("plan_id") REFERENCES "StudyPlan"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

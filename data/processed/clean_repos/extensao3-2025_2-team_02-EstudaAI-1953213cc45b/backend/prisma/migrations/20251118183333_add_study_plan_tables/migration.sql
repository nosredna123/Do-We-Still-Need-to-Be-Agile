-- CreateTable
CREATE TABLE "StudyPlan" (
    "id" SERIAL NOT NULL,
    "userId" INTEGER NOT NULL,
    "discipline_id" INTEGER NOT NULL,
    "title" TEXT NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "roadmap" TEXT NOT NULL,
    "justifications" TEXT NOT NULL,
    "complementary_materials" TEXT NOT NULL,

    CONSTRAINT "StudyPlan_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "StudyPlanTopics" (
    "id" SERIAL NOT NULL,
    "plan_id" INTEGER NOT NULL,
    "title" TEXT NOT NULL,
    "order_index" INTEGER NOT NULL,

    CONSTRAINT "StudyPlanTopics_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "StudyPlanExpanded" (
    "id" SERIAL NOT NULL,
    "plan_id" INTEGER NOT NULL,
    "topic_title" VARCHAR(50) NOT NULL,
    "justification" VARCHAR(100) NOT NULL,
    "order_index" INTEGER NOT NULL,

    CONSTRAINT "StudyPlanExpanded_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "StudyPlanComplementary" (
    "id" SERIAL NOT NULL,
    "plan_id" INTEGER NOT NULL,
    "topic_title" VARCHAR(50) NOT NULL,
    "description" VARCHAR(100) NOT NULL,
    "order_index" INTEGER NOT NULL,

    CONSTRAINT "StudyPlanComplementary_pkey" PRIMARY KEY ("id")
);

-- AddForeignKey
ALTER TABLE "StudyPlan" ADD CONSTRAINT "StudyPlan_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "StudyPlan" ADD CONSTRAINT "StudyPlan_discipline_id_fkey" FOREIGN KEY ("discipline_id") REFERENCES "Subject"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "StudyPlanTopics" ADD CONSTRAINT "StudyPlanTopics_plan_id_fkey" FOREIGN KEY ("plan_id") REFERENCES "StudyPlan"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "StudyPlanExpanded" ADD CONSTRAINT "StudyPlanExpanded_plan_id_fkey" FOREIGN KEY ("plan_id") REFERENCES "StudyPlan"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "StudyPlanComplementary" ADD CONSTRAINT "StudyPlanComplementary_plan_id_fkey" FOREIGN KEY ("plan_id") REFERENCES "StudyPlan"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

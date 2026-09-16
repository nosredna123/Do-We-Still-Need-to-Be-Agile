-- DropForeignKey
ALTER TABLE "public"."Material" DROP CONSTRAINT "Material_topic_id_fkey";

-- DropForeignKey
ALTER TABLE "public"."StudyPlan" DROP CONSTRAINT "StudyPlan_discipline_id_fkey";

-- DropForeignKey
ALTER TABLE "public"."StudyPlanChecklist" DROP CONSTRAINT "StudyPlanChecklist_plan_id_fkey";

-- DropForeignKey
ALTER TABLE "public"."StudyPlanComplementary" DROP CONSTRAINT "StudyPlanComplementary_plan_id_fkey";

-- DropForeignKey
ALTER TABLE "public"."StudyPlanExpanded" DROP CONSTRAINT "StudyPlanExpanded_plan_id_fkey";

-- DropForeignKey
ALTER TABLE "public"."StudyPlanTopics" DROP CONSTRAINT "StudyPlanTopics_plan_id_fkey";

-- DropForeignKey
ALTER TABLE "public"."Summary" DROP CONSTRAINT "Summary_topic_id_fkey";

-- DropForeignKey
ALTER TABLE "public"."Topic" DROP CONSTRAINT "Topic_subject_id_fkey";

-- DropForeignKey
ALTER TABLE "public"."Transcript" DROP CONSTRAINT "Transcript_material_id_fkey";

-- DropForeignKey
ALTER TABLE "public"."Transcript" DROP CONSTRAINT "Transcript_topicId_fkey";

-- AddForeignKey
ALTER TABLE "Topic" ADD CONSTRAINT "Topic_subject_id_fkey" FOREIGN KEY ("subject_id") REFERENCES "Subject"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Summary" ADD CONSTRAINT "Summary_topic_id_fkey" FOREIGN KEY ("topic_id") REFERENCES "Topic"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Material" ADD CONSTRAINT "Material_topic_id_fkey" FOREIGN KEY ("topic_id") REFERENCES "Topic"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Transcript" ADD CONSTRAINT "Transcript_material_id_fkey" FOREIGN KEY ("material_id") REFERENCES "Material"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Transcript" ADD CONSTRAINT "Transcript_topicId_fkey" FOREIGN KEY ("topicId") REFERENCES "Topic"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "StudyPlan" ADD CONSTRAINT "StudyPlan_discipline_id_fkey" FOREIGN KEY ("discipline_id") REFERENCES "Subject"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "StudyPlanTopics" ADD CONSTRAINT "StudyPlanTopics_plan_id_fkey" FOREIGN KEY ("plan_id") REFERENCES "StudyPlan"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "StudyPlanExpanded" ADD CONSTRAINT "StudyPlanExpanded_plan_id_fkey" FOREIGN KEY ("plan_id") REFERENCES "StudyPlan"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "StudyPlanComplementary" ADD CONSTRAINT "StudyPlanComplementary_plan_id_fkey" FOREIGN KEY ("plan_id") REFERENCES "StudyPlan"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "StudyPlanChecklist" ADD CONSTRAINT "StudyPlanChecklist_plan_id_fkey" FOREIGN KEY ("plan_id") REFERENCES "StudyPlan"("id") ON DELETE CASCADE ON UPDATE CASCADE;

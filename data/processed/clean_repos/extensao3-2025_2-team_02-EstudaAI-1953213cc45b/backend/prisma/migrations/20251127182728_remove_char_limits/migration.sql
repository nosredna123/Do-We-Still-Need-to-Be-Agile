-- AlterTable
ALTER TABLE "StudyPlanChecklistItem" ALTER COLUMN "title" SET DATA TYPE TEXT,
ALTER COLUMN "description" SET DATA TYPE TEXT;

-- AlterTable
ALTER TABLE "StudyPlanComplementary" ALTER COLUMN "topic_title" SET DATA TYPE TEXT,
ALTER COLUMN "description" SET DATA TYPE TEXT;

-- AlterTable
ALTER TABLE "StudyPlanExpanded" ALTER COLUMN "topic_title" SET DATA TYPE TEXT,
ALTER COLUMN "justification" SET DATA TYPE TEXT;

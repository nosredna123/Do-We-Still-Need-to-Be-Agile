import express from "express"

import { addChecklistItem, chat, createReminder, createStudyPlan, createSubject, createTopic, deleteChecklistItem, deleteMaterial, deleteReminder, deleteStudyPlan, deleteSubject, deleteTopic, editChecklistItem, editReminder, getAISummaryAndReminders, getReminders, getStudyPlan, getStudyPlans, getSubjects, getSubjectTopics, loadMessages, markChecklistItem, registerStudent, sendMaterialsToLLMAndSaveTranscripts, sendTranscriptsForStudyPlan, topicMaterials, topicMessages, topicSummaries, uploadMaterials } from "../controllers/student.controller.js";
import { authMiddleware } from "../middlewares/authmiddleware.js";
import { upload } from "../config/multer.js";
import { getRelevantChunks, processChunksAndEmbeddings } from "../controllers/chunks.controller.js";

const studentRouter = express.Router();

studentRouter.post("/register", registerStudent);
studentRouter.get("/reminders", authMiddleware, getReminders)
studentRouter.post("/reminders/create", authMiddleware, createReminder)
studentRouter.delete("/reminders/delete", authMiddleware, deleteReminder)
studentRouter.put("/reminders/edit", authMiddleware, editReminder)
studentRouter.post("/subjects/create", authMiddleware, createSubject)
studentRouter.get("/subjects", authMiddleware, getSubjects)
studentRouter.post("/llm/generate", authMiddleware, getAISummaryAndReminders)
studentRouter.post("/materials/upload", authMiddleware, upload.array("files"), uploadMaterials)
studentRouter.delete("/materials/delete", authMiddleware, deleteMaterial)
studentRouter.post("/llm/materials/send", authMiddleware, sendMaterialsToLLMAndSaveTranscripts)
studentRouter.post("/llm/transcripts/send", authMiddleware, sendTranscriptsForStudyPlan)
studentRouter.get("/subjects/topics", authMiddleware, getSubjectTopics)
studentRouter.post("/studyplans/create", authMiddleware, createStudyPlan)
studentRouter.delete("/studyplans/delete", authMiddleware, deleteStudyPlan)
studentRouter.post("/topics/create", authMiddleware, createTopic)
studentRouter.delete("/topics/delete", authMiddleware, deleteTopic)
studentRouter.get("/studyplans", authMiddleware, getStudyPlans)
studentRouter.get("/studyplan", authMiddleware, getStudyPlan)
studentRouter.put("/studyplan/checklist/edit", authMiddleware, editChecklistItem)
studentRouter.put("/studyplan/checklist/mark", authMiddleware, markChecklistItem)
studentRouter.post("/llm/embed", authMiddleware, processChunksAndEmbeddings)
studentRouter.post("/studyplan/checklist/add", authMiddleware, addChecklistItem)
studentRouter.delete("/studyplan/checklist/delete", authMiddleware, deleteChecklistItem)
// topic transcripts
studentRouter.get("/topic/materials", authMiddleware, topicMaterials)
studentRouter.get("/topic/summaries", authMiddleware, topicSummaries)
studentRouter.get("/topic/messages", authMiddleware, topicMessages)
studentRouter.post("/llm/chat", authMiddleware, getRelevantChunks)
studentRouter.get("/topic/messages", authMiddleware, loadMessages)
studentRouter.delete("/subject/delete", authMiddleware, deleteSubject)

export default studentRouter
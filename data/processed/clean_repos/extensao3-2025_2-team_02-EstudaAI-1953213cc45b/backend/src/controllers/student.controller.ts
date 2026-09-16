import type { NextFunction, Request, Response } from "express"
import { CreateReminderSchema, CreateUserRequestSchema } from "../schemas/UsersRequestSchema.js"
import { studentService } from "../services/student.service.js"
import { userService } from "../services/user.service.js"
import axios from "axios"

export const registerStudent = async (req: Request, res: Response, next: NextFunction) => {
    try {
        const body = CreateUserRequestSchema.parse(req.body)
        const newStudent = await studentService.registerService(body)
        res.status(201).json(newStudent)
    } catch (error) {
        next(error)
    }
}

export const loginUser = async (req: Request, res: Response, next: NextFunction) => {
    try {
        const { email, password } = req.body

        const user = await userService.loginService(email, password)
        const acessToken = await userService.getAcessToken(user.id, user.role)
        const userId = user.id
        const userRole = user.role
        res.status(200).json({
            id: user.id,
            name: user.name,
            email: user.email,
            role: user.role,
            acessToken
          })
        
    } catch (error) {
        next(error) 
    }
}

export const getReminders = async (req: Request, res: Response, next: NextFunction) => {
    try {
        // console.log(req.auth?.id)
        const userId = Number(req.auth?.id)
        // console.log(userId)
        const reminders = await studentService.getRemindersService(userId)
        res.status(200).json(reminders)
    } catch (error) {
        next(error)
    }
}

export const createReminder = async (req: Request, res: Response, next: NextFunction) => {
    try {
        const userId = Number(req.auth?.id)
        const { title, description, due_date } = CreateReminderSchema.parse(req.body)
        const reminderData: Lembrete = {
            titulo: title,
            descricao: description
          };
        if (due_date) {
            reminderData.data = new Date(due_date);
        }
        const reminder = await studentService.createReminderService(userId, reminderData)
        res.status(201).json(reminder)
    } catch (error) {
        next(error)
    }
}

export const createReminderAlt = async (req: Request, res: Response, next: NextFunction) => {
    try {
        const userId = Number(req.auth?.id)
        const { title, description, due_date } = CreateReminderSchema.parse(req.body.l)
        const reminderData: Lembrete = {
            titulo: title,
            descricao: description
          };
        if (due_date) {
            reminderData.data = new Date(due_date);
        }
        const reminder = await studentService.createReminderService(userId, reminderData)
        res.status(201).json(reminder)
    } catch (error) {
        next(error)
    }
}

export const createSubject = async (req: Request, res: Response, next: NextFunction) => {
    try {
        const userId = Number(req.auth?.id)
        const { name } = req.body
        const subject = await studentService.createSubjectService(userId, name)
        res.status(201).json(subject)
    } catch (error) {
        next(error)
    }
}

export const getSubjects = async (req: Request, res: Response, next: NextFunction) => {
    try {
        const userId = Number(req.auth?.id)
        const subjects = await studentService.getSubjectsService(userId)
        res.status(201).json(subjects)
    } catch (error) {
        next(error)
    }
}

export const getAISummaryAndReminders = async (req: Request, res: Response, next: NextFunction) => {
    try {
        const userId = Number(req.auth?.id)
        const topicId = Number(req.body.topicId)
        const transcripts = await studentService.getTranscripts([topicId])
        console.log(transcripts[0])
        const aiResponse = await axios.post("http://127.0.0.1:5000/generate", transcripts[0])
        // res.status(200).json(aiResponse)

        const result = await studentService.processSummaryRemindersJSON(userId, topicId, aiResponse.data)
        res.status(200).json(result)
    } catch (error) {
        next(error)
    }
}

export const createSummary = async (req: Request, res: Response, next: NextFunction) => {
    try {
        const data = req.body.aiResponse.resumo
        const topicId = req.body.topicId
        const summary = await studentService.createSummaryService(topicId, data)
        res.status(201).json(summary)
    } catch (error) {
        next(error)
    }
}

export const createTopic = async (req: Request, res: Response, next: NextFunction) => {
    try {
        const subjectId = Number(req.body.subjectId)
        const title = req.body.title
        const topic = await studentService.createTopic(subjectId, title)
        res.status(201).json(topic)
    } catch (error) {
        next(error)
    }
}

export const uploadMaterials = async (req: Request, res: Response, next: NextFunction) => {
    try {
        const files = req.files as Express.Multer.File[]
        const userId = Number(req.auth?.id)
        const topicId = Number(req.body.topicId)

        if (!files || files.length === 0) {
            return res.status(400).json({ error: "Nenhum arquivo enviado" })
        }

        const uploads = await studentService.uploadMaterialsService(userId, topicId, files)
        res.status(201).json(uploads)
    } catch (error) {
        next(error)
    }
}

export const sendMaterialsToLLMAndSaveTranscripts = async (req: Request, res: Response, next: NextFunction) => {
    try {
        const topicId = Number(req.body.topicId)
        const materialUrls = await studentService.getTopicMaterials(topicId)
        const transcripts = await axios.post("http://127.0.0.1:5000/transcript", materialUrls)
        // console.log(transcripts.data.results)
        const createdTranscripts = await studentService.saveTranscripts(transcripts.data.results, topicId)
        res.status(200).json({materialUrls, transcripts: createdTranscripts})
    } catch (error) {
        next(error)
    }
}

export const sendTranscriptsForStudyPlan = async (req: Request, res: Response, next: NextFunction) => {
    try {
        const topicIds = req.body.topicIds
        const transcripts = await studentService.getTranscripts(topicIds)
        const studyplan = await axios.post("http://127.0.0.1:5000/studyplan", transcripts)
        res.status(201).json(studyplan.data)
    } catch (error) {
        next(error)
    }
}

export const getStudyPlans = async (req: Request, res: Response, next: NextFunction) => {
    try {
        const subjectId = Number(req.query.subjectId)
        const studyPlans = await studentService.getStudyPlans(subjectId)
        res.status(200).json(studyPlans)
    } catch (error) {
        next(error)
    }
}

export const getStudyPlan = async (req: Request, res: Response, next: NextFunction) => {
    try {
        const studyPlanId = Number(req.query.id)
        const studyPlan = await studentService.getStudyPlan(studyPlanId)
        res.status(200).json(studyPlan)
    } catch (error) {
        next(error)
    }
}

export const deleteMaterial = async (req: Request, res: Response, next: NextFunction) => {
    try {
        const materialId = Number(req.query.materialId)
        const topicId = Number(req.query.topicId)
        const material = await studentService.deleteMaterial(materialId, topicId)
        res.status(200).json(material)
    } catch (error) {
        next(error)
    }
}

export const deleteTopic = async (req: Request, res: Response, next: NextFunction) => {
    try {
        const topicId = Number(req.query.id)
        const deletedTopic = await studentService.deleteTopic(topicId)
        res.status(200).json(deletedTopic)
    } catch (error) {
        next(error)
    }
}

export const topicSummaries = async (req: Request, res: Response, next: NextFunction) => {
    try {
        const topicId = Number(req.query.topicId)
        const summaries = await studentService.topicSummaries(topicId)
        res.status(200).json(summaries)
    } catch (error) {
        next(error)
    }
}

export const topicMaterials = async (req: Request, res: Response, next: NextFunction) => {
    try {
        const topicId = Number(req.query.topicId)
        const materials = await studentService.getTopicMaterials(topicId)
        res.status(200).json(materials)
    } catch (error) {
        next(error)
    }
}

export const topicMessages = async (req: Request, res: Response, next: NextFunction) => {
    try {
        const topicId = Number(req.query.topicId)
        const messages = await studentService.topicMessages(topicId)
        res.status(200).json(messages)
    } catch (error) {
        next(error)
    }
}

export const editReminder = async (req: Request, res: Response, next: NextFunction) => {
    try {
        const reminderId = Number(req.body.id)
        const data: Lembrete = {
            titulo: req.body.title,
            descricao: req.body.description,
            data: req.body.due_date
        }
        const reminder = await studentService.editReminder(reminderId, data)
        res.status(200).json(reminder)
    } catch (error) {
        next(error)
    }
}

export const deleteReminder = async (req: Request, res: Response, next: NextFunction) => {
    try {
        const reminderId = Number(req.query.id)
        const deletedReminder = await studentService.deleteReminder(reminderId)
        res.status(200).json(deletedReminder)
    } catch (error) {
        next(error)
    }
}
// delete lembrete

export const createStudyPlan = async (req: Request, res: Response, next: NextFunction) => {
    const {
        subjectId,
        planData
    } = req.body

    const userId = Number(req.auth?.id)
    const result = await studentService.processStudyPlanJSON(planData, userId, subjectId)

    res.status(201).json(result)
}

export const deleteStudyPlan = async (req: Request, res: Response, next: NextFunction) => {
    const planId = Number(req.query.planId)

    const deletedPlan = await studentService.deleteStudyPlan(planId)
    res.status(200).json(deletedPlan)
}

export const editChecklistItem = async (req: Request, res: Response, next: NextFunction) => {
    const checklistItemId = Number(req.body.itemId)
    const data = {
        title: req.body.title,
        description: req.body.description
    }
    const editedItem = await studentService.editChecklistItem(checklistItemId, data)
    res.status(200).json(editedItem)
}

export const markChecklistItem = async (req: Request, res: Response, next: NextFunction) => {
    const itemId = Number(req.query.itemId)
    const item = await studentService.markChecklistItem(itemId)
    res.status(200).json(item)
}

export const getSubjectTopics = async (req: Request, res: Response, next: NextFunction) => {
    try {
        const subjectId = Number(req.query.subjectId)
        // console.log(subjectId)
        const topics = await studentService.getSubjectTopics(subjectId)
        res.status(200).json(topics)
    } catch (error) {
        next(error)
    }
}

export const chat = async (req: Request, res: Response, next: NextFunction) => {
    try {
        const message = req.body.message
        const response = axios.post("http://127.0.0.1:5000/chat", message)
        res.status(200).json(response)
    } catch (error) {
        next(error)
    }
}

export const loadMessages = async (req: Request, res: Response, next: NextFunction) => {
    try {
        const topicId = Number(req.query.topicId)
        const messages = await studentService.loadMessages(topicId)
        res.status(200).json(messages)
    } catch (error) {
        next(error)
    }
}

export const addChecklistItem = async (req: Request, res: Response, next: NextFunction) => {
    try {
        const planId = Number(req.body.planId)
        const description = req.body.description
        const title = req.body.title
        const newItem = await studentService.addChecklistItem(planId, title, description)
        res.status(200).json(newItem)
    } catch (error) {
        next(error)
    }
}

export const deleteChecklistItem = async (req: Request, res: Response, next: NextFunction) => {
    try {
        const itemId = Number(req.query.itemId)
        const deletedItem = await studentService.deleteChecklistItem(itemId)
        res.status(200).json(deletedItem)
    } catch (error) {
        next(error)
    }
}

export const deleteSubject = async (req: Request, res: Response, next: NextFunction) => {
    try {
        const subjectId = Number(req.query.subjectId)
        const deletedSubject = await studentService.deleteSubject(subjectId)
        res.status(200).json(deletedSubject)
    } catch (error) {
        next(error)
    }
}
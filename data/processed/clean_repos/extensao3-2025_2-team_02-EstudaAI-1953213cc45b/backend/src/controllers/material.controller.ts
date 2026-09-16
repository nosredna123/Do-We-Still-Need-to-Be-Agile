import type { Request, Response, NextFunction } from "express"
import { materialService } from "../services/material.service.js"


export const uploadMaterials = async (req: Request, res: Response, next: NextFunction) => {
    try {
        const files = req.files as Express.Multer.File[]
        const userId = Number(req.auth?.id)
        const topicId = Number(req.body.topicId)

        if (!files || files.length === 0) {
            return res.status(400).json({ error: "Nenhum arquivo enviado" })
        }

        const uploads = await materialService.uploadMaterialsService(userId, topicId, files)
        res.status(201).json(uploads)
    } catch (error) {
        next(error)
    }
}
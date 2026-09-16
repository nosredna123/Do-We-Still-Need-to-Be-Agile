import express from "express"
import { upload } from "../config/multer.js"
import { authMiddleware } from "../middlewares/authmiddleware.js"
import { uploadMaterials } from "../controllers/material.controller.js"

const materialRouter = express.Router()

materialRouter.post("/upload", authMiddleware, upload.array("files"), uploadMaterials)

export default materialRouter
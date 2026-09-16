import { prisma } from "./database/index.js"
import { Router } from "express"
import userRouter from "./routes/user.routes.js"
import studentRouter from "./routes/student.routes.js"
import materialRouter from "./routes/material.routes.js"

const router = Router()

router.get("/users", async (req, res) => {
    const users = await prisma.user.findMany()
    res.json(users)
})

router.use("/users", userRouter)
router.use("/students", studentRouter)
router.use("/materials", materialRouter)

export { router }
import express from "express"
import { prisma } from "../database/index.js"


import userRoutes from "./user.routes.js";
import materialRoutes from "./material.routes.js";
import reminderRoutes from "./reminder.routes.js";
import planRoutes from "./plan.routes.js";


const router = express.Router();


router.get("/users", async (req, res) => {
    const users = await prisma.user.findMany()
    res.json(users)
})


router.use("/users", userRoutes);        
router.use("/materials", materialRoutes); 
router.use("/reminders", reminderRoutes);
router.use("/plan", planRoutes);          

router.get("/", (req, res) => {
  res.send("✅ EstudaAI API - Roteador funcionando!");
});

export default router;
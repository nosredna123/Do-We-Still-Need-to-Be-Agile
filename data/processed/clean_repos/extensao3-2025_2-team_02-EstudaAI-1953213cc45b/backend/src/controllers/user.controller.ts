import type { NextFunction, Request, Response } from "express"
import { CreateUserRequestSchema } from "../schemas/UsersRequestSchema.js"
import { userService } from "../services/user.service.js"
import type { Role } from "../types/roles.js"

export const registerUser = async (req: Request, res: Response, next: NextFunction) => {
    try {
        const body = CreateUserRequestSchema.parse(req.body)
        const newUser = await userService.registerService(body)
        res.status(201).json(newUser)
    } catch (error) {
        next(error)
    }
}

export const loginUser = async (req: Request, res: Response, next: NextFunction) => {
    try {
        const { email, password } = req.body

        const user = await userService.loginService(email, password)
        if(user.error) {
            res.status(500).json({error: user.error})
        }
        else {
            const accessToken = await userService.getAcessToken(user.id, user.role)
            const userId = user.id
            const userRole = user.role
            res.status(200).json({
                id: user.id,
                name: user.name,
                email: user.email,
                role: user.role,
                accessToken
            })
        }
    } catch (error) {
        next(error) 
    }
}
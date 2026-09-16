import { prisma } from "../database/index.js";
import type { Role } from "../types/roles.js";
import jwt from "jsonwebtoken"

class UserService {
    async loginService(email: string, password: string) {
        const user = await prisma.user.findFirst({
            where: { email, password },
            include: {
                student: true,
                teacher: true
            }
        })

        if(!user) {
            return { error: "Credenciais inválidas. Tente novamente" }
        }

        let role: Role

        console.log(user.student)

        if(user.student) {
            role = "STUDENT"
        }
        else {
            if(user.teacher) {
                role = "TEACHER"
            }
            else{
                throw new Error("Unknown user type")
            }
        }
        
        return {
            id: user.id,
            name: user.name,
            email: user.email,
            role
        }
    }

    async registerService(body: { name: string; email: string; password: string; }) {
        const newUser = await prisma.user.create({
            data: {
                email: body.email,
                name: body.name,
                password: body.password,
            }
        })
        return newUser
    }

    async getAcessToken(userId: number, role: Role) {
        const secret = process.env.ACCESS_TOKEN_SECRET
        if(!secret) throw new Error("ACCESS TOKEN NOT DEFINED")
        const accessToken = jwt.sign({id: userId, userRole: role}, secret, {expiresIn: "1h"})
        return accessToken
    }
}

export const userService = new UserService()
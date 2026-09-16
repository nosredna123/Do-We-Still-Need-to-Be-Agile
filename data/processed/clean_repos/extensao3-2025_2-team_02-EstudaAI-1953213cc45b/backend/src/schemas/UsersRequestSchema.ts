import z3, { z } from "zod";

export const CreateUserRequestSchema = z3.object({
    name: z.string(),
    email: z.string().email(),
    password: z.string()
})

export const CreateReminderSchema = z3.object({
    title: z.string().min(1),
    description: z.string().min(1),
    due_date: z.string().optional(),
  });
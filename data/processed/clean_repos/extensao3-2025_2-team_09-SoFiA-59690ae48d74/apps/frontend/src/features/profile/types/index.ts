import { z } from 'zod'

export const profileSchema = z.object({
  name: z.string().min(2, 'O nome deve ter pelo menos 2 caracteres'),
  api_key: z.string().optional().nullable(),
  profile_pic: z.string().optional().nullable(),
  salary: z.string().nullable().refine((val) => !val || !isNaN(Number(val)), {
    message: 'O salário deve ser um número válido',
  }),
  payday: z.string().optional().nullable().refine((val) => !val || (Number(val) >= 1 && Number(val) <= 31), {
    message: 'O dia de recebimento deve estar entre 1 e 31',
  }),
})

export type ProfileFormValues = z.infer<typeof profileSchema>

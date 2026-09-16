import { supabase } from "../config/supabase.js"
import { prisma } from "../database/index.js"

class MaterialService {
    sanitizeFileName(filename: string): string {
        return filename
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .replace(/[^a-zA-Z0-9.\-_]/g, "_");
    }

    async uploadMaterialsService(userId: number, topicId: number, files: Express.Multer.File[]) {
        const uploads = files.map(async (file) => {
            const safeName = this.sanitizeFileName(file.originalname)
            const path = `materials/${userId}/${topicId}/${Date.now()}-${safeName}`

            const { error } = await supabase.storage
            .from(`EstudaAI%20Files`)
            .upload(path, file.buffer, {
                contentType: file.mimetype
            })

            if (error) throw new Error("Erro no upload: " + error.message)

            const { data: publicUrlData } = supabase.storage
            .from("EstudaAI%20Files")
            .getPublicUrl(path)

            const newFile = await prisma.material.create({
                data: {
                    title: file.originalname,
                    file_type: file.mimetype,
                    file_path: publicUrlData.publicUrl,
                    topic: {
                        connect: { id: topicId }
                    },
                    user: {
                        connect: { id: userId }
                    }
                }
            })

            return newFile
        })

       return Promise.all(uploads)
    }
}

export const materialService = new MaterialService()
export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  // Allows to automatically instantiate createClient with right options
  // instead of createClient<Database, { PostgrestVersion: 'XX' }>(URL, KEY)
  __InternalSupabase: {
    PostgrestVersion: "14.5"
  }
  public: {
    Tables: {
      alternativa: {
        Row: {
          correta: boolean
          feedback: string | null
          id_questao: number
          letra: string
          texto: string
        }
        Insert: {
          correta?: boolean
          feedback?: string | null
          id_questao: number
          letra: string
          texto: string
        }
        Update: {
          correta?: boolean
          feedback?: string | null
          id_questao?: number
          letra?: string
          texto?: string
        }
        Relationships: [
          {
            foreignKeyName: "alternativa_id_questao_fkey"
            columns: ["id_questao"]
            isOneToOne: false
            referencedRelation: "questao"
            referencedColumns: ["id_questao"]
          },
        ]
      }
      aluno: {
        Row: {
          auth_user_id: string | null
          avatar_url: string | null
          created_at: string
          email: string
          id_aluno: number
          id_instituicao: number | null
          nome: string
          senha: string | null
          updated_at: string
        }
        Insert: {
          auth_user_id?: string | null
          avatar_url?: string | null
          created_at?: string
          email: string
          id_aluno?: number
          id_instituicao?: number | null
          nome: string
          senha?: string | null
          updated_at?: string
        }
        Update: {
          auth_user_id?: string | null
          avatar_url?: string | null
          created_at?: string
          email?: string
          id_aluno?: number
          id_instituicao?: number | null
          nome?: string
          senha?: string | null
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "aluno_id_instituicao_fkey"
            columns: ["id_instituicao"]
            isOneToOne: false
            referencedRelation: "instituicao"
            referencedColumns: ["id_instituicao"]
          },
        ]
      }
      aluno_questao_tags: {
        Row: {
          data_tag: string
          id_aluno: number
          id_questao: number
          id_tag: number
        }
        Insert: {
          data_tag?: string
          id_aluno: number
          id_questao: number
          id_tag: number
        }
        Update: {
          data_tag?: string
          id_aluno?: number
          id_questao?: number
          id_tag?: number
        }
        Relationships: [
          {
            foreignKeyName: "aluno_questao_tags_id_aluno_fkey"
            columns: ["id_aluno"]
            isOneToOne: false
            referencedRelation: "aluno"
            referencedColumns: ["id_aluno"]
          },
          {
            foreignKeyName: "aluno_questao_tags_id_questao_fkey"
            columns: ["id_questao"]
            isOneToOne: false
            referencedRelation: "questao"
            referencedColumns: ["id_questao"]
          },
          {
            foreignKeyName: "aluno_questao_tags_id_tag_fkey"
            columns: ["id_tag"]
            isOneToOne: false
            referencedRelation: "tags"
            referencedColumns: ["id_tag"]
          },
        ]
      }
      assunto: {
        Row: {
          created_at: string
          id_assunto: number
          id_assunto_pai: number | null
          id_disciplina: number
          nome: string
        }
        Insert: {
          created_at?: string
          id_assunto?: number
          id_assunto_pai?: number | null
          id_disciplina: number
          nome: string
        }
        Update: {
          created_at?: string
          id_assunto?: number
          id_assunto_pai?: number | null
          id_disciplina?: number
          nome?: string
        }
        Relationships: [
          {
            foreignKeyName: "assunto_id_assunto_pai_fkey"
            columns: ["id_assunto_pai"]
            isOneToOne: false
            referencedRelation: "assunto"
            referencedColumns: ["id_assunto"]
          },
          {
            foreignKeyName: "assunto_id_disciplina_fkey"
            columns: ["id_disciplina"]
            isOneToOne: false
            referencedRelation: "disciplina"
            referencedColumns: ["id_disciplina"]
          },
        ]
      }
      banca: {
        Row: {
          created_at: string
          id_banca: number
          nome: string
          sigla: string | null
        }
        Insert: {
          created_at?: string
          id_banca?: number
          nome: string
          sigla?: string | null
        }
        Update: {
          created_at?: string
          id_banca?: number
          nome?: string
          sigla?: string | null
        }
        Relationships: []
      }
      chat_message: {
        Row: {
          conteudo: string
          created_at: string
          id_chat: number
          id_mensagem: number
          id_questao: number | null
          id_resposta: number | null
          metadata: Json | null
          role: Database["public"]["Enums"]["chat_role"]
        }
        Insert: {
          conteudo: string
          created_at?: string
          id_chat: number
          id_mensagem?: number
          id_questao?: number | null
          id_resposta?: number | null
          metadata?: Json | null
          role: Database["public"]["Enums"]["chat_role"]
        }
        Update: {
          conteudo?: string
          created_at?: string
          id_chat?: number
          id_mensagem?: number
          id_questao?: number | null
          id_resposta?: number | null
          metadata?: Json | null
          role?: Database["public"]["Enums"]["chat_role"]
        }
        Relationships: [
          {
            foreignKeyName: "chat_message_id_chat_fkey"
            columns: ["id_chat"]
            isOneToOne: false
            referencedRelation: "chat_session"
            referencedColumns: ["id_chat"]
          },
          {
            foreignKeyName: "chat_message_id_questao_fkey"
            columns: ["id_questao"]
            isOneToOne: false
            referencedRelation: "questao"
            referencedColumns: ["id_questao"]
          },
          {
            foreignKeyName: "chat_message_id_resposta_fkey"
            columns: ["id_resposta"]
            isOneToOne: false
            referencedRelation: "resposta"
            referencedColumns: ["id_resposta"]
          },
        ]
      }
      chat_session: {
        Row: {
          build: string | null
          created_at: string
          id_aluno: number
          id_chat: number
          id_disciplina: number | null
          status: boolean
          titulo: string | null
          updated_at: string
        }
        Insert: {
          build?: string | null
          created_at?: string
          id_aluno: number
          id_chat?: number
          id_disciplina?: number | null
          status?: boolean
          titulo?: string | null
          updated_at?: string
        }
        Update: {
          build?: string | null
          created_at?: string
          id_aluno?: number
          id_chat?: number
          id_disciplina?: number | null
          status?: boolean
          titulo?: string | null
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "chat_session_id_aluno_fkey"
            columns: ["id_aluno"]
            isOneToOne: false
            referencedRelation: "aluno"
            referencedColumns: ["id_aluno"]
          },
          {
            foreignKeyName: "chat_session_id_disciplina_fkey"
            columns: ["id_disciplina"]
            isOneToOne: false
            referencedRelation: "disciplina"
            referencedColumns: ["id_disciplina"]
          },
        ]
      }
      comentarios: {
        Row: {
          comentario_pai_id: number | null
          data_comentario: string
          id_aluno: number
          id_comentario: number
          id_questao: number
          status: boolean
          texto: string
        }
        Insert: {
          comentario_pai_id?: number | null
          data_comentario?: string
          id_aluno: number
          id_comentario?: number
          id_questao: number
          status?: boolean
          texto: string
        }
        Update: {
          comentario_pai_id?: number | null
          data_comentario?: string
          id_aluno?: number
          id_comentario?: number
          id_questao?: number
          status?: boolean
          texto?: string
        }
        Relationships: [
          {
            foreignKeyName: "comentarios_comentario_pai_id_fkey"
            columns: ["comentario_pai_id"]
            isOneToOne: false
            referencedRelation: "comentarios"
            referencedColumns: ["id_comentario"]
          },
          {
            foreignKeyName: "comentarios_id_aluno_fkey"
            columns: ["id_aluno"]
            isOneToOne: false
            referencedRelation: "aluno"
            referencedColumns: ["id_aluno"]
          },
          {
            foreignKeyName: "comentarios_id_questao_fkey"
            columns: ["id_questao"]
            isOneToOne: false
            referencedRelation: "questao"
            referencedColumns: ["id_questao"]
          },
        ]
      }
      disciplina: {
        Row: {
          cor_hex: string | null
          created_at: string
          icone: string | null
          id_disciplina: number
          nome: string
        }
        Insert: {
          cor_hex?: string | null
          created_at?: string
          icone?: string | null
          id_disciplina?: number
          nome: string
        }
        Update: {
          cor_hex?: string | null
          created_at?: string
          icone?: string | null
          id_disciplina?: number
          nome?: string
        }
        Relationships: []
      }
      instituicao: {
        Row: {
          created_at: string
          id_instituicao: number
          nome: string
          sigla: string | null
          status: boolean
          uf: string | null
        }
        Insert: {
          created_at?: string
          id_instituicao?: number
          nome: string
          sigla?: string | null
          status?: boolean
          uf?: string | null
        }
        Update: {
          created_at?: string
          id_instituicao?: number
          nome?: string
          sigla?: string | null
          status?: boolean
          uf?: string | null
        }
        Relationships: []
      }
      log: {
        Row: {
          acao: string
          data_hora: string
          id_aluno: number | null
          id_log: number
          payload: Json | null
        }
        Insert: {
          acao: string
          data_hora?: string
          id_aluno?: number | null
          id_log?: number
          payload?: Json | null
        }
        Update: {
          acao?: string
          data_hora?: string
          id_aluno?: number | null
          id_log?: number
          payload?: Json | null
        }
        Relationships: [
          {
            foreignKeyName: "log_id_aluno_fkey"
            columns: ["id_aluno"]
            isOneToOne: false
            referencedRelation: "aluno"
            referencedColumns: ["id_aluno"]
          },
        ]
      }
      prova: {
        Row: {
          created_at: string
          data_prova: string | null
          id_aluno: number | null
          id_prova: number
          nome: string
          status: boolean
        }
        Insert: {
          created_at?: string
          data_prova?: string | null
          id_aluno?: number | null
          id_prova?: number
          nome: string
          status?: boolean
        }
        Update: {
          created_at?: string
          data_prova?: string | null
          id_aluno?: number | null
          id_prova?: number
          nome?: string
          status?: boolean
        }
        Relationships: [
          {
            foreignKeyName: "prova_id_aluno_fkey"
            columns: ["id_aluno"]
            isOneToOne: false
            referencedRelation: "aluno"
            referencedColumns: ["id_aluno"]
          },
        ]
      }
      questao: {
        Row: {
          ano: number | null
          comentario: string | null
          created_at: string
          dificuldade: Database["public"]["Enums"]["questao_dificuldade"] | null
          enunciado: string
          fonte_prompt: string | null
          id_banca: number | null
          id_prova: number | null
          id_questao: number
          origem: Database["public"]["Enums"]["questao_origem"]
          status: boolean
          tipo: string | null
          verificada: boolean
        }
        Insert: {
          ano?: number | null
          comentario?: string | null
          created_at?: string
          dificuldade?:
            | Database["public"]["Enums"]["questao_dificuldade"]
            | null
          enunciado: string
          fonte_prompt?: string | null
          id_banca?: number | null
          id_prova?: number | null
          id_questao?: number
          origem?: Database["public"]["Enums"]["questao_origem"]
          status?: boolean
          tipo?: string | null
          verificada?: boolean
        }
        Update: {
          ano?: number | null
          comentario?: string | null
          created_at?: string
          dificuldade?:
            | Database["public"]["Enums"]["questao_dificuldade"]
            | null
          enunciado?: string
          fonte_prompt?: string | null
          id_banca?: number | null
          id_prova?: number | null
          id_questao?: number
          origem?: Database["public"]["Enums"]["questao_origem"]
          status?: boolean
          tipo?: string | null
          verificada?: boolean
        }
        Relationships: [
          {
            foreignKeyName: "questao_id_banca_fkey"
            columns: ["id_banca"]
            isOneToOne: false
            referencedRelation: "banca"
            referencedColumns: ["id_banca"]
          },
          {
            foreignKeyName: "questao_id_prova_fkey"
            columns: ["id_prova"]
            isOneToOne: false
            referencedRelation: "prova"
            referencedColumns: ["id_prova"]
          },
        ]
      }
      questao_assunto: {
        Row: {
          id_assunto: number
          id_questao: number
        }
        Insert: {
          id_assunto: number
          id_questao: number
        }
        Update: {
          id_assunto?: number
          id_questao?: number
        }
        Relationships: [
          {
            foreignKeyName: "questao_assunto_id_assunto_fkey"
            columns: ["id_assunto"]
            isOneToOne: false
            referencedRelation: "assunto"
            referencedColumns: ["id_assunto"]
          },
          {
            foreignKeyName: "questao_assunto_id_questao_fkey"
            columns: ["id_questao"]
            isOneToOne: false
            referencedRelation: "questao"
            referencedColumns: ["id_questao"]
          },
        ]
      }
      resposta: {
        Row: {
          correta: boolean | null
          data_resposta: string
          id_aluno: number
          id_questao: number
          id_resposta: number
          letra_resposta: string | null
          texto_resposta: string | null
        }
        Insert: {
          correta?: boolean | null
          data_resposta?: string
          id_aluno: number
          id_questao: number
          id_resposta?: number
          letra_resposta?: string | null
          texto_resposta?: string | null
        }
        Update: {
          correta?: boolean | null
          data_resposta?: string
          id_aluno?: number
          id_questao?: number
          id_resposta?: number
          letra_resposta?: string | null
          texto_resposta?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "resposta_id_aluno_fkey"
            columns: ["id_aluno"]
            isOneToOne: false
            referencedRelation: "aluno"
            referencedColumns: ["id_aluno"]
          },
          {
            foreignKeyName: "resposta_id_questao_fkey"
            columns: ["id_questao"]
            isOneToOne: false
            referencedRelation: "questao"
            referencedColumns: ["id_questao"]
          },
        ]
      }
      tags: {
        Row: {
          cor_hex: string | null
          descricao: string | null
          icone: string | null
          id_tag: number
          nome: string
        }
        Insert: {
          cor_hex?: string | null
          descricao?: string | null
          icone?: string | null
          id_tag?: number
          nome: string
        }
        Update: {
          cor_hex?: string | null
          descricao?: string | null
          icone?: string | null
          id_tag?: number
          nome?: string
        }
        Relationships: []
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      [_ in never]: never
    }
    Enums: {
      chat_role: "user" | "assistant" | "system"
      questao_dificuldade: "facil" | "media" | "dificil"
      questao_origem: "oficial" | "gerada_ia"
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}

type DatabaseWithoutInternals = Omit<Database, "__InternalSupabase">

type DefaultSchema = DatabaseWithoutInternals[Extract<keyof Database, "public">]

export type Tables<
  DefaultSchemaTableNameOrOptions extends
    | keyof (DefaultSchema["Tables"] & DefaultSchema["Views"])
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
        DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
      DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])[TableName] extends {
      Row: infer R
    }
    ? R
    : never
  : DefaultSchemaTableNameOrOptions extends keyof (DefaultSchema["Tables"] &
        DefaultSchema["Views"])
    ? (DefaultSchema["Tables"] &
        DefaultSchema["Views"])[DefaultSchemaTableNameOrOptions] extends {
        Row: infer R
      }
      ? R
      : never
    : never

export type TablesInsert<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Insert: infer I
    }
    ? I
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Insert: infer I
      }
      ? I
      : never
    : never

export type TablesUpdate<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Update: infer U
    }
    ? U
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Update: infer U
      }
      ? U
      : never
    : never

export type Enums<
  DefaultSchemaEnumNameOrOptions extends
    | keyof DefaultSchema["Enums"]
    | { schema: keyof DatabaseWithoutInternals },
  EnumName extends DefaultSchemaEnumNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"]
    : never = never,
> = DefaultSchemaEnumNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"][EnumName]
  : DefaultSchemaEnumNameOrOptions extends keyof DefaultSchema["Enums"]
    ? DefaultSchema["Enums"][DefaultSchemaEnumNameOrOptions]
    : never

export type CompositeTypes<
  PublicCompositeTypeNameOrOptions extends
    | keyof DefaultSchema["CompositeTypes"]
    | { schema: keyof DatabaseWithoutInternals },
  CompositeTypeName extends PublicCompositeTypeNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"]
    : never = never,
> = PublicCompositeTypeNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"][CompositeTypeName]
  : PublicCompositeTypeNameOrOptions extends keyof DefaultSchema["CompositeTypes"]
    ? DefaultSchema["CompositeTypes"][PublicCompositeTypeNameOrOptions]
    : never

export const Constants = {
  public: {
    Enums: {
      chat_role: ["user", "assistant", "system"],
      questao_dificuldade: ["facil", "media", "dificil"],
      questao_origem: ["oficial", "gerada_ia"],
    },
  },
} as const

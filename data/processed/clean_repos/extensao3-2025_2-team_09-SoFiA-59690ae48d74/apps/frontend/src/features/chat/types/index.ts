export interface ApiResponse<T> {
  data: T
  error?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

export interface UserSalaryInfo {
  amount: number
  payday: number
}

export interface User {
  id: number
  name: string
  profile_pic: string | null
  api_key: string | null
  created_at: string | null
  updated_at: string | null
  salary_recurrence_id: number | null
  salary: UserSalaryInfo | null
}

export interface CreateUserRequest {
  name: string
  profile_pic?: string
  api_key?: string
}

export interface UpdateUserRequest {
  name?: string
  profile_pic?: string
  api_key?: string
}

export type RecurrenceFrequency = 'monthly' | 'weekly' | 'yearly'

export interface RecurrenceInput {
  amount: number
  description: string
  transaction_type: 'income' | 'expense'
  frequency: RecurrenceFrequency
  day: number
  category_id?: number | null
  active?: boolean
}

export interface RecurrenceUpdate {
  amount?: number
  description?: string
  transaction_type?: 'income' | 'expense'
  frequency?: RecurrenceFrequency
  day?: number
  category_id?: number | null
  active?: boolean
}

export interface Category {
  id: number
  name: string
  created_at: string | null
  updated_at: string | null
}

export interface CreateCategoryRequest {
  name: string
}

export type TransactionType = 'expense' | 'income'

export interface Transaction {
  id: number
  amount: number
  description: string
  transaction_type: TransactionType
  category_id: number 
  user_id: number
  created_at: string | null
  updated_at: string | null
  reference_date : string 
}

export interface CreateExpenseRequest {
  amount: number
  description: string
  transaction_type: 'expense'
  category_id: number
}

export interface CreateIncomeRequest {
  amount: number
  description: string
  transaction_type: 'income'
  category_id?: null
}

export type ChatRole = 'user' | 'assistant'
export type ModelPreference = 'remote' | 'dummy'

export interface Message {
  id: number
  content: string
  role: ChatRole
  created_at: string
  meta_data: Record<string, never> | null
}

export interface UIMessage {
  role: ChatRole
  content: string
}

export interface ChatSession {
  id: number
  user_id: number
  title: string | null
  created_at: string
  updated_at: string | null
  messages: Message[]
}

export interface CreateSessionRequest {
  message: string
  model_preference?: ModelPreference | string
  model_name?: string
}

export interface CreateSessionResponse {
  response: string
  session_id: number
  session_title: string
  action_taken: string
}

export interface UpdateSessionRequest {
  title: string
}

export interface SendMessageRequest {
  message: string
  model_preference?: ModelPreference | string
  model_name?: string
}

export interface SendMessageResponse {
  response: string
  session_id: number
  session_title: string | null
  action_taken: string | null
}

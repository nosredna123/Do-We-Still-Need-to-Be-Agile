import axios, { AxiosError, type AxiosResponse } from 'axios'
import { toast } from 'sonner'
import { Env } from '../env'

declare module 'axios' {
  export interface AxiosRequestConfig {
    _showToastOnError?: boolean
  }
}

const apiClient = axios.create({
  baseURL: Env.VITE_API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
})

apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config
    const shouldShowToast = originalRequest?._showToastOnError !== false
    if (error.response && shouldShowToast) {
      const errorData = error.response.data as {
        error?: string
        detail?: string
        response?: string
      }
      const errorMessage =
        errorData?.detail ||
        errorData?.error ||
        errorData?.response ||
        'Um erro inesperado ocorreu. Tente novamente mais tarde.'
      toast.error(errorMessage)
    } else if (!error.response && shouldShowToast) {
      toast.error('Erro de conexão. Verifique sua internet ou tente novamente.')
    }
    return Promise.reject(error)
  }
)

export default apiClient

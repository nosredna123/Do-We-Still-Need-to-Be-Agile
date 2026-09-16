import type { AxiosRequestConfig } from "axios"
import api from "./axiosConfig"

const get = async <T>(
  url: string,
  params?: object,
  baseURL?: string,
  config?: AxiosRequestConfig
): Promise<T> => {
  const response = await api(baseURL).get<T>(url, { params, ...config })
  return response.data
}

const post = async <T>(
  url: string,
  body: object,
  params?: object,
  baseURL?: string,
  config?: AxiosRequestConfig
): Promise<T> => {
  const response = await api(baseURL).post<T>(url, body, { params, ...config })
  return response.data
}

const put = async <T>(
  url: string,
  body: object,
  params?: object,
  baseURL?: string
): Promise<T> => {
  const response = await api(baseURL).put<T>(url, body, { params })
  return response.data
}

const patch = async <T>(
  url: string,
  body: object,
  params?: object,
  baseURL?: string
): Promise<T> => {
  const response = await api(baseURL).patch<T>(url, body, { params })
  return response.data
}

const del = async <T>(
  url: string, 
  baseURL?: string,
  params?: object
): Promise<T> => {
  const response = await api(baseURL).delete<T>(url, { params })
  return response.data
}

export default { get, post, put, patch, delete: del }
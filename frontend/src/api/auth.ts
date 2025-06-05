import axios from 'axios'

const API_URL = 'http://localhost:8000/api'

export interface RegisterData {
  username: string
  password: string
  password2: string
  email: string
}

export const register = async (data: RegisterData) => {
  try {
    const response = await axios.post(`${API_URL}/user/register/`, data)
    return response.data
  } catch (error: any) {
    if (error.response) {
      throw error.response.data
    }
    throw error
  }
} 
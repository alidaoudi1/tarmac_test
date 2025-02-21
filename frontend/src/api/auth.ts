import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

export interface LoginData {
  username: string;
  password: string;
}

export interface RegisterData extends LoginData {
  email: string;
}

export const auth = {
  login: async (data: LoginData) => {
    const response = await axios.post(`${API_URL}/auth/login/`, data);
    return response.data;
  },
  
  register: async (data: RegisterData) => {
    const response = await axios.post(`${API_URL}/auth/register/`, data);
    return response.data;
  }
}; 
import axios from 'axios'

export const baseUrl = 'http://192.168.1.180'

export const HTTP = axios.create({
  baseURL: `${baseUrl}/api/`
})

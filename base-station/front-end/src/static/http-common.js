import axios from 'axios'

export const baseUrl = 'http://100.89.161.91'

export const HTTP = axios.create({
  baseURL: `${baseUrl}/api/`
})

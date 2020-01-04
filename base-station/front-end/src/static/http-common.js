import axios from 'axios'

export const HTTP = axios.create({
  baseURL: `http://192.168.1.180:5000/api/`
})
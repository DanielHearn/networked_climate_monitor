import axios from 'axios'

export const HTTP = axios.create({
  baseURL: `http://100.89.155.6:5000/api/`
})
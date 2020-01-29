import axios from 'axios'

export const HTTP = axios.create({
  baseURL: 'http://100.89.161.91:5000/api/'
})

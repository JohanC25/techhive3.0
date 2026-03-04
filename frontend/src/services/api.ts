import axios from 'axios'

/*const api = axios.create({
  baseURL: `http://${window.location.hostname}:8000`
})*/
const backendPort = '8000'
const api = axios.create({
  baseURL: `${window.location.protocol}//${window.location.hostname}:${backendPort}`
})


api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default api
import axios from 'axios'
import { useAuthStore } from '@/sotres/auth'

const apiClient =  axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/",
    timeout: 5000,
})

apiClient.interceptors.request.use(
    (config) => {
        const authStore = useAuthStore()
        if (authStore.token){
            config.headers.Authorization = `Bearer ${authStore.token}`
            return config
    }
    (error) => Promise.reject(error)

})

export default apiClient
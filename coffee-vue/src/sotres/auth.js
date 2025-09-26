import {defineStore} from 'pinia'

export const useAuthStore = defineStore('auth', {
    state:() => ({
        token: localStorage.getItem('authToken') || null,
        user: null,
        isLogged: false,
        error:null,
    }),

    getters:{
        isAuthenticated:(state) => !!state.token,
    },

    actions:{
        setToken(token){
            this.token = token
            if(token){
                localStorage.setItem('authToken', token)
            }
            else{
                localStorage.removeItem('authToken')
            }
        },

        setIsLogged(isLogged){
            this.isLogged=isLogged
        },

        setError(error){
            this.error=error
        },

        clear(){
            this.setToken(null)
            this.setIsLogged(false)
            this.setError(null)
        },
    }
})
import { createRouter, createWebHistory } from 'vue-router'
import DialogueView from '../views/DialogueView.vue'
import UserLoginView from '../views/UserLoginView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    
    {
      path: '/dialogue/:id',
      name: 'Dialogue',
      component: DialogueView,
      props:true,
    },
    {
      path: '/user/login',
      name: 'user_login',
      component: UserLoginView,
    },
    {
      path: '/user/register',
      name: 'user_register',
      component: () => import('../views/UserRegisterView.vue'),
    },
  ],
})

export default router

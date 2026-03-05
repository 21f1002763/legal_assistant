import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Section from '../views/Section.vue'
import Chat from '../views/Chat.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/section/:number',
    name: 'Section',
    component: Section
  },
  {
    path: '/chat',
    name: 'Chat',
    component: Chat
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router

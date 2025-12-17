import { createRouter, createWebHistory } from 'vue-router'

import StoryDashboard from '../pages/StoryDashboard.vue'
import StoryReplay from '../pages/StoryReplay.vue'

const routes = [
  {
    path: '/',
    name: 'StoryDashboard',
    component: StoryDashboard,
  },
  {
    path: '/replay/:storyId',
    name: 'StoryReplay',
    component: StoryReplay,
    props: true,
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router

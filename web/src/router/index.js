import { createRouter, createWebHistory } from 'vue-router'
import Layout from '../views/Layout.vue'
import Login from '../views/Login.vue'
import Ledger from '../views/Ledger.vue'
import Input from '../views/Input.vue'
import Persons from '../views/Persons.vue'
import Definitions from '../views/Definitions.vue'
import Analysis from '../views/Analysis.vue'
import Advice from '../views/Advice.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: Layout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Ledger',
        component: Ledger
      },
      {
        path: 'input',
        name: 'Input',
        component: Input
      },
      {
        path: 'persons',
        name: 'Persons',
        component: Persons
      },
      {
        path: 'definitions',
        name: 'Definitions',
        component: Definitions
      },
      {
        path: 'analysis',
        name: 'Analysis',
        component: Analysis
      },
      {
        path: 'advice',
        name: 'Advice',
        component: Advice
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')
  if (to.meta.requiresAuth !== false && !token) {
    next({ name: 'Login' })
  } else if (to.name === 'Login' && token) {
    next({ name: 'Ledger' })
  } else {
    next()
  }
})

export default router
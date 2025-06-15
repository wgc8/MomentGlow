import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import ProfileView from '../views/ProfileView.vue'
import FeedView from '../views/FeedView.vue'
import { useUserStore } from '@/store/user'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView
    },
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: {
        requiresAuth: true
      }
    },
    {
      path: '/feed',
      name: 'feed',
      component: FeedView,
      meta: {
        requiresAuth: true
      }
    },
    {
      path: '/profile',
      name: 'my-profile',
      component: ProfileView,
      meta: {
        requiresAuth: true
      }
    },
    {
      path: '/profile/:id',
      name: 'user-profile',
      component: ProfileView,
      meta: {
        requiresAuth: true
      }
    }
  ]
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  
  if (to.matched.some(record => record.meta.requiresAuth)) {
    // 需要登录的页面
    if (!userStore.isLoggedIn) {
      next('/login')
    } else {
      next()
    }
  } else {
    // 不需要登录的页面
    if (userStore.isLoggedIn && (to.path === '/login' || to.path === '/register')) {
      next('/')
    } else {
      next()
    }
  }
})

export default router 
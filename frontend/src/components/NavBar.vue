<template>
  <div class="navbar">
    <div class="navbar-container">
      <div class="logo">
        <router-link to="/">MomentGlow</router-link>
      </div>
      <div class="nav-links">
        <router-link to="/" class="nav-link">首页</router-link>
        <router-link to="/feed" class="nav-link">动态</router-link>
        <router-link to="/profile" class="nav-link">个人主页</router-link>
      </div>
      <div class="user-actions">
        <span class="username">{{ username }}</span>
        <el-dropdown>
          <span class="el-dropdown-link">
            <el-avatar :size="32" :src="avatar || '/default-avatar.png'"></el-avatar>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="goToProfile">个人主页</el-dropdown-item>
              <el-dropdown-item @click="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'

const router = useRouter()
const userStore = useUserStore()

const username = computed(() => userStore.username)
const avatar = computed(() => '')  // 如果用户有头像，可以从用户信息中获取

const goToProfile = () => {
  router.push('/profile')
}

const logout = () => {
  userStore.logout()
  router.push('/login')
}
</script>

<style lang="scss" scoped>
.navbar {
  background-color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 0 20px;
  height: 60px;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  
  .navbar-container {
    max-width: 1200px;
    margin: 0 auto;
    height: 100%;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .logo {
    font-size: 20px;
    font-weight: bold;
    
    a {
      color: #409EFF;
      text-decoration: none;
    }
  }
  
  .nav-links {
    display: flex;
    gap: 20px;
    
    .nav-link {
      color: #333;
      text-decoration: none;
      font-size: 16px;
      padding: 5px 0;
      position: relative;
      
      &:hover, &.router-link-active {
        color: #409EFF;
      }
      
      &.router-link-active::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 2px;
        background-color: #409EFF;
      }
    }
  }
  
  .user-actions {
    display: flex;
    align-items: center;
    gap: 10px;
    
    .username {
      font-size: 14px;
      color: #333;
    }
    
    .el-dropdown-link {
      cursor: pointer;
      display: flex;
      align-items: center;
    }
  }
}

// 移动端适配
@media screen and (max-width: 768px) {
  .navbar {
    padding: 0 10px;
    
    .nav-links {
      display: none;
    }
    
    .username {
      display: none;
    }
  }
}
</style> 
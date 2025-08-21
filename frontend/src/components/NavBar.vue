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
        <el-dropdown class="avatar-dropdown">
          <span class="el-dropdown-link">
            <el-avatar :size="32" :src="avatarUrl" class="user-avatar"></el-avatar>
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
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { getUserAvatar } from '@/api/user'

const router = useRouter()
const userStore = useUserStore()

const username = computed(() => userStore.username)
const avatarUrl = ref('/media/default.jpg')

const loadUserAvatar = async () => {
  try {
    const avatarInfo = await getUserAvatar()
    avatarUrl.value = avatarInfo.avatar_url
  } catch (error) {
    console.error('获取用户头像失败:', error)
    avatarUrl.value = '/media/default.jpg'
  }
}

const goToProfile = () => {
  router.push('/profile')
}

const logout = () => {
  userStore.logout()
  router.push('/login')
}

onMounted(() => {
  if (userStore.isLoggedIn) {
    loadUserAvatar()
  }
})
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
    
    .avatar-dropdown {
      .el-dropdown-link {
        cursor: pointer;
        display: flex;
        align-items: center;
        outline: none;
        border: none;
        background: none;
        
        &:hover {
          outline: none;
          border: none;
          background: none;
        }
        
        &:focus {
          outline: none;
          border: none;
          background: none;
        }
      }
      
      .user-avatar {
        border-radius: 50%;
        transition: all 0.3s ease;
        
        &:hover {
          transform: scale(1.05);
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
        }
      }
    }
  }
}

// 覆盖Element Plus的默认样式
:deep(.el-dropdown) {
  .el-dropdown-link {
    outline: none !important;
    border: none !important;
    background: none !important;
    
    &:hover {
      outline: none !important;
      border: none !important;
      background: none !important;
    }
    
    &:focus {
      outline: none !important;
      border: none !important;
      background: none !important;
    }
  }
}

:deep(.el-avatar) {
  border: none !important;
  outline: none !important;
  
  &:hover {
    border: none !important;
    outline: none !important;
  }
  
  &:focus {
    border: none !important;
    outline: none !important;
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
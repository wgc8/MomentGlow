<template>
  <div class="avatar-upload">
    <div class="avatar-container">
      <el-avatar 
        :size="size" 
        :src="avatarUrl" 
        @error="handleAvatarError"
      />
      <div class="upload-overlay" @click="triggerFileInput">
        <el-icon><Camera /></el-icon>
        <span>更换头像</span>
      </div>
    </div>
    
    <input
      ref="fileInput"
      type="file"
      accept="image/*"
      style="display: none"
      @change="handleFileChange"
    />
    
    <!-- 上传进度 -->
    <el-progress 
      v-if="uploading" 
      :percentage="uploadProgress" 
      :show-text="false"
      class="upload-progress"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Camera } from '@element-plus/icons-vue'
import { getUserAvatar, uploadUserAvatar } from '@/api/user'

interface Props {
  size?: number
  userId?: number
}

const props = withDefaults(defineProps<Props>(), {
  size: 100,
  userId: undefined
})

const emit = defineEmits<{
  avatarUpdated: [avatarUrl: string]
}>()

const fileInput = ref<HTMLInputElement>()
const avatarUrl = ref('/media/default.jpg')
const uploading = ref(false)
const uploadProgress = ref(0)

const loadAvatar = async () => {
  try {
    const avatarInfo = await getUserAvatar(props.userId)
    avatarUrl.value = avatarInfo.avatar_url
  } catch (error) {
    console.error('获取头像失败:', error)
    avatarUrl.value = '/media/default.jpg'
  }
}

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileChange = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  
  if (!file) return
  
  // 验证文件类型
  const allowedTypes = ['image/jpeg', 'image/png', 'image/gif']
  if (!allowedTypes.includes(file.type)) {
    ElMessage.error('只支持JPEG、PNG、GIF格式的图片')
    return
  }
  
  // 验证文件大小（5MB）
  if (file.size > 5 * 1024 * 1024) {
    ElMessage.error('图片大小不能超过5MB')
    return
  }
  
  try {
    uploading.value = true
    uploadProgress.value = 0
    
    // 模拟上传进度
    const progressInterval = setInterval(() => {
      if (uploadProgress.value < 90) {
        uploadProgress.value += 10
      }
    }, 100)
    
    const result = await uploadUserAvatar(file)
    
    clearInterval(progressInterval)
    uploadProgress.value = 100
    
    ElMessage.success('头像上传成功，页面即将刷新')
    
    // 重置文件输入
    if (target) {
      target.value = ''
    }
    
    // 延迟一下再刷新页面，让用户看到成功消息
    setTimeout(() => {
      window.location.reload()
    }, 1000)
    
  } catch (error) {
    console.error('头像上传失败:', error)
    ElMessage.error('头像上传失败，请重试')
  } finally {
    uploading.value = false
    uploadProgress.value = 0
  }
}

const handleAvatarError = () => {
  avatarUrl.value = '/media/default.jpg'
}

onMounted(() => {
  loadAvatar()
})
</script>

<style lang="scss" scoped>
.avatar-upload {
  display: inline-block;
  position: relative;
  
  .avatar-container {
    position: relative;
    display: inline-block;
    cursor: pointer;
    
    &:hover .upload-overlay {
      opacity: 1;
    }
    
    .upload-overlay {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.6);
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      opacity: 0;
      transition: opacity 0.3s;
      border-radius: 50%;
      color: white;
      font-size: 12px;
      
      .el-icon {
        font-size: 16px;
        margin-bottom: 4px;
      }
    }
  }
  
  .upload-progress {
    margin-top: 8px;
    width: 100%;
  }
}
</style> 
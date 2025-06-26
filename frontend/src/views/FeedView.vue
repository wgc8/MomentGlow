<template>
  <div class="feed-container">
    <nav-bar />
    <div class="feed-content">
      <div class="feed-header">
        <h1>动态</h1>
        <div class="feed-filters">
          <el-select v-model="selectedMood" placeholder="心情筛选" clearable>
            <el-option
              v-for="item in moodOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 320px;"
            clearable
          />
        </div>
      </div>

      <div v-if="loading" class="loading-state">
        <el-skeleton :rows="3" animated />
      </div>
      
      <div v-else-if="diaries.length === 0" class="empty-state">
        <el-empty description="暂无动态" />
      </div>

      <div v-else class="diary-feed">
        <div class="timeline-scroll">
          <el-timeline>
            <el-timeline-item
              v-for="diary in filteredDiaries"
              :key="diary.id"
              :timestamp="formatDateTime(diary.createdAt)"
              placement="top"
            >
              <el-card class="diary-card">
                <div class="diary-header">
                  <div class="user-info">
                    <el-avatar :size="40" :src="diary.user.avatar || '/default-avatar.png'" />
                    <div class="user-details">
                      <router-link :to="'/profile/' + diary.user.id" class="username">
                        {{ diary.user.username }}
                      </router-link>
                      <span class="mood-tag" :class="'mood-' + diary.mood">
                        {{ getMoodText(diary.mood) }}
                      </span>
                    </div>
                  </div>
                </div>
                <div class="diary-content" v-html="diary.content"></div>
                <div class="diary-footer">
                  <div class="diary-actions">
                    <el-button type="text" @click="handleLike(diary)">
                      <el-icon><Star /></el-icon>
                      {{ diary.likes }}
                    </el-button>
                    <el-button type="text" @click="handleComment(diary)">
                      <el-icon><ChatDotRound /></el-icon>
                      {{ diary.comments }}
                    </el-button>
                  </div>
                </div>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Star, ChatDotRound } from '@element-plus/icons-vue'
import NavBar from '@/components/NavBar.vue'
import { getPublicDiaries, likeDiary } from '@/api/diary'

interface User {
  id: number
  username: string
  avatar: string
}

interface Diary {
  id: number
  content: string
  mood: string
  createdAt: string
  user: User
  likes: number
  comments: number
  isLiked: boolean
}

// 状态
const loading = ref(false)
const loadingMore = ref(false)
const diaries = ref<Diary[]>([])
const page = ref(1)
const hasMore = ref("")
const selectedMood = ref('')
const timeRange = ref('')
const dateRange = ref<[string, string] | []>([])

// 筛选选项
const moodOptions = [
  { label: '开心', value: 'happy' },
  { label: '难过', value: 'sad' },
  { label: '生气', value: 'angry' },
  { label: '平静', value: 'calm' },
  { label: '兴奋', value: 'excited' },
  { label: '焦虑', value: 'anxious' },
  { label: '疲惫', value: 'tired' }
]

// 计算属性
const filteredDiaries = computed(() => {
  let result = [...diaries.value]
  
  if (selectedMood.value) {
    result = result.filter(diary => diary.mood === selectedMood.value)
  }
  
  if (dateRange.value && dateRange.value.length === 2) {
    const [start, end] = dateRange.value
    const startDate = new Date(start)
    const endDate = new Date(end)
    result = result.filter(diary => {
      const diaryDate = new Date(diary.createdAt)
      return diaryDate >= startDate && diaryDate <= endDate
    })
  }
  
  return result
})

// 方法
const loadDiaries = async (isLoadMore = false) => {
  if (isLoadMore) {
    loadingMore.value = true
  } else {
    loading.value = true
  }
  
  try {
    const response = await getPublicDiaries({
      page: page.value,
      mood: selectedMood.value,
      timeRange: timeRange.value
    })
    let diaryInfo = response.data.results
    if (isLoadMore) {
      diaries.value.push(...diaryInfo)
    } else {
      diaries.value = diaryInfo
    }
    
    hasMore.value = response.data.next
    if (hasMore.value) {
      page.value++
    }
  } catch (error) {
    ElMessage.error('加载动态失败')
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

const loadMore = () => {
  loadDiaries(true)
}

const handleLike = async (diary: Diary) => {
  try {
    await likeDiary(diary.id)
    diary.isLiked = !diary.isLiked
    diary.likes += diary.isLiked ? 1 : -1
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const handleComment = (diary: Diary) => {
  // TODO: 实现评论功能
  ElMessage.info('评论功能开发中')
}

const formatDateTime = (dateString: string) => {
  const date = new Date(dateString)
  return `${date.getFullYear()}年${date.getMonth() + 1}月${date.getDate()}日 ${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`
}

const getMoodText = (mood: string) => {
  const moodMap: Record<string, string> = {
    'happy': '开心',
    'sad': '难过',
    'angry': '生气',
    'calm': '平静',
    'excited': '兴奋',
    'anxious': '焦虑',
    'tired': '疲惫'
  }
  return moodMap[mood] || mood
}

// 监听筛选条件变化
watch([selectedMood, timeRange], () => {
  page.value = 1
  loadDiaries()
})

// 新增监听dateRange变化，自动格式化timeRange
watch(dateRange, (val) => {
  if (val && val.length === 2) {
    timeRange.value = `${val[0]},${val[1]}`
  } else {
    timeRange.value = ''
  }
})

// 初始化
onMounted(() => {
  loadDiaries()
})
</script>

<style lang="scss" scoped>
.feed-container {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.feed-content {
  max-width: 800px;
  margin: 80px auto 20px;
  padding: 20px;
}

.feed-header {
  margin-bottom: 30px;
  
  h1 {
    margin: 0 0 20px 0;
    color: #303133;
  }
  
  .feed-filters {
    display: flex;
    gap: 15px;
    
    .el-select {
      width: 150px;
    }
  }
}

.diary-feed {
  .timeline-scroll {
    height: calc(100vh - 180px); // 头部+外边距约80+30+20+50
    min-height: 300px;
    overflow-y: auto;
    padding-right: 8px;
    box-sizing: border-box;
  }
  .diary-card {
    margin-bottom: 20px;
    
    .diary-header {
      margin-bottom: 15px;
      
      .user-info {
        display: flex;
        align-items: center;
        gap: 10px;
        
        .user-details {
          display: flex;
          flex-direction: column;
          
          .username {
            color: #303133;
            text-decoration: none;
            font-weight: 500;
            
            &:hover {
              color: #409EFF;
            }
          }
          
          .mood-tag {
            font-size: 12px;
            padding: 2px 8px;
            border-radius: 10px;
            display: inline-block;
            margin-top: 4px;
            
            &.mood-happy { background-color: #f0f9eb; color: #67c23a; }
            &.mood-sad { background-color: #f4f4f5; color: #909399; }
            &.mood-angry { background-color: #fef0f0; color: #f56c6c; }
            &.mood-calm { background-color: #f4f4f5; color: #909399; }
            &.mood-excited { background-color: #fdf6ec; color: #e6a23c; }
            &.mood-anxious { background-color: #e8f4fd; color: #409EFF; }
            &.mood-tired { background-color: #f3f3f3; color: #b0b0b0; }
          }
        }
      }
    }
    
    .diary-content {
      margin: 15px 0;
      line-height: 1.6;
      color: #303133;
    }
    
    .diary-footer {
      border-top: 1px solid #ebeef5;
      padding-top: 10px;
      
      .diary-actions {
        display: flex;
        gap: 20px;
        
        .el-button {
          display: flex;
          align-items: center;
          gap: 5px;
        }
      }
    }
  }
}

.loading-state {
  padding: 20px;
}

.empty-state {
  padding: 40px 0;
}

// 移动端适配
@media screen and (max-width: 768px) {
  .feed-content {
    padding: 10px;
  }
  
  .feed-header {
    .feed-filters {
      flex-direction: column;
      
      .el-select {
        width: 100%;
      }
    }
  }

  .diary-feed {
    .timeline-scroll {
      height: calc(100vh - 160px);
      min-height: 200px;
    }
  }
}
</style> 
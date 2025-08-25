<template>
  <div class="profile-page">
    <nav-bar />
    <div class="profile-container">
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <p>加载中...</p>
      </div>
      <div v-else class="profile-content">
        <!-- 用户信息部分 -->
        <div class="profile-header">
        <div class="avatar-container">
          <avatar-upload 
            v-if="isOwnProfile" 
            :size="120" 
          />
          <el-avatar 
            v-else 
            :size="120" 
            :src="userInfo.avatar_url || '/media/default.jpg'"
          />
        </div>
        <div class="user-info">
          <div class="username-container">
            <h1 v-if="!editingUsername">{{ userInfo.username }}</h1>
            <div v-else class="edit-field">
              <input v-model="editForm.username" type="text" class="edit-input" />
              <div class="edit-actions">
                <button @click="saveUsername" class="save-btn">保存</button>
                <button @click="cancelEditUsername" class="cancel-btn">取消</button>
              </div>
            </div>
            <button v-if="isOwnProfile && !editingUsername" @click="startEditUsername" class="edit-icon">
              <i class="fas fa-edit"></i>
            </button>
          </div>
          <div class="bio-container">
            <p v-if="!editingBio" class="bio">{{ userInfo.bio || '这个人很懒，什么都没留下...' }}</p>
            <div v-else class="edit-field">
              <textarea v-model="editForm.bio" class="edit-textarea"></textarea>
              <div class="edit-actions">
                <button @click="saveBio" class="save-btn">保存</button>
                <button @click="cancelEditBio" class="cancel-btn">取消</button>
              </div>
            </div>
            <button v-if="isOwnProfile && !editingBio" @click="startEditBio" class="edit-icon">
              <i class="fas fa-edit"></i>
            </button>
          </div>
          <p class="join-date">加入时间：{{ formatDate(userInfo.date_joined) }}</p>
        </div>
      </div>

      <!-- 日记统计日历 -->
      <div class="diary-stats">
        <h2>日记提交记录</h2>
        <div class="calendar">
          <div class="calendar-header">
            <button @click="prevMonth" class="calendar-nav">&lt;</button>
            <h3>{{ currentYear }}年 {{ currentMonth + 1 }}月</h3>
            <button @click="nextMonth" class="calendar-nav">&gt;</button>
          </div>
          <div class="weekdays">
            <div v-for="day in ['日', '一', '二', '三', '四', '五', '六']" :key="day" class="weekday">{{ day }}</div>
          </div>
          <div class="days">
            <div v-for="day in calendarDays" :key="day.date" class="day" :class="getDayClass(day)">
              <span>{{ day.dayOfMonth }}</span>
              <div v-if="day.hasEntry" class="mood-indicator" :class="'mood-' + day.mood"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- 日记列表 -->
      <div class="diary-list">
        <h2>日记列表</h2>
        <div v-if="currentMonthDiaries.length === 0" class="no-diaries">
          <p>暂无日记记录</p>
        </div>
        <div v-else class="diary-entries">
          <div v-for="diary in currentMonthDiaries" :key="diary.id" class="diary-entry">
            <div class="diary-header">
              <div class="diary-date">{{ formatDateTime(diary.created_at) }}</div>
              <div class="diary-mood">心情：{{ getMoodText(diary.mood) }}</div>
              <div v-if="isOwnProfile" class="diary-actions">
                <button @click="editDiary(diary)" class="action-btn edit">编辑</button>
                <button @click="confirmDeleteDiary(diary.id)" class="action-btn delete">删除</button>
              </div>
            </div>
            <div v-if="editingDiaryId === diary.id" class="diary-edit">
              <textarea v-model="diaryEditForm.content" class="diary-edit-content"></textarea>
              <div class="mood-selector">
                <label>心情：</label>
                <select v-model="diaryEditForm.mood">
                  <option value="happy">开心</option>
                  <option value="sad">难过</option>
                  <option value="angry">生气</option>
                  <option value="neutral">平静</option>
                  <option value="excited">兴奋</option>
                </select>
              </div>
              <div class="diary-edit-actions">
                <button @click="saveDiaryEdit" class="save-btn">保存</button>
                <button @click="cancelDiaryEdit" class="cancel-btn">取消</button>
              </div>
            </div>
            <div v-else class="diary-content">{{ diary.title }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 确认删除对话框 -->
    <div v-if="showDeleteConfirm" class="delete-confirm-modal">
      <div class="modal-content">
        <h3>确认删除</h3>
        <p>确定要删除这条日记吗？此操作无法撤销。</p>
        <div class="modal-actions">
          <button @click="deleteDiaryConfirmed" class="confirm-btn">确认删除</button>
          <button @click="cancelDeleteDiary" class="cancel-btn">取消</button>
        </div>
      </div>
    </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { getUserInfo,  updateUserInfo} from '@/api/user'
import { getDiaries} from '@/api/diary'
import http from '@/utils/http'
import type { DiaryInfo } from '@/api/diary'
import type { UserInfo } from '@/api/user'
import NavBar from '@/components/NavBar.vue'
import AvatarUpload from '@/components/AvatarUpload.vue'
import { ElMessage, ElMessageBox } from 'element-plus'


const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// 获取路由中的用户ID，如果没有则使用当前登录用户的ID
const profileUserId = computed(() => {
  const routeId = Number(route.params.id)
  return isNaN(routeId) ? userStore.userId : routeId
})

// 判断是否是查看自己的主页
const isOwnProfile = computed(() => profileUserId.value === userStore.userId)

// 用户信息
const userInfo = ref<UserInfo>({
  id: 0,
  username: '',
  email: '',
  date_joined: '',
  bio: '',
})

// 日记列表（直接使用当月日记）
const diaryStats = ref<DiaryInfo[]>([])
const currentMonthDiaries = ref<DiaryInfo[]>([])

// 加载状态
const loading = ref(true)

// 编辑状态
const editingUsername = ref(false)
const editingBio = ref(false)
const editForm = reactive({
  username: '',
  bio: ''
})

// 日记编辑状态
const editingDiaryId = ref<number | null>(null)
const diaryEditForm = reactive({
  content: '',
  mood: ''
})

// 删除确认
const showDeleteConfirm = ref(false)
const diaryToDelete = ref<number | null>(null)

// 日历相关
const currentDate = ref(new Date())
const currentYear = computed(() => currentDate.value.getFullYear())
const currentMonth = computed(() => currentDate.value.getMonth())

// 获取当前月的所有日记记录（循环处理分页）
const loadCurrentMonthDiaries = async (userId: number, year: number, month: number) => {
  try {
    const startDate = `${year}-${String(month + 1).padStart(2, '0')}-01`
    // 使用本地时间计算月末日期，避免时区问题
    const endDate = `${year}-${String(month + 1).padStart(2, '0')}-${new Date(year, month + 1, 0).getDate()}`
    
    // 初始化日记数组和分页URL
    let allDiaries: DiaryInfo[] = []
    let nextUrl: string | null = null
    
    // 获取第一页数据
    const firstResponse = await getDiaries({
      user_id: userId.toString(),
      timeRange: `${startDate},${endDate}`,
      page: 1
    })
    
    const firstData = firstResponse.data
    allDiaries.push(...firstData.results)
    nextUrl = firstData.next
    
    // 循环获取后续页面的数据
    while (nextUrl) {
      try {
        const response = await http.get(nextUrl)
        const data: any = response.data
        allDiaries.push(...data.results)
        nextUrl = data.next
      } catch (error) {
        console.error('获取分页数据失败:', error)
        break
      }
    }
    
    currentMonthDiaries.value = allDiaries
  } catch (error) {
    console.error('加载当月日记失败:', error)
    currentMonthDiaries.value = []
  }
}

// 加载用户数据
const loadUserData = async () => {
  try {
    loading.value = true
    if (profileUserId.value) {
      const [userInfoData] = await Promise.all([
        getUserInfo(profileUserId.value),
      ])
      
      userInfo.value = userInfoData
      
      // 加载当前月的日记记录
      await loadCurrentMonthDiaries(profileUserId.value, currentYear.value, currentMonth.value)
      

    }
  } catch (error) {
    console.error('加载用户数据失败:', error)
  } finally {
    loading.value = false
  }
}

// 编辑用户名
const startEditUsername = () => {
  editForm.username = userInfo.value.username
  editingUsername.value = true
}

const saveUsername = async () => {
  if (editForm.username.trim() && isOwnProfile.value) {
    try {
      await updateUserInfo(userInfo.value.id, { username: editForm.username })
      userInfo.value.username = editForm.username
      editingUsername.value = false
    } catch (error) {
      console.error('更新用户名失败:', error)
    }
  }
}

const cancelEditUsername = () => {
  editingUsername.value = false
}

// 编辑个人简介
const startEditBio = () => {
  editForm.bio = userInfo.value.bio || ''
  editingBio.value = true
}

const saveBio = async () => {
  if (isOwnProfile.value) {
    try {
      await updateUserInfo(userInfo.value.id, { bio: editForm.bio })
      userInfo.value.bio = editForm.bio
      editingBio.value = false
    } catch (error) {
      console.error('更新个人简介失败:', error)
    }
  }
}

const cancelEditBio = () => {
  editingBio.value = false
}

// 编辑日记
const editDiary = (diary: DiaryInfo) => {
  diaryEditForm.content = diary.content
  diaryEditForm.mood = diary.mood
  editingDiaryId.value = diary.id
}

const saveDiaryEdit = async () => {
  // if (editingDiaryId.value && isOwnProfile.value) {
  //   try {
  //     await updateDiary(editingDiaryId.value, diaryEditForm.content, diaryEditForm.mood)
      
  //     // 更新本地数据
  //     const index = diaries.value.findIndex(d => d.id === editingDiaryId.value)
  //     if (index !== -1) {
  //       diaries.value[index].content = diaryEditForm.content
  //       diaries.value[index].mood = diaryEditForm.mood
  //     }
      
  //     editingDiaryId.value = null
      
  //     // 重新加载日记统计数据
  //     diaryStats.value = await getUserDiaryStats(profileUserId.value!)
  //   } catch (error) {
  //     console.error('更新日记失败:', error)
  //   }
  // }
}

const cancelDiaryEdit = () => {
  editingDiaryId.value = null
}

// 删除日记
const confirmDeleteDiary = (id: number) => {
  diaryToDelete.value = id
  showDeleteConfirm.value = true
}

const deleteDiaryConfirmed = async () => {
  // if (diaryToDelete.value && isOwnProfile.value) {
  //   try {
  //     await deleteDiary(diaryToDelete.value)
      
  //     // 从列表中移除
  //     diaries.value = diaries.value.filter(d => d.id !== diaryToDelete.value)
      
  //     // 重新加载日记统计数据
  //     diaryStats.value = await getUserDiaryStats(profileUserId.value!)
      
  //     showDeleteConfirm.value = false
  //     diaryToDelete.value = null
  //   } catch (error) {
  //     console.error('删除日记失败:', error)
  //   }
  // }
}

const cancelDeleteDiary = () => {
  showDeleteConfirm.value = false
  diaryToDelete.value = null
}

// 日历相关方法
const prevMonth = async () => {
  const newDate = new Date(currentDate.value)
  newDate.setMonth(newDate.getMonth() - 1)
  currentDate.value = newDate
  
  // 重新加载该月的日记记录
  if (profileUserId.value) {
    await loadCurrentMonthDiaries(profileUserId.value, currentYear.value, currentMonth.value)
  }
}

const nextMonth = async () => {
  const newDate = new Date(currentDate.value)
  newDate.setMonth(newDate.getMonth() + 1)
  currentDate.value = newDate
  
  // 重新加载该月的日记记录
  if (profileUserId.value) {
    await loadCurrentMonthDiaries(profileUserId.value, currentYear.value, currentMonth.value)
  }
}

const calendarDays = computed(() => {
  const year = currentYear.value
  const month = currentMonth.value
  
  // 获取当月第一天
  const firstDay = new Date(year, month, 1)
  // 获取当月最后一天
  const lastDay = new Date(year, month + 1, 0)
  
  // 当月第一天是星期几（0为周日，6为周六）
  const firstDayOfWeek = firstDay.getDay()
  
  // 当月总天数
  const daysInMonth = lastDay.getDate()
  
  // 创建日历数据
  const days = []
  
  // 添加上月末尾的几天
  for (let i = 0; i < firstDayOfWeek; i++) {
    const prevMonthLastDay = new Date(year, month, 0)
    const day = prevMonthLastDay.getDate() - firstDayOfWeek + i + 1
    days.push({
      date: `${year}-${month === 0 ? 12 : month}-${day}`,
      dayOfMonth: day,
      isCurrentMonth: false,
      hasEntry: false
    })
  }
  
  // 添加当月的天数
  for (let i = 1; i <= daysInMonth; i++) {
    const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(i).padStart(2, '0')}`
    
    // 检查当天是否有日记
    const hasEntry = currentMonthDiaries.value.some(diary => {
      const diaryDate = new Date(diary.created_at)
      // 使用本地时间，避免时区问题
      const diaryDateStr = `${diaryDate.getFullYear()}-${String(diaryDate.getMonth() + 1).padStart(2, '0')}-${String(diaryDate.getDate()).padStart(2, '0')}`
      
      // 调试信息：打印日期比较
      if (currentMonthDiaries.value.length > 0) {
        console.log(`比较日期: 日历日期=${dateStr}, 日记日期=${diaryDateStr}, 原始日记时间=${diary.created_at}`)
      }
      
      return diaryDateStr === dateStr
    })
    
    days.push({
      date: dateStr,
      dayOfMonth: i,
      isCurrentMonth: true,
      hasEntry: hasEntry,
      mood: hasEntry ? currentMonthDiaries.value.find(diary => {
        const diaryDate = new Date(diary.created_at)
        // 使用本地时间，避免时区问题
        const diaryDateStr = `${diaryDate.getFullYear()}-${String(diaryDate.getMonth() + 1).padStart(2, '0')}-${String(diaryDate.getDate()).padStart(2, '0')}`
        return diaryDateStr === dateStr
      })?.mood || 'neutral' : 'neutral'
    })
  }
  
  // 添加下月开始的几天以填满6行
  const remainingDays = 42 - days.length
  for (let i = 1; i <= remainingDays; i++) {
    days.push({
      date: `${year}-${month === 11 ? 1 : month + 2}-${i}`,
      dayOfMonth: i,
      isCurrentMonth: false,
      hasEntry: false
    })
  }
  
  return days
})

const getDayClass = (day: any) => {
  return {
    'current-month': day.isCurrentMonth,
    'other-month': !day.isCurrentMonth,
    'has-entry': day.hasEntry
  }
}

// 工具函数
const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return `${date.getFullYear()}年${date.getMonth() + 1}月${date.getDate()}日`
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
    'neutral': '平静',
    'excited': '兴奋'
  }
  return moodMap[mood] || mood
}

// 初始化
onMounted(() => {
  loadUserData()
})
</script>

<style scoped>
.profile-page {
  height: 100vh;
  overflow-y: auto;
  background-color: #f5f7fa;
  position: relative;
  -webkit-overflow-scrolling: touch;
}

/* 确保滚动条样式 */
.profile-page::-webkit-scrollbar {
  width: 8px;
}

.profile-page::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.profile-page::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

.profile-page::-webkit-scrollbar-thumb:hover {
  background: #555;
}

.profile-container {
  max-width: 900px;
  margin: 80px auto 20px;
  padding: 20px;
  padding-bottom: 40px;
  overflow: visible;
}

.profile-content {
  overflow: visible;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  border-top-color: #3498db;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.profile-header {
  display: flex;
  margin-bottom: 30px;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 10px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.avatar-container {
  position: relative;
  margin-right: 30px;
}

.avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
}

.avatar-edit {
  position: absolute;
  bottom: 0;
  right: 0;
  background: rgba(0,0,0,0.6);
  border-radius: 50%;
  padding: 5px;
}

.edit-btn {
  background: none;
  border: none;
  color: white;
  font-size: 12px;
  cursor: pointer;
}

.user-info {
  flex: 1;
}

.username-container, .bio-container {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.edit-icon {
  background: none;
  border: none;
  color: #666;
  margin-left: 10px;
  cursor: pointer;
}

.edit-field {
  width: 100%;
}

.edit-input, .edit-textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.edit-textarea {
  min-height: 100px;
}

.edit-actions {
  margin-top: 10px;
}

.save-btn, .cancel-btn {
  padding: 5px 10px;
  margin-right: 10px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.save-btn {
  background-color: #4CAF50;
  color: white;
}

.cancel-btn {
  background-color: #f44336;
  color: white;
}

.join-date {
  color: #666;
  font-size: 14px;
}

.diary-stats {
  margin-bottom: 30px;
}

.calendar {
  background-color: white;
  border-radius: 10px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  padding: 15px;
}

.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.calendar-nav {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
}

.weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  text-align: center;
  font-weight: bold;
  margin-bottom: 10px;
}

.days {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 5px;
}

.day {
  height: 40px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: 5px;
  position: relative;
}

.current-month {
  background-color: #f8f9fa;
}

.other-month {
  background-color: #eee;
  color: #aaa;
}

.has-entry {
  font-weight: bold;
  background-color: #4CAF50 !important;
  color: white !important;
}

.mood-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  position: absolute;
  bottom: 5px;
}

.mood-happy { background-color: #4CAF50; }
.mood-sad { background-color: #2196F3; }
.mood-angry { background-color: #f44336; }
.mood-neutral { background-color: #9E9E9E; }
.mood-excited { background-color: #FF9800; }

.diary-list {
  margin-top: 30px;
}

.no-diaries {
  text-align: center;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 10px;
}

.diary-entries {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.diary-entry {
  background-color: white;
  border-radius: 10px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  padding: 15px;
}

.diary-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.diary-date, .diary-mood {
  color: #666;
  font-size: 14px;
}

.diary-actions {
  display: flex;
  gap: 10px;
}

.action-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 14px;
}

.action-btn.edit {
  color: #2196F3;
}

.action-btn.delete {
  color: #f44336;
}

.diary-content {
  white-space: pre-line;
}

.diary-edit {
  margin-top: 15px;
}

.diary-edit-content {
  width: 100%;
  min-height: 100px;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin-bottom: 10px;
}

.mood-selector {
  margin-bottom: 10px;
}

.diary-edit-actions {
  display: flex;
  gap: 10px;
}

.delete-confirm-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  padding: 20px;
  border-radius: 10px;
  width: 400px;
  max-width: 90%;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.confirm-btn {
  background-color: #f44336;
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 4px;
  cursor: pointer;
}
</style> 
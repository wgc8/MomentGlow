<template>
  <div class="diary-container">
    <nav-bar />
    <el-container>
      <!-- 在移动端隐藏侧边栏，通过抽屉显示 -->
      <el-drawer
        v-model="showSidebar"
        direction="ltr"
        size="80%"
        :with-header="false"
        class="diary-drawer"
      >
        <diary-list
          :diaries="diaryList"
          :selected-id="selectedDiaryId"
          @select="selectDiary"
          @create="createNewDiary"
        />
      </el-drawer>

      <!-- 桌面端显示侧边栏 -->
      <el-aside width="250px" class="desktop-sidebar">
        <div class="diary-list">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索日记..."
            prefix-icon="Search"
            clearable
          />
          <el-button type="primary" class="new-diary-btn" @click="createNewDiary">
            <el-icon><Plus /></el-icon>新建日记
          </el-button>
          <el-scrollbar height="calc(100vh - 120px)">
            <el-timeline>
              <el-timeline-item
                v-for="diary in diaryList"
                :key="diary.id"
                :timestamp="diary.date"
                placement="top"
              >
                <el-card 
                  :class="{ 'diary-card': true, 'active': selectedDiaryId === diary.id }"
                  @click="selectDiary(diary.id)"
                >
                  <h4>{{ diary.title }}</h4>
                  <p>{{ diary.preview }}</p>
                </el-card>
              </el-timeline-item>
            </el-timeline>
          </el-scrollbar>
        </div>
      </el-aside>

      <el-main>
        <!-- 移动端顶部工具栏 -->
        <div class="mobile-header">
          <el-button @click="showSidebar = true">
            <el-icon><Menu /></el-icon>
          </el-button>
          <span class="mobile-title">{{ currentDiary.title || '新日记' }}</span>
        </div>

        <div v-if="selectedDiaryId" class="editor-wrapper">
          <diary-editor
            v-model="currentDiary"
            :readonly="!isEdit"
            @edit="handleEdit"
            @save="saveDiary"
            @delete="deleteDiary"
          />
        </div>
        <div class="empty-state" v-else>
          <el-empty description="选择或创建一篇日记开始写作">
            <el-button type="primary" @click="createNewDiary">
              <el-icon><Plus /></el-icon>新建日记
            </el-button>
          </el-empty>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Search, Menu } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import DiaryList from '../components/DiaryList.vue'
import DiaryEditor from '../components/DiaryEditor.vue'
import NavBar from '../components/NavBar.vue'
import { useUserStore } from '@/store/user'
import { publishDiary as apiPublishDiary, deleteDiary as apiDeleteDiary, getDiaries as apiGetDiaries } from '@/api/diary'
import type { DiaryInput, GetDiariesRequestParams } from '@/api/diary'

const router = useRouter()
const userStore = useUserStore()

// 响应式状态
const showSidebar = ref(false)
const searchKeyword = ref('')
const selectedDiaryId = ref<number | null>(null)
const currentDiary = ref({
  title: '',
  content: '',
  weather: '',
  mood: '',
  isPublic: false
})
const isEdit = ref(false)

// 日记列表数据
interface Diary {
  id: number
  title: string
  preview: string
  date: string
  content: string
  weather?: string
  mood?: string
  isPublic?: boolean
}

const diaryList = ref<Diary[]>([])

// 方法
const createNewDiary = () => {
  const newDiary = {
    id: Date.now(),
    title: '新日记',
    preview: '',
    date: new Date().toISOString().split('T')[0],
    content: '',
    weather: '',
    mood: '',
    isPublic: false
  }
  //TODO： 这里还是临时添加一个框的交互效果更好一点。但是会导致一个问题，成功创建新的日记之后，临时添加的“新日记”也在列表中
  diaryList.value.unshift(newDiary)
  selectedDiaryId.value = newDiary.id
  currentDiary.value = { 
    title: newDiary.title, 
    content: '',
    weather: '',
    mood: '',
    isPublic: false
  }
  showSidebar.value = false
  isEdit.value = true
}

const selectDiary = (id: number) => {
  selectedDiaryId.value = id
  const diary = diaryList.value.find(d => d.id === id)
  if (diary) {
    currentDiary.value = { 
      title: diary.title,
      content: diary.content,
      weather: diary.weather || '',
      mood: diary.mood || '',
      isPublic: diary.isPublic || false
    }
  }
  showSidebar.value = false
  isEdit.value = false
}

const handleEdit = () => {
  isEdit.value = true
}

const saveDiary = async () => {
  const index = diaryList.value.findIndex(d => d.id === selectedDiaryId.value)
  if (index > -1) {
    const preview = currentDiary.value.content
      .replace(/<[^>]+>/g, '')
      .slice(0, 50)
      .replace(/\n/g, ' ') + '...'
    
    let diaryInput: DiaryInput = {
      id: diaryList.value[index].id,
      title: currentDiary.value.title,
      content: currentDiary.value.content,
      mood: currentDiary.value.mood,
      weather: currentDiary.value.weather,
      is_public: currentDiary.value.isPublic,
      user: {
        id: userStore.userId?.toString() || '',
        username: userStore.username,
      }
    }

    const res = await apiPublishDiary(diaryInput)
    if (res && res.data) {
      // 清除临时日记对象
      diaryList.value.shift();
      // 更新本地日记列表
      diaryList.value.unshift( {
        ...res.data,
        preview: res.data.content.replace(/<[^>]+>/g, '').slice(0, 50) + '...',
        date: res.data.created_at ? res.data.created_at.split('T')[0] : ''
      })
      // 弹窗提示保存成功
      ElMessage.success('保存成功')
      isEdit.value = false
    }
  }
}

const deleteDiary = () => {
  const index = diaryList.value.findIndex(d => d.id === selectedDiaryId.value)
  if (index > -1) {
    diaryList.value.splice(index, 1)
    selectedDiaryId.value = null
    currentDiary.value = { 
      title: '', 
      content: '',
      weather: '',
      mood: '',
      isPublic: false
    }
    ElMessage.success('删除成功')
  }
}
// 获取历史日记数据
const loadDiaries = async (isLoadMore = false) => {
  try {
    let params : GetDiariesRequestParams = {
      user_id: userStore.userId?.toString() || ''
    }
    const response = await apiGetDiaries(params)
    if (response && response.data && Array.isArray(response.data)) {
      diaryList.value = response.data.map((item: any) => ({
        ...item,
        preview: item.content.replace(/<[^>]+>/g, '').slice(0, 50) + '...',
        date: item.created_at ? item.created_at.split('T')[0] : ''
      })) 
  } else{
      diaryList.value = []
    }
  } catch (error) {
    ElMessage.error('加载日记失败')
    diaryList.value = []
  }
}

// 初始化
onMounted(() => {
  loadDiaries()
})
</script>

<style lang="scss" scoped>
.diary-container {
  height: 100vh;
  padding-top: 80px;
  
  .el-aside {
    border-right: 1px solid #dcdfe6;
    background-color: #f5f7fa;
    height: calc(100vh - 60px);
    
    .diary-list {
      padding: 20px;
      
      .new-diary-btn {
        width: 100%;
        margin: 15px 0;
      }
      
      .diary-card {
        cursor: pointer;
        margin-bottom: 10px;
        transition: all 0.3s;
        
        &:hover {
          transform: translateY(-2px);
          box-shadow: 0 2px 12px 0 rgba(0,0,0,.1);
        }
        
        &.active {
          border-color: var(--el-color-primary);
        }
        
        h4 {
          margin: 0 0 10px 0;
        }
        
        p {
          margin: 0;
          font-size: 12px;
          color: #666;
        }
      }
    }
  }
  
  .el-main {
    padding: 0;
    display: flex;
    flex-direction: column;
    height: calc(100vh - 116px);

    .editor-wrapper {
      flex: 1;
      display: flex;
      flex-direction: column;
      height: 100%;
    }
    
    .empty-state {
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
    }
  }
}

// 桌面端适配
@media screen and (min-width: 769px) {
  .mobile-header {
    display: none !important;
  }
}

// 移动端适配
@media screen and (max-width: 768px) {
  .diary-container {
    .desktop-sidebar {
      display: none;
    }

    .mobile-header {
      display: flex;
      align-items: center;
      padding: 10px;
      border-bottom: 1px solid #dcdfe6;
      background-color: #fff;
      justify-content: space-between;

      .mobile-title {
        margin-left: 10px;
        font-size: 16px;
        font-weight: 500;
      }
    }

    .el-main {
      padding: 0;

      .editor-wrapper {
        height: calc(100vh - 116px);
      }
    }
  }
}

:deep(.diary-drawer) {
  .el-drawer__body {
    padding: 0;
  }
}
</style> 
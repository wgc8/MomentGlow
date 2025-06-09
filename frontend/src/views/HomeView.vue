<template>
  <div class="diary-container">
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
          <div class="user-info">
            <span>欢迎，{{ username }}</span>
            <el-button type="text" @click="handleLogout">退出登录</el-button>
          </div>
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
          <el-button type="text" @click="handleLogout">退出</el-button>
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
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Search, Menu } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import DiaryList from '../components/DiaryList.vue'
import DiaryEditor from '../components/DiaryEditor.vue'
import { useUserStore } from '@/store/user'

const router = useRouter()
const userStore = useUserStore()

// 响应式状态
const showSidebar = ref(false)
const searchKeyword = ref('')
const selectedDiaryId = ref<number | null>(null)
const currentDiary = ref({
  title: '',
  content: ''
})
const isEdit = ref(false)
const username = ref(userStore.username)

// 模拟日记列表数据
const diaryList = ref([
  {
    id: 1,
    title: '今天的心情',
    preview: '今天天气很好，我去公园散步...',
    date: '2024-01-20',
    content: ''
  }
])

// 方法
const createNewDiary = () => {
  const newDiary = {
    id: Date.now(),
    title: '新日记',
    preview: '',
    date: new Date().toISOString().split('T')[0],
    content: ''
  }
  diaryList.value.unshift(newDiary)
  selectedDiaryId.value = newDiary.id
  currentDiary.value = { title: newDiary.title, content: '' }
  showSidebar.value = false
  isEdit.value = true
}

const selectDiary = (id: number) => {
  selectedDiaryId.value = id
  const diary = diaryList.value.find(d => d.id === id)
  if (diary) {
    currentDiary.value = { 
      title: diary.title,
      content: diary.content
    }
  }
  showSidebar.value = false
  isEdit.value = false
}

const handleEdit = () => {
  isEdit.value = true
}

const saveDiary = () => {
  const index = diaryList.value.findIndex(d => d.id === selectedDiaryId.value)
  if (index > -1) {
    const preview = currentDiary.value.content
      .replace(/<[^>]+>/g, '')
      .slice(0, 50)
      .replace(/\n/g, ' ') + '...'
    
    diaryList.value[index] = {
      ...diaryList.value[index],
      title: currentDiary.value.title,
      content: currentDiary.value.content,
      preview
    }
    ElMessage.success('保存成功')
    isEdit.value = false
  }
}

const deleteDiary = () => {
  const index = diaryList.value.findIndex(d => d.id === selectedDiaryId.value)
  if (index > -1) {
    diaryList.value.splice(index, 1)
    selectedDiaryId.value = null
    currentDiary.value = { title: '', content: '' }
    ElMessage.success('删除成功')
  }
}

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}
</script>

<style lang="scss" scoped>
.diary-container {
  height: 100vh;
  
  .el-aside {
    border-right: 1px solid #dcdfe6;
    background-color: #f5f7fa;
    
    .diary-list {
      padding: 20px;
      
      .user-info {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
        padding-bottom: 10px;
        border-bottom: 1px solid #dcdfe6;
      }
      
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
    padding: 20px;
    display: flex;
    flex-direction: column;
    
    .editor-wrapper {
      flex: 1;
      display: flex;
      flex-direction: column;
      height: calc(100vh - 40px);
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
        height: calc(100vh - 56px);
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
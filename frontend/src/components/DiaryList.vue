<template>
  <div class="diary-list">
    <el-input
      v-model="searchKeyword"
      placeholder="搜索日记..."
      prefix-icon="Search"
      clearable
      @input="handleSearch"
    />
    <el-button type="primary" class="new-diary-btn" @click="$emit('create')">
      <el-icon><Plus /></el-icon>新建日记
    </el-button>
    <el-scrollbar height="calc(100vh - 120px)">
      <el-timeline>
        <el-timeline-item
          v-for="diary in filteredDiaries"
          :key="diary.id"
          :timestamp="diary.date"
          placement="top"
        >
          <el-card 
            :class="{ 'diary-card': true, 'active': selectedId === diary.id }"
            @click="$emit('select', diary.id)"
          >
            <h4>{{ diary.title }}</h4>
            <p>{{ diary.preview }}</p>
          </el-card>
        </el-timeline-item>
      </el-timeline>
    </el-scrollbar>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Plus, Search } from '@element-plus/icons-vue'

interface Diary {
  id: number
  title: string
  preview: string
  date: string
  content: string
}

const props = defineProps<{
  diaries: Diary[]
  selectedId: number | null
}>()

const emit = defineEmits<{
  (e: 'select', id: number): void
  (e: 'create'): void
}>()

const searchKeyword = ref('')

const filteredDiaries = computed(() => {
  if (!searchKeyword.value) return props.diaries
  const keyword = searchKeyword.value.toLowerCase()
  return props.diaries.filter(diary => 
    diary.title.toLowerCase().includes(keyword) || 
    diary.preview.toLowerCase().includes(keyword)
  )
})

const handleSearch = () => {
  // 可以在这里添加防抖处理
}
</script>

<style lang="scss" scoped>
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
</style> 
<template>
  <div class="diary-editor">
    <div class="editor-header">
      <div class="editor-info">
      <el-input
        v-model="title"
        placeholder="日记标题"
        class="title-input"
        @input="handleTitleChange"
        :disabled="readonly"
      />
        <div class="weather-mood">
          <el-select
            v-model="weather"
            placeholder="选择天气"
            :disabled="readonly"
            @change="handleWeatherChange"
            class="weather-select"
          >
            <el-option label="晴天" value="sunny" />
            <el-option label="多云" value="cloudy" />
            <el-option label="阴天" value="overcast" />
            <el-option label="小雨" value="light-rain" />
            <el-option label="大雨" value="heavy-rain" />
            <el-option label="雪" value="snow" />
            <el-option label="雾" value="fog" />
          </el-select>
          <el-select
            v-model="mood"
            placeholder="选择心情"
            :disabled="readonly"
            @change="handleMoodChange"
            class="mood-select"
          >
            <el-option label="开心" value="happy" />
            <el-option label="平静" value="calm" />
            <el-option label="兴奋" value="excited" />
            <el-option label="难过" value="sad" />
            <el-option label="生气" value="angry" />
            <el-option label="焦虑" value="anxious" />
            <el-option label="疲惫" value="tired" />
          </el-select>
          <el-switch
            v-model="isPublic"
            :disabled="readonly"
            @change="handlePublicChange"
            active-text="公开"
            inactive-text="私密"
            class="public-switch"
          />
        </div>
      </div>
      <div class="editor-actions">
        <el-button v-if="readonly" @click="emit('edit')">
          <el-icon><Edit /></el-icon>
          <span class="button-text">修改</span>
        </el-button>
        <el-button v-else type="primary" @click="handleSave">
          <el-icon><Check /></el-icon>
          <span class="button-text">保存</span>
        </el-button>
        <el-button v-if="!readonly" type="danger" @click="handleDelete">
          <el-icon><Delete /></el-icon>
          <span class="button-text">删除</span>
        </el-button>
      </div>
    </div>
    <div ref="editorContainer" class="editor-content"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Check, Delete, Edit } from '@element-plus/icons-vue'
import Quill from 'quill'
import 'quill/dist/quill.snow.css'

const props = defineProps<{
  modelValue: {
    title: string
    content: string
    weather: string
    mood: string
    isPublic: boolean
  },
  readonly?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: { title: string, content: string, weather: string, mood: string, isPublic: boolean }): void
  (e: 'save'): void
  (e: 'delete'): void
  (e: 'edit'): void
}>()

const title = ref(props.modelValue.title)
const weather = ref(props.modelValue.weather)
const mood = ref(props.modelValue.mood)
const isPublic = ref(props.modelValue.isPublic)
const editorContainer = ref<HTMLElement | null>(null)
let editor: Quill | null = null

// 监听属性变化
watch(() => props.modelValue, (newVal) => {
  if (newVal.title !== title.value) {
    title.value = newVal.title
  }
  if (editor && newVal.content !== editor.root.innerHTML) {
    editor.root.innerHTML = newVal.content
  }
}, { deep: true })

// 初始化编辑器
const initEditor = () => {
  if (editorContainer.value) {
    const toolbarOptions = window.innerWidth > 768 ? [
      ['bold', 'italic', 'underline', 'strike'],
      ['blockquote', 'code-block'],
      [{ 'header': 1 }, { 'header': 2 }],
      [{ 'list': 'ordered'}, { 'list': 'bullet' }],
      [{ 'script': 'sub'}, { 'script': 'super' }],
      [{ 'indent': '-1'}, { 'indent': '+1' }],
      [{ 'size': ['small', false, 'large', 'huge'] }],
      [{ 'header': [1, 2, 3, 4, 5, 6, false] }],
      [{ 'color': [] }, { 'background': [] }],
      [{ 'font': [] }],
      [{ 'align': [] }],
      ['clean'],
      ['link', 'image']
    ] : [
      ['bold', 'italic'],
      [{ 'list': 'ordered'}, { 'list': 'bullet' }],
      [{ 'color': [] }],
      ['clean']
    ]

    editor = new Quill(editorContainer.value, {
      modules: {
        toolbar: toolbarOptions
      },
      theme: 'snow',
      placeholder: '开始写下今天的故事...'
    })

    // 设置初始内容
    editor.root.innerHTML = props.modelValue.content

    // 设置初始状态
    editor.enable(!props.readonly)
    const toolbar = editorContainer.value.querySelector('.ql-toolbar') as HTMLElement
    if (toolbar) {
      toolbar.style.display = props.readonly ? 'none' : 'block'
    }

    // 监听内容变化
    editor.on('text-change', () => {
      if (editor && !props.readonly) {
        emit('update:modelValue', {
          title: title.value,
          content: editor.root.innerHTML,
          weather: weather.value,
          mood: mood.value,
          isPublic: isPublic.value
        })
      }
    })
  }
}

// 监听只读状态变化
watch(() => props.readonly, (val) => {
  if (editor) {
    editor.enable(!val)
    const toolbar = editorContainer.value?.querySelector('.ql-toolbar') as HTMLElement
    if (toolbar) {
      toolbar.style.display = val ? 'none' : 'block'
    }
  }
}, { immediate: true })

// 标题变化处理
const handleTitleChange = () => {
  emit('update:modelValue', {
    title: title.value,
    content: editor?.root.innerHTML || '',
    weather: weather.value,
    mood: mood.value,
    isPublic: isPublic.value
  })
}

// 保存处理
const handleSave = () => {
  emit('save')
}

// 删除处理
const handleDelete = () => {
  emit('delete')
}

// 天气变化处理
const handleWeatherChange = () => {
  emit('update:modelValue', {
    title: title.value,
    content: editor?.root.innerHTML || '',
    weather: weather.value,
    mood: mood.value,
    isPublic: isPublic.value
  })
}

// 心情变化处理
const handleMoodChange = () => {
  emit('update:modelValue', {
    title: title.value,
    content: editor?.root.innerHTML || '',
    weather: weather.value,
    mood: mood.value,
    isPublic: isPublic.value
  })
}

// 公开状态变化处理
const handlePublicChange = () => {
  emit('update:modelValue', {
    title: title.value,
    content: editor?.root.innerHTML || '',
    weather: weather.value,
    mood: mood.value,
    isPublic: isPublic.value
  })
}

// 生命周期钩子
onMounted(() => {
  initEditor()
})

onBeforeUnmount(() => {
  editor = null
})
</script>

<style lang="scss" scoped>
.diary-editor {
  display: flex;
  flex-direction: column;
  height: 100%;

  .editor-header {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-bottom: 10px;
    
    .editor-info {
      display: flex;
    align-items: center;
      gap: 10px;
      width: 100%;
    
    .title-input {
      width: 300px;
        flex-shrink: 0;
      }
      
      .weather-mood {
        display: flex;
        gap: 10px;
        flex: 1;
        
        .weather-select,
        .mood-select {
          width: 120px;
        }
        
        .public-switch {
          margin-left: 10px;
        }
      }
    }
    
    .editor-actions {
      display: flex;
      gap: 10px;
      justify-content: flex-end;
    }
  }

  .editor-content {
    flex: 1 1 0%;
    min-height: 0;
    max-height: 100%;
    display: flex;
    flex-direction: column;
    border: 1px solid #dcdfe6;
    border-radius: 4px;
    position: relative;
    overflow: hidden;

    :deep(.ql-toolbar) {
      flex-shrink: 0;
    }

    :deep(.ql-container) {
      flex: 1 1 0%;
      display: flex;
      flex-direction: column;
      height: 0;
      min-height: 0;
      border: none;
    }

    :deep(.ql-editor) {
      flex: 1 1 0%;
      overflow-y: auto;
      height: 0;
      min-height: 0;
      padding: 12px 20px;
      
      &.ql-blank::before {
        font-style: normal;
        color: #999;
      }
    }
  }
}

// 移动端适配
@media screen and (max-width: 768px) {
  .diary-editor {
    height: 100%; // 使用100%高度，因为父容器已经处理了布局
    
    .editor-header {
      padding: 10px;
      gap: 10px;

      .editor-info {
        flex-direction: column;
        align-items: stretch;

      .title-input {
        width: 100%;
        }
        
        .weather-mood {
          width: 100%;
          flex-direction: column;
          
          .weather-select,
          .mood-select {
            width: 100%;
          }
        }
      }

      .editor-actions {
        width: 100%;
        justify-content: flex-end;
      }
    }

    .button-text {
      display: none;
    }
  }
}
</style> 
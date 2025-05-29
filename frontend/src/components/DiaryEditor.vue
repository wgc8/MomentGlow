<template>
  <div class="diary-editor">
    <div class="editor-header">
      <el-input
        v-model="title"
        placeholder="日记标题"
        class="title-input"
        @input="handleTitleChange"
        :disabled="readonly"
      />
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
  },
  readonly?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: { title: string, content: string }): void
  (e: 'save'): void
  (e: 'delete'): void
  (e: 'edit'): void
}>()

const title = ref(props.modelValue.title)
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
          content: editor.root.innerHTML
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
    content: editor?.root.innerHTML || ''
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
  height: 95vh;

  .editor-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    
    .title-input {
      width: 300px;
    }
    
    .editor-actions {
      display: flex;
      gap: 10px;
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
    .editor-header {
      padding: 10px;
      flex-wrap: wrap;
      gap: 10px;

      .title-input {
        width: 100%;
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
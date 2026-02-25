<template>
  <div class="post-composer">
    <el-input
      v-model="content"
      type="textarea"
      :rows="3"
      placeholder="分享你的想法..."
      maxlength="2000"
      show-word-limit
    />
    <div class="composer-actions">
      <el-button type="primary" :loading="posting" :disabled="!content.trim()" @click="submit">
        发布
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const emit = defineEmits(['posted'])
const content = ref('')
const posting = ref(false)

const submit = () => {
  if (!content.value.trim()) return
  posting.value = true
  emit('posted', content.value.trim())
}

const reset = () => {
  content.value = ''
  posting.value = false
}

defineExpose({ reset })
</script>

<style scoped>
.post-composer {
  background: rgba(255,255,255,0.6);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 20px;
  border: 1px solid rgba(255,255,255,0.5);
}
.composer-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 12px;
}
</style>

<template>
  <div v-if="conversation && conversation.length" class="shared-conversation">
    <div class="conv-header">
      <span>AI 对话记录</span>
    </div>
    <div class="conv-messages">
      <div
        v-for="(msg, i) in conversation"
        :key="i"
        class="conv-msg"
        :class="msg.sender"
      >
        <div class="conv-bubble">{{ msg.text }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  conversation: { type: Array, default: () => [] }
})
</script>

<style scoped>
.shared-conversation {
  background: #f7f7f8;
  border-radius: 12px;
  padding: 16px;
  margin: 12px 0;
  max-height: 400px;
  overflow-y: auto;
}
.conv-header {
  font-size: 13px;
  font-weight: 600;
  color: #6e6e73;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e5e7eb;
}
.conv-msg {
  display: flex;
  margin-bottom: 8px;
}
.conv-msg.user { justify-content: flex-end; }
.conv-msg.agent { justify-content: flex-start; }
.conv-bubble {
  max-width: 80%;
  padding: 8px 14px;
  border-radius: 14px;
  font-size: 13px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
}
.conv-msg.user .conv-bubble {
  background: #DCF8C6;
  color: #1d1d1f;
}
.conv-msg.agent .conv-bubble {
  background: #ECECEC;
  color: #1d1d1f;
}
</style>

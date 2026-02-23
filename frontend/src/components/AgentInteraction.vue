<template>
  <div class="module-card">
    <h2 class="module-title">
      <el-icon><MagicStick /></el-icon>
      <span>智能助理 SHU Prophet</span>
    </h2>

    <!-- 对话窗口 (无变化) -->
    <div class="chat-window" ref="chatWindowRef">
      <!-- 消息历史 -->
      <div v-for="(msg, index) in messages" :key="index" class="message-container" :class="msg.sender">
        <div v-if="msg.sender === 'agent'" class="avatar-wrapper" @click="onAvatarClick(index, $event)" @mouseenter="msg.isHovering = true" @mouseleave="msg.isHovering = false">
          <div class="avatar avatar-3d" :class="{ 'is-thinking': isAgentTyping, 'is-blinking': isBlinking, 'is-combo': msg.showCombo, 'is-hovering': msg.isHovering }" :style="msg.showCombo ? {} : avatarTiltStyle">
            <svg viewBox="0 0 48 48" width="28" height="28">
              <circle cx="10" cy="16" r="8" fill="none" stroke="#1d1d1f" stroke-width="2"/>
              <circle cx="38" cy="16" r="8" fill="none" stroke="#1d1d1f" stroke-width="2"/>
              <circle cx="24" cy="26" r="11" fill="none" stroke="#1d1d1f" stroke-width="2"/>
              <circle cx="20" cy="24" :r="isBlinking ? 0.5 : 2" fill="#1d1d1f"/>
              <circle cx="28" cy="24" :r="isBlinking ? 0.5 : 2" fill="#1d1d1f"/>
              <path d="M 21 29 Q 24 31 27 29" fill="none" stroke="#1d1d1f" stroke-width="1.5" stroke-linecap="round"/>
              <path d="M 14 28 L 9 27" stroke="#1d1d1f" stroke-width="1" stroke-linecap="round"/>
              <path d="M 14 30 L 9 31" stroke="#1d1d1f" stroke-width="1" stroke-linecap="round"/>
              <path d="M 34 28 L 39 27" stroke="#1d1d1f" stroke-width="1" stroke-linecap="round"/>
              <path d="M 34 30 L 39 31" stroke="#1d1d1f" stroke-width="1" stroke-linecap="round"/>
            </svg>
          </div>
          <div v-if="msg.showBubble" class="click-bubble">{{ msg.bubbleText }}</div>
        </div>
        <div class="message-bubble">
          <div v-html="renderMarkdown(msg.text)" class="markdown-content"></div>
          <div v-if="msg.chartData" class="chart-container">
            <v-chart class="chart" :option="getChartOption(msg.chartData)" style="height: 350px;" autoresize/>
          </div>
        </div>
        <div v-if="msg.sender === 'user'" class="avatar">
          <svg viewBox="0 0 48 48" width="28" height="28">
            <circle cx="24" cy="20" r="8" fill="none" stroke="#1d1d1f" stroke-width="2"/>
            <path d="M 12 38 Q 12 28 24 28 Q 36 28 36 38" fill="none" stroke="#1d1d1f" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </div>
      </div>
      <!-- 加载动画 (无变化) -->
      <div v-if="isAgentTyping" class="message-container agent">
         <div class="message-bubble typing-indicator"><span></span><span></span><span></span></div>
      </div>
    </div>

    <!-- 核心升级：全新的输入区域，集成了文本输入、上传和发送按钮 -->
    <div class="input-area">
      <el-input
        v-model="userInput"
        placeholder="在这里输入消息..."
        @keyup.enter="sendMessage"
        :disabled="isAgentTyping"
        clearable
      >
        <!-- 将上传按钮集成到输入框的后面 -->
        <template #append>
          <el-upload
            ref="uploadRef"
            action="/api/agent-upload-predict"
            name="file"
            :show-file-list="false"
            :on-success="handleUploadSuccess"
            :on-error="handleUploadError"
            :before-upload="beforeUpload"
          >
            <el-button :icon="UploadFilled" :disabled="isAgentTyping"></el-button>
          </el-upload>
        </template>
      </el-input>
      <el-button type="primary" @click="sendMessage" :disabled="isAgentTyping" style="margin-left: 10px;">发送</el-button>
    </div>

    <!-- COMBO效果 - 传送到body确保在最上层 -->
    <Teleport to="body">
      <div v-if="showGlobalCombo" class="combo-effect-big" :style="{ left: comboPos.x + 'px', top: comboPos.y + 'px' }">
        <div class="combo-mouse">🐭</div>
        <div class="combo-text-big">🎉 COMBO! 🎉</div>
        <div class="combo-fireworks">
          <span v-for="i in 12" :key="i" class="firework">✨</span>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, computed } from 'vue';
import { ElMessage } from 'element-plus';
import { marked } from 'marked';
import { UploadFilled } from '@element-plus/icons-vue'
import axios from 'axios';

// Markdown渲染函数
const renderMarkdown = (text) => {
  if (!text) return '';
  try {
    return marked.parse(text);
  } catch (e) {
    return text;
  }
};

// --- 状态定义 ---
const userInput = ref('');
const isAgentTyping = ref(false);
const chatWindowRef = ref(null);
const messages = ref([]);
const sessionId = ref(`session_${Date.now()}_${Math.random()}`);
const isBlinking = ref(false);
const clickCounts = ref({});
const mousePos = ref({ x: 0, y: 0 });
const showGlobalCombo = ref(false);
const comboPos = ref({ x: 0, y: 0 });

// --- 生命周期钩子 ---
onMounted(() => {
  sendMessage('你好', true);
  startBlinking();
  window.addEventListener('mousemove', handleMouseMove);
});

// 鼠标追踪
const handleMouseMove = (e) => {
  mousePos.value = { x: e.clientX, y: e.clientY };
};

// 计算头像倾斜样式
const avatarTiltStyle = computed(() => {
  const centerX = window.innerWidth / 2;
  const centerY = window.innerHeight / 2;
  const deltaX = (mousePos.value.x - centerX) / centerX;
  const deltaY = (mousePos.value.y - centerY) / centerY;
  const rotateY = deltaX * 25;
  const rotateX = -deltaY * 25;
  return {
    transform: `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale(1)`
  };
});

// 眨眼效果
const startBlinking = () => {
  setInterval(() => {
    isBlinking.value = true;
    setTimeout(() => isBlinking.value = false, 150);
  }, 4000);
};

// 点击头像
const onAvatarClick = (index, event) => {
  if (!clickCounts.value[index]) clickCounts.value[index] = 0;
  clickCounts.value[index]++;

  const msg = messages.value[index];
  const phrases = ['在下鼠先知，有何指教？', '今天的预测准吗？', '让我算算...', '数据在跳舞呢~', '(/ω＼)'];

  if (clickCounts.value[index] >= 5) {
    const rect = event.currentTarget.getBoundingClientRect();
    comboPos.value = { x: rect.left + rect.width / 2, y: rect.top + rect.height / 2 };
    msg.showBubble = false;
    msg.showCombo = true;
    showGlobalCombo.value = true;
    clickCounts.value[index] = 0;
    setTimeout(() => {
      msg.showCombo = false;
      showGlobalCombo.value = false;
    }, 2000);
  } else {
    msg.showCombo = false;
    msg.bubbleText = phrases[Math.floor(Math.random() * phrases.length)];
    msg.showBubble = true;
    setTimeout(() => msg.showBubble = false, 2000);
  }
};

// --- 方法 ---

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    const chatWindow = chatWindowRef.value;
    if (chatWindow) chatWindow.scrollTop = chatWindow.scrollHeight;
  });
};

// 发送纯文本消息
const sendMessage = async (initialMessage = '', isGreeting = false) => {
  const textToSend = isGreeting ? initialMessage : userInput.value.trim();
  if (!textToSend) return;

  if (!isGreeting) {
    messages.value.push({ sender: 'user', text: textToSend });
  }

  userInput.value = '';
  isAgentTyping.value = true;
  scrollToBottom();

  try {
    const response = await axios.post('/api/agent-message', {
      message: textToSend,
      session_id: sessionId.value
    });
    messages.value.push({ sender: 'agent', text: response.data.reply });
  } catch (error) {
    messages.value.push({ sender: 'agent', text: '抱歉，我好像遇到了一点网络问题。' });
  } finally {
    isAgentTyping.value = false;
    scrollToBottom();
  }
};

// 文件上传前的钩子
const beforeUpload = (file) => {
  const isCSV = file.type === 'text/csv' || file.name.endsWith('.csv');
  if (!isCSV) {
    ElMessage.error('只能上传 CSV 格式的文件!');
    return false;
  }
  messages.value.push({ sender: 'user', text: `(已上传文件: ${file.name})` });
  isAgentTyping.value = true;
  scrollToBottom();
  return true;
};

// 文件上传成功的回调
const handleUploadSuccess = (response) => {
  isAgentTyping.value = false;
  if (response.error) {
    messages.value.push({ sender: 'agent', text: `分析失败: ${response.error}` });
  } else {
    messages.value.push({
      sender: 'agent',
      text: response.report,
      isReport: true,
      chartData: response.chart_data
    });
  }
  scrollToBottom();
};

// 文件上传失败的回调
const handleUploadError = (error) => {
  isAgentTyping.value = false;
  const errorMsg = JSON.parse(error.message)?.error || '上传或分析失败，请检查文件或后端服务。';
  messages.value.push({ sender: 'agent', text: `出现错误: ${errorMsg}` });
  scrollToBottom();
};

// ECharts图表配置 (无变化)
const getChartOption = (chartData) => ({
  tooltip: { trigger: 'axis' },
  legend: { data: ['历史数据', 'ARIMA预测值'], top: 'bottom', textStyle: { color: '#e2e8f0' } },
  grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
  xAxis: { type: 'value', name: 'X', splitLine: { show: false } },
  yAxis: { type: 'value', name: 'Y', splitLine: { lineStyle: { color: '#334155' } } },
  series: [
    { name: '历史数据', type: 'line', smooth: true, showSymbol: false, data: chartData.history_data, itemStyle: { color: '#38bdf8' } },
    { name: 'ARIMA预测值', type: 'line', smooth: true, showSymbol: false, data: chartData.forecast_data, lineStyle: { type: 'dashed' }, itemStyle: { color: '#67c23a' } }
  ]
});
</script>

<style scoped>
.chat-window {
  height: 65vh;
  background-color: #F7F7F8;
  border: none;
  border-radius: 12px;
  padding: 1.5rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}
.message-container {
  display: flex;
  margin-bottom: 1rem;
  flex-shrink: 0;
  gap: 10px;
  align-items: flex-start;
}
.message-container.user {
  justify-content: flex-end;
}
.message-container.agent {
  justify-content: flex-start;
}
.avatar-wrapper {
  position: relative;
  cursor: pointer;
  user-select: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  margin-left: 20px;
  perspective: 1000px;
}
.avatar-3d {
  transform-style: preserve-3d;
  transition: transform 0.1s ease-out;
}
.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
  background-color: #ffffff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  cursor: pointer;
}
.avatar-3d {
  transform-style: preserve-3d;
  transition: transform 0.05s ease-out !important;
}
.avatar:hover {
  transform: scale(1.15);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}
.avatar.is-thinking {
  animation: bounce 0.6s ease-in-out infinite;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.3);
}
.avatar.is-hovering {
  transform: scale(1.2) !important;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.25) !important;
}
.avatar.is-combo {
  animation: comboJump 0.5s ease-out, comboShrink 0.3s 1.7s ease-in !important;
  transform: none !important;
}
@keyframes comboJump {
  0% { transform: scale(1); }
  50% { transform: scale(0.3); opacity: 0.3; }
  100% { transform: scale(0); opacity: 0; }
}
@keyframes comboShrink {
  0% { transform: scale(0); opacity: 0; }
  100% { transform: scale(1); opacity: 1; }
}
.combo-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.3);
  z-index: 9999;
  pointer-events: none;
  animation: overlayFade 0.3s ease-out;
}
@keyframes overlayFade {
  0% { opacity: 0; }
  100% { opacity: 1; }
}
.combo-effect-big {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 9999;
  pointer-events: none;
}
.combo-mouse {
  position: absolute;
  font-size: 80px;
  animation: mouseRun 2s ease-in-out;
}
@keyframes mouseRun {
  0% { left: 0; top: 0; transform: rotate(0deg); }
  25% { left: 200px; top: -100px; transform: rotate(360deg); }
  50% { left: 0; top: -200px; transform: rotate(720deg); }
  75% { left: -200px; top: -100px; transform: rotate(1080deg); }
  100% { left: 0; top: 0; transform: rotate(1440deg) scale(0.2); opacity: 0; }
}
.combo-text-big {
  position: absolute;
  top: -150px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 48px;
  font-weight: bold;
  color: #ff6b6b;
  text-shadow: 3px 3px 6px rgba(0,0,0,0.3);
  animation: comboBounce 0.6s ease-out;
}
@keyframes comboBounce {
  0%, 100% { transform: translateX(-50%) scale(1); }
  50% { transform: translateX(-50%) scale(1.3); }
}
.combo-fireworks {
  position: absolute;
  top: 0;
  left: 0;
}
.firework {
  position: absolute;
  font-size: 30px;
  animation: fireworkExplode 1.5s ease-out forwards;
}
.firework:nth-child(1) { animation-delay: 0s; --fx: 150px; --fy: -150px; }
.firework:nth-child(2) { animation-delay: 0.1s; --fx: 200px; --fy: 0; }
.firework:nth-child(3) { animation-delay: 0.2s; --fx: 150px; --fy: 150px; }
.firework:nth-child(4) { animation-delay: 0.3s; --fx: 0; --fy: 200px; }
.firework:nth-child(5) { animation-delay: 0.4s; --fx: -150px; --fy: 150px; }
.firework:nth-child(6) { animation-delay: 0.5s; --fx: -200px; --fy: 0; }
.firework:nth-child(7) { animation-delay: 0.6s; --fx: -150px; --fy: -150px; }
.firework:nth-child(8) { animation-delay: 0.7s; --fx: 0; --fy: -200px; }
.firework:nth-child(9) { animation-delay: 0.8s; --fx: 100px; --fy: -100px; }
.firework:nth-child(10) { animation-delay: 0.9s; --fx: 100px; --fy: 100px; }
.firework:nth-child(11) { animation-delay: 1s; --fx: -100px; --fy: 100px; }
.firework:nth-child(12) { animation-delay: 1.1s; --fx: -100px; --fy: -100px; }
@keyframes fireworkExplode {
  0% { transform: translate(0, 0) scale(0); opacity: 1; }
  100% { transform: translate(var(--fx), var(--fy)) scale(2); opacity: 0; }
}
.click-bubble {
  position: absolute;
  top: -40px;
  left: 50%;
  transform: translateX(-50%);
  background: #ffffff;
  color: #1d1d1f;
  padding: 8px 16px;
  border-radius: 16px;
  font-size: 14px;
  white-space: nowrap;
  z-index: 10;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  animation: popIn 0.3s ease-out;
}
@keyframes popIn {
  0% { transform: translateX(-50%) scale(0); opacity: 0; }
  50% { transform: translateX(-50%) scale(1.1); }
  100% { transform: translateX(-50%) scale(1); opacity: 1; }
}
@keyframes breathe {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.03); }
}
@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-4px); }
}
.message-bubble {
  max-width: 75%;
  padding: 12px 16px;
  border-radius: 18px;
  line-height: 1.6;
  word-wrap: break-word;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.08);
  position: relative;
}
.message-container.user .message-bubble {
  background-color: #DCF8C6;
  color: #1d1d1f;
  border-bottom-right-radius: 4px;
}
.message-container.agent .message-bubble {
  background-color: #ECECEC;
  color: #1d1d1f;
  border-bottom-left-radius: 4px;
}
.chart-container {
  margin-top: 1rem;
  background-color: #ffffff;
  border-radius: 12px;
  padding: 1rem;
  border: 1px solid #e5e5e5;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}
.message-bubble :deep(h3) {
  font-size: 1.1rem;
  color: #1d1d1f;
  margin-top: 1rem;
  margin-bottom: 0.5rem;
  font-weight: 600;
}
.message-bubble :deep(p) {
  margin: 0 0 0.5rem 0;
}
.message-bubble :deep(strong) {
  font-weight: 600;
}
.message-bubble :deep(code) {
  background-color: rgba(0, 0, 0, 0.05);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 0.9em;
}
.markdown-content :deep(h1),
.markdown-content :deep(h2),
.markdown-content :deep(h3) {
  font-weight: 600;
  margin-top: 1em;
  margin-bottom: 0.5em;
  color: #1d1d1f;
}
.markdown-content :deep(h1) { font-size: 1.5em; }
.markdown-content :deep(h2) { font-size: 1.3em; }
.markdown-content :deep(h3) { font-size: 1.1em; }
.markdown-content :deep(p) {
  margin: 0.5em 0;
  line-height: 1.6;
}
.markdown-content :deep(ul),
.markdown-content :deep(ol) {
  margin: 0.5em 0;
  padding-left: 1.5em;
}
.markdown-content :deep(li) {
  margin: 0.3em 0;
  line-height: 1.6;
}
.markdown-content :deep(pre) {
  background-color: #f6f8fa;
  border-radius: 6px;
  padding: 12px;
  overflow-x: auto;
  margin: 0.5em 0;
}
.markdown-content :deep(pre code) {
  background-color: transparent;
  padding: 0;
}
.markdown-content :deep(strong) {
  font-weight: 600;
  color: #1d1d1f;
}
.markdown-content :deep(em) {
  font-style: italic;
}
.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 8px 0;
}
.typing-indicator span {
  height: 8px;
  width: 8px;
  background-color: #999;
  border-radius: 50%;
  animation: 1s blink infinite;
}
.typing-indicator span:nth-child(2) { animation-delay: .2s; }
.typing-indicator span:nth-child(3) { animation-delay: .4s; }
@keyframes blink { 50% { opacity: 0.3; } }

.input-area {
  margin-top: 1.5rem;
  display: flex;
  align-items: center;
  gap: 12px;
}
.input-area :deep(.el-upload) {
  --el-input-group-append-padding: 0;
  --el-input-group-append-border-color: transparent;
}
.input-area :deep(.el-input__wrapper) {
  background-color: #ffffff;
  border-radius: 24px;
  padding: 12px 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}
.input-area :deep(.el-button) {
  border-radius: 20px;
  padding: 12px 24px;
  font-weight: 500;
}
</style>
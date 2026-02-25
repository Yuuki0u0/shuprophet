<template>
  <div class="profile-page">
    <div class="module-card profile-card">
      <h2 class="module-title">
        <el-icon><UserFilled /></el-icon>
        <span>个人中心</span>
      </h2>
      <div class="profile-header">
        <div class="avatar-section">
          <img :src="user?.avatar_url || '/api/user/avatars/default.png'" class="profile-avatar" @click="triggerUpload" />
          <el-button size="small" @click="triggerUpload">更换头像</el-button>
          <input ref="fileRef" type="file" accept="image/*" style="display:none" @change="uploadAvatar" />
        </div>
        <div class="info-section">
          <el-form :model="form" label-width="70px">
            <el-form-item label="用户名">
              <el-input :value="user?.username" disabled />
            </el-form-item>
            <el-form-item label="昵称">
              <el-input v-model="form.nickname" maxlength="80" />
            </el-form-item>
            <el-form-item label="简介">
              <el-input v-model="form.bio" type="textarea" :rows="3" maxlength="500" show-word-limit />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="saving" @click="saveProfile">保存</el-button>
            </el-form-item>
          </el-form>
        </div>
      </div>
    </div>

    <!-- 积分管理卡片 -->
    <div class="module-card credits-card">
      <h2 class="module-title">
        <el-icon><Coin /></el-icon>
        <span>积分管理</span>
      </h2>

      <div class="credits-overview">
        <div class="credits-stat">
          <span class="stat-label">当前积分</span>
          <span class="stat-value">{{ creditsInfo?.credits ?? 0 }}</span>
        </div>
        <div class="credits-stat">
          <span class="stat-label">今日已用</span>
          <span class="stat-value">{{ creditsInfo?.today_used ?? 0 }} / {{ creditsInfo?.free_limit ?? 10 }}</span>
        </div>
        <div class="credits-stat">
          <span class="stat-label">免费剩余</span>
          <span class="stat-value highlight">{{ creditsInfo?.free_remaining ?? 0 }}</span>
        </div>
      </div>

      <!-- 兑换码 -->
      <div class="redeem-section">
        <h3 class="section-title">兑换码充值</h3>
        <div class="redeem-row">
          <el-input v-model="redeemCode" placeholder="请输入兑换码" maxlength="64" clearable />
          <el-button type="primary" :loading="redeeming" @click="doRedeem">兑换</el-button>
        </div>
      </div>

      <!-- 积分流水 -->
      <div class="logs-section">
        <h3 class="section-title">积分记录</h3>
        <div v-if="creditLogs.length" class="log-list">
          <div v-for="log in creditLogs" :key="log.id" class="log-item">
            <span class="log-desc">{{ log.description }}</span>
            <span class="log-amount" :class="log.amount > 0 ? 'positive' : 'negative'">
              {{ log.amount > 0 ? '+' : '' }}{{ log.amount }}
            </span>
            <span class="log-time">{{ formatTime(log.created_at) }}</span>
          </div>
        </div>
        <div v-else class="empty-logs">暂无积分记录</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Coin } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import request from '@/utils/request'

const auth = useAuthStore()
const user = computed(() => auth.user)
const saving = ref(false)
const fileRef = ref(null)
const form = ref({ nickname: '', bio: '' })

// 积分相关
const creditsInfo = ref(null)
const redeemCode = ref('')
const redeeming = ref(false)
const creditLogs = ref([])

onMounted(() => {
  if (user.value) {
    form.value.nickname = user.value.nickname || ''
    form.value.bio = user.value.bio || ''
  }
  fetchCredits()
  fetchLogs()
})

const triggerUpload = () => fileRef.value?.click()

const uploadAvatar = async (e) => {
  const file = e.target.files?.[0]
  if (!file) return
  const fd = new FormData()
  fd.append('file', file)
  try {
    const res = await request.post('/user/avatar', fd)
    auth.user.avatar_url = res.data.avatar_url
    localStorage.setItem('user', JSON.stringify(auth.user))
    ElMessage.success('头像已更新')
  } catch {
    ElMessage.error('上传失败')
  }
  e.target.value = ''
}

const saveProfile = async () => {
  saving.value = true
  try {
    const res = await request.put('/user/profile', form.value)
    auth.user.nickname = res.data.user.nickname
    auth.user.bio = res.data.user.bio
    localStorage.setItem('user', JSON.stringify(auth.user))
    ElMessage.success('保存成功')
  } catch {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

// 积分函数
const fetchCredits = async () => {
  try {
    const res = await request.get('/credits/info')
    creditsInfo.value = res.data
  } catch { /* ignore */ }
}

const fetchLogs = async () => {
  try {
    const res = await request.get('/credits/logs')
    creditLogs.value = res.data.logs
  } catch { /* ignore */ }
}

const doRedeem = async () => {
  if (!redeemCode.value.trim()) {
    ElMessage.warning('请输入兑换码')
    return
  }
  redeeming.value = true
  try {
    const res = await request.post('/credits/redeem', { code: redeemCode.value.trim() })
    ElMessage.success(res.data.message)
    redeemCode.value = ''
    fetchCredits()
    fetchLogs()
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '兑换失败')
  } finally {
    redeeming.value = false
  }
}

const formatTime = (iso) => {
  if (!iso) return ''
  const d = new Date(iso)
  return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours()}:${String(d.getMinutes()).padStart(2, '0')}`
}
</script>

<style scoped>
.profile-header {
  display: flex;
  gap: 40px;
  align-items: flex-start;
}
.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}
.profile-avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  cursor: pointer;
  border: 3px solid #e5e7eb;
  transition: border-color 0.2s;
}
.profile-avatar:hover {
  border-color: #409eff;
}
.info-section {
  flex: 1;
  min-width: 0;
}
@media (max-width: 768px) {
  .profile-header {
    flex-direction: column;
    align-items: center;
  }
}

/* 积分管理 */
.credits-card {
  margin-top: 24px;
}
.credits-overview {
  display: flex;
  gap: 24px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}
.credits-stat {
  background: #f5f7fa;
  border-radius: 12px;
  padding: 16px 24px;
  text-align: center;
  flex: 1;
  min-width: 120px;
}
.stat-label {
  display: block;
  font-size: 13px;
  color: #6e6e73;
  margin-bottom: 6px;
}
.stat-value {
  display: block;
  font-size: 1.5rem;
  font-weight: 600;
  color: #1d1d1f;
}
.stat-value.highlight {
  color: #0071e3;
}
.section-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #1d1d1f;
  margin-bottom: 12px;
}
.redeem-section {
  margin-bottom: 24px;
}
.redeem-row {
  display: flex;
  gap: 12px;
  max-width: 400px;
}
.log-list {
  max-height: 300px;
  overflow-y: auto;
}
.log-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
  font-size: 14px;
}
.log-desc {
  flex: 1;
  color: #1d1d1f;
}
.log-amount {
  font-weight: 600;
  min-width: 60px;
  text-align: right;
}
.log-amount.positive {
  color: #34c759;
}
.log-amount.negative {
  color: #ff3b30;
}
.log-time {
  color: #9ca3af;
  font-size: 12px;
  min-width: 80px;
  text-align: right;
}
.empty-logs {
  color: #9ca3af;
  text-align: center;
  padding: 20px 0;
}
</style>

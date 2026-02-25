<template>
  <div class="admin-page">
    <!-- 未登录：密码输入 -->
    <div v-if="!adminToken" class="module-card admin-login">
      <h2 class="module-title">管理员验证</h2>
      <div class="login-form">
        <el-input v-model="password" type="password" placeholder="请输入管理员密码" @keyup.enter="doLogin" show-password />
        <el-button type="primary" :loading="logging" @click="doLogin" style="margin-top:12px;width:100%">验证</el-button>
      </div>
    </div>

    <!-- 已登录：管理面板 -->
    <template v-else>
      <div class="module-card">
        <h2 class="module-title">兑换码管理</h2>

        <!-- 生成区 -->
        <div class="gen-section">
          <el-input-number v-model="genCount" :min="1" :max="100" label="数量" />
          <el-input-number v-model="genCredits" :min="1" :max="10000" label="积分" />
          <el-button type="primary" :loading="generating" @click="doGenerate">批量生成</el-button>
        </div>

        <!-- 刚生成的码 -->
        <div v-if="newCodes.length" class="new-codes">
          <p>新生成的兑换码（点击复制全部）：</p>
          <pre class="code-block" @click="copyAll">{{ newCodes.join('\n') }}</pre>
        </div>

        <!-- 码列表 -->
        <el-table :data="codes" stripe style="width:100%;margin-top:16px" max-height="500">
          <el-table-column prop="code" label="兑换码" min-width="180" />
          <el-table-column prop="credits" label="积分" width="80" />
          <el-table-column label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="row.is_used ? 'info' : 'success'" size="small">
                {{ row.is_used ? '已用' : '可用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="80">
            <template #default="{ row }">
              <el-button size="small" type="danger" text @click="doDelete(row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const password = ref('')
const logging = ref(false)
const adminToken = ref(sessionStorage.getItem('admin_token') || '')

const codes = ref([])
const newCodes = ref([])
const genCount = ref(10)
const genCredits = ref(100)
const generating = ref(false)

const api = axios.create({ baseURL: '/api/admin' })
api.interceptors.request.use(cfg => {
  if (adminToken.value) cfg.headers['X-Admin-Token'] = adminToken.value
  return cfg
})

onMounted(() => { if (adminToken.value) fetchCodes() })

const doLogin = async () => {
  if (!password.value) return
  logging.value = true
  try {
    const res = await api.post('/login', { password: password.value })
    adminToken.value = res.data.token
    sessionStorage.setItem('admin_token', res.data.token)
    password.value = ''
    fetchCodes()
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '验证失败')
  } finally {
    logging.value = false
  }
}

const fetchCodes = async () => {
  try {
    const res = await api.get('/codes')
    codes.value = res.data.codes
  } catch {
    ElMessage.error('加载失败')
  }
}

const doGenerate = async () => {
  generating.value = true
  try {
    const res = await api.post('/codes/generate', {
      count: genCount.value,
      credits: genCredits.value
    })
    newCodes.value = res.data.codes
    ElMessage.success(res.data.message)
    fetchCodes()
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '生成失败')
  } finally {
    generating.value = false
  }
}

const doDelete = async (id) => {
  try {
    await api.delete(`/codes/${id}`)
    ElMessage.success('已删除')
    fetchCodes()
  } catch {
    ElMessage.error('删除失败')
  }
}

const copyAll = async () => {
  try {
    await navigator.clipboard.writeText(newCodes.value.join('\n'))
    ElMessage.success('已复制到剪贴板')
  } catch {
    ElMessage.error('复制失败')
  }
}
</script>

<style scoped>
.admin-page {
  max-width: 800px;
  margin: 0 auto;
}
.admin-login {
  max-width: 400px;
  margin: 10vh auto;
  text-align: center;
}
.login-form {
  max-width: 300px;
  margin: 0 auto;
}
.gen-section {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}
.new-codes {
  margin-top: 16px;
}
.new-codes p {
  font-size: 13px;
  color: #6e6e73;
  margin-bottom: 8px;
}
.code-block {
  background: #f5f7fa;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 13px;
  cursor: pointer;
  user-select: all;
  line-height: 1.8;
}
.code-block:hover {
  background: #eef1f6;
}
</style>
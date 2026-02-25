<template>
  <div>
    <h1 class="page-title">{{ $route.meta.title }}</h1>
    <!-- 未登录：显示提示 -->
    <div v-if="!isLoggedIn" class="module-card login-gate">
      <div class="gate-icon">🔒</div>
      <h3>请先登录</h3>
      <p>智能助理功能需要登录后才能使用</p>
      <div class="gate-actions">
        <el-button type="primary" @click="$router.push('/login')">去登录</el-button>
        <el-button @click="$router.push('/register')">注册账号</el-button>
      </div>
    </div>
    <!-- 已登录：显示助理 -->
    <AgentInteraction v-else />
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useAuthStore } from '@/stores/auth';
import AgentInteraction from '@/components/AgentInteraction.vue';

defineOptions({ name: 'AgentView' });

const auth = useAuthStore();
const isLoggedIn = computed(() => auth.isLoggedIn);
</script>

<style scoped>
.login-gate {
  text-align: center;
  padding: 60px 40px;
}
.gate-icon {
  font-size: 48px;
  margin-bottom: 16px;
}
.login-gate h3 {
  font-size: 1.5rem;
  color: #1d1d1f;
  margin-bottom: 8px;
}
.login-gate p {
  color: #6e6e73;
  margin-bottom: 24px;
}
.gate-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
}
</style>

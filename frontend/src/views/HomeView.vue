<template>
  <div class="home-view">

    <!-- Hero Section -->
    <section class="hero-section">
      <img src="@/assets/logo.png" alt="Project Logo" class="home-logo">
      <p class="hero-tagline">新一代时序智能预测与决策平台</p>
      <p class="hero-sub">Powered by LLM Agent &middot; Multi-Model Ensemble &middot; Deep Reasoning</p>
    </section>

    <!-- Stats Bar -->
    <section class="stats-bar">
      <div class="stat-item" v-for="s in stats" :key="s.label">
        <span class="stat-number">{{ s.value }}</span>
        <span class="stat-label">{{ s.label }}</span>
      </div>
    </section>

    <!-- Feature Cards -->
    <section class="features-section">
      <div class="feature-card" v-for="f in features" :key="f.title">
        <div class="feature-icon">{{ f.icon }}</div>
        <div class="feature-body">
          <h3 class="feature-title">{{ f.title }}</h3>
          <p class="feature-desc">{{ f.desc }}</p>
        </div>
        <div class="feature-tag">{{ f.tag }}</div>
      </div>
    </section>

    <!-- Research Achievements — compact ribbon -->
    <section class="research-ribbon">
      <h2 class="ribbon-title">学术成果</h2>
      <div class="ribbon-track">
        <div class="ribbon-item" v-for="p in papers" :key="p.model"
             :class="p.rank.toLowerCase().replace('-','')">
          <span class="ribbon-rank">{{ p.rank }}</span>
          <span class="ribbon-model">{{ p.model }}</span>
          <span class="ribbon-conf">{{ p.conf }}</span>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="cta-section">
      <el-button type="primary" size="large" @click="$router.push('/app')" round class="cta-btn">
        进入数据探索 <el-icon class="el-icon--right"><ArrowRight /></el-icon>
      </el-button>
      <p class="cta-hint">Wei Li &middot; Zixin Wang</p>
    </section>

  </div>
</template>

<script setup>
import { ArrowRight } from '@element-plus/icons-vue'

const stats = [
  { value: '6', label: 'CCF 论文' },
  { value: '6+', label: '自研模型' },
  { value: '3', label: '核心引擎' },
  { value: '12+', label: '分析工具' },
]

const features = [
  {
    icon: '🔬',
    title: '科研数据探索',
    desc: '多模型对比可视化，自动计算 MAE/MSE 指标，一键加载标准数据集',
    tag: 'Explorer',
  },
  {
    icon: '⚡',
    title: '实时智能预测',
    desc: '上传 CSV 即刻获得 ARIMA + 多模型集成预测，置信区间与趋势分析',
    tag: 'Predictor',
  },
  {
    icon: '🧠',
    title: 'AI 智能助理',
    desc: '基于 LLM Agent 的对话式分析，支持深度推理思考模式与完整推理轨迹展示',
    tag: 'Agent',
  },
  {
    icon: '📊',
    title: '统计接地分析',
    desc: '频域分析、变点检测、平稳性检验、异常检测等 12+ 专业统计工具',
    tag: 'Tools',
  },
]

const papers = [
  { rank: 'CCF-B', conf: 'ICASSP 2026', model: 'ScatterFusion' },
  { rank: 'CCF-B', conf: 'ICASSP 2026', model: 'AWGFormer' },
  { rank: 'CCF-C', conf: 'ICANN 2025', model: 'SWIFT' },
  { rank: 'CCF-C', conf: 'ICIC 2025', model: 'LWSpace' },
  { rank: 'CCF-C', conf: 'ICIC 2025', model: 'EnergyPatchTST' },
  { rank: 'CCF-C', conf: 'ICANN 2025', model: 'TimeFlowDiffuser' },
]
</script>

<style scoped>
.home-view {
  max-width: 960px;
  margin: 0 auto;
  padding: 6vh 20px 8vh;
}

/* ---- Hero ---- */
.hero-section {
  text-align: center;
  margin-bottom: 3rem;
}
.home-logo {
  max-width: 420px;
  width: 75%;
  height: auto;
  margin-bottom: 0.5rem;
}
.hero-tagline {
  font-size: 1.15rem;
  font-weight: 500;
  color: #475569;
  margin: 0 0 0.5rem;
  letter-spacing: 0.08em;
}
.hero-sub {
  font-size: 0.85rem;
  color: #94a3b8;
  margin: 0;
  letter-spacing: 0.04em;
}

/* ---- Stats Bar ---- */
.stats-bar {
  display: flex;
  justify-content: center;
  gap: 2px;
  margin-bottom: 3rem;
  background: linear-gradient(135deg, rgba(56,189,248,0.08), rgba(167,139,250,0.08));
  border-radius: 16px;
  padding: 1.5rem 0;
  border: 1px solid rgba(255,255,255,0.5);
  box-shadow: 0 4px 24px rgba(0,0,0,0.04);
}
.stat-item {
  flex: 1;
  text-align: center;
  position: relative;
}
.stat-item:not(:last-child)::after {
  content: '';
  position: absolute;
  right: 0;
  top: 15%;
  height: 70%;
  width: 1px;
  background: rgba(0,0,0,0.06);
}
.stat-number {
  display: block;
  font-size: 2rem;
  font-weight: 700;
  background: linear-gradient(135deg, #38bdf8, #a78bfa);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  line-height: 1.2;
}
.stat-label {
  display: block;
  font-size: 0.8rem;
  color: #94a3b8;
  margin-top: 4px;
  letter-spacing: 0.04em;
}

/* ---- Feature Cards ---- */
.features-section {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.25rem;
  margin-bottom: 3rem;
}
.feature-card {
  position: relative;
  background: rgba(255,255,255,0.65);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255,255,255,0.5);
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 4px 20px rgba(0,0,0,0.05);
  transition: box-shadow 0.3s ease, border-color 0.3s ease;
  overflow: hidden;
}
.feature-card:hover {
  border-color: rgba(56,189,248,0.3);
  box-shadow: 0 8px 32px rgba(56,189,248,0.1);
}
.feature-icon {
  font-size: 1.75rem;
  margin-bottom: 0.75rem;
}
.feature-title {
  font-size: 1.05rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 0.4rem;
}
.feature-desc {
  font-size: 0.82rem;
  color: #64748b;
  line-height: 1.6;
  margin: 0;
}
.feature-tag {
  position: absolute;
  top: 1rem;
  right: 1rem;
  font-size: 0.65rem;
  font-weight: 600;
  color: #38bdf8;
  background: rgba(56,189,248,0.08);
  padding: 2px 8px;
  border-radius: 6px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

/* ---- Research Ribbon ---- */
.research-ribbon {
  margin-bottom: 3rem;
}
.ribbon-title {
  font-size: 0.85rem;
  font-weight: 600;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  margin: 0 0 1rem;
  text-align: center;
}
.ribbon-track {
  display: flex;
  gap: 0.75rem;
  overflow-x: auto;
  padding-bottom: 4px;
  scrollbar-width: thin;
}
.ribbon-item {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 1rem;
  border-radius: 10px;
  background: rgba(255,255,255,0.5);
  border: 1px solid rgba(0,0,0,0.04);
  transition: box-shadow 0.25s ease;
}
.ribbon-item:hover {
  box-shadow: 0 4px 16px rgba(0,0,0,0.08);
}
.ribbon-item.ccfb .ribbon-rank {
  color: #d97706;
}
.ribbon-item.ccfc .ribbon-rank {
  color: #a78bfa;
}
.ribbon-rank {
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.04em;
}
.ribbon-model {
  font-size: 0.82rem;
  font-weight: 600;
  color: #1e293b;
}
.ribbon-conf {
  font-size: 0.7rem;
  color: #94a3b8;
}

/* ---- CTA ---- */
.cta-section {
  text-align: center;
}
.cta-btn {
  padding: 12px 36px;
  font-size: 1rem;
  font-weight: 500;
}
.cta-hint {
  margin-top: 1rem;
  font-size: 0.8rem;
  color: #cbd5e1;
  letter-spacing: 0.04em;
}

/* ---- Responsive ---- */
@media (max-width: 640px) {
  .features-section {
    grid-template-columns: 1fr;
  }
  .stats-bar {
    flex-wrap: wrap;
    gap: 1rem;
    padding: 1rem;
  }
  .stat-item:not(:last-child)::after {
    display: none;
  }
  .ribbon-track {
    flex-wrap: wrap;
    justify-content: center;
  }
}
</style>

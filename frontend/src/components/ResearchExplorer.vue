<template>
  <div class="module-card">
    <h2 class="module-title"><el-icon><Box /></el-icon><span>科研成果探索</span></h2>
    <el-form label-position="top">
      <el-form-item label="选择数据集进行预处理与分析">
        <el-select v-model="selectedDataset" placeholder="请选择数据集" style="width: 100%;" @change="runAnalysis" filterable>
          <el-option v-for="item in datasetOptions" :key="item" :label="item" :value="item"/>
        </el-select>
      </el-form-item>
    </el-form>

    <div v-if="isLoading" class="loading-container">
      <div class="progress-bar">
        <div class="progress-fill" :style="{width: loadingProgress + '%'}"></div>
      </div>
      <div class="loading-text">{{ loadingStage }}</div>
    </div>
    
    <div v-if="!isLoading && chartData">
      <el-row :gutter="12" class="metrics-cards">
        <el-col :span="12" v-for="model in chartData.model_predictions" :key="model.model_name">
          <div class="metric-card">
            <span class="model-name">{{ model.model_name }}</span>
            <div class="metrics">
              <span>MAE: <b>{{ model.metrics.mae }}</b></span>
              <span>MSE: <b>{{ model.metrics.mse }}</b></span>
            </div>
          </div>
        </el-col>
      </el-row>
      <v-chart class="chart" :option="chartOption" style="height: 450px;" autoresize/>
      <v-chart class="chart" :option="performanceOption" style="height: 300px; margin-top: 20px;" autoresize/>
    </div>

    <el-empty v-if="!isLoading && !chartData" description="请选择一个数据集开始分析" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';
import { ElMessage } from 'element-plus';

const selectedDataset = ref('');
const datasetOptions = ref([]);
const isLoading = ref(false);
const chartData = ref(null);
const loadingProgress = ref(0);
const loadingStage = ref('');

onMounted(async () => {
  try {
    const response = await axios.get('/api/datasets');
    datasetOptions.value = response.data;
    if (datasetOptions.value.length > 0) {
      selectedDataset.value = datasetOptions.value[0];
      runAnalysis(); // 自动加载第一个数据集
    }
  } catch (error) {
    ElMessage.error('获取数据集列表失败！');
  }
});

const runAnalysis = async () => {
  if (!selectedDataset.value) return;
  isLoading.value = true;
  chartData.value = null;
  loadingProgress.value = 0;
  loadingStage.value = '数据加载中...';

  try {
    await new Promise(r => setTimeout(r, 400));
    loadingProgress.value = 33;
    loadingStage.value = '模型推理中...';

    const response = await axios.post('/api/parse-csv', {
      dataset: selectedDataset.value,
    });

    loadingProgress.value = 66;
    loadingStage.value = '结果生成中...';
    await new Promise(r => setTimeout(r, 300));

    if (response.data.error) {
      ElMessage.error(response.data.error);
    } else {
      loadingProgress.value = 100;
      await new Promise(r => setTimeout(r, 200));
      chartData.value = response.data;
    }
  } catch (error) {
    const errorMsg = error.response?.data?.error || '分析失败，请检查后端服务。';
    ElMessage.error(errorMsg);
  } finally {
    isLoading.value = false;
  }
};

const chartOption = computed(() => {
  if (!chartData.value) return {};

  const series = [];
  const legendData = [];

  // 现代高级调色盘：深青、丁香紫、琥珀橙、珊瑚粉等
  const colors = ['#0ea5e9', '#8b5cf6', '#f59e0b', '#f43f5e', '#10b981', '#6366f1', '#ec4899', '#14b8a6'];

  legendData.push(chartData.value.actual_data.model_name);
  series.push({
    name: chartData.value.actual_data.model_name,
    type: 'line',
    smooth: true,
    showSymbol: false,
    data: chartData.value.actual_data.data,
    lineStyle: { color: '#1e293b', width: 3 },
    areaStyle: {
      color: {
        type: 'linear',
        x: 0, y: 0, x2: 0, y2: 1,
        colorStops: [
          { offset: 0, color: 'rgba(30, 41, 59, 0.15)' },
          { offset: 1, color: 'rgba(30, 41, 59, 0.02)' }
        ]
      }
    }
  });

  chartData.value.model_predictions.forEach((model, index) => {
    legendData.push(model.model_name);
    const color = colors[index % colors.length];
    series.push({
      name: model.model_name,
      type: 'line',
      smooth: true,
      showSymbol: false,
      data: model.data,
      lineStyle: { width: 2, color: color },
      emphasis: { lineStyle: { width: 3 } }
    });
  });

  return {
    title: {
      text: '模型性能可视化对比',
      left: 'center',
      textStyle: { color: '#0f172a', fontSize: 18, fontWeight: 600, fontFamily: 'Inter, PingFang SC, sans-serif' }
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(15, 23, 42, 0.95)',
      borderColor: 'transparent',
      textStyle: { color: '#f1f5f9', fontSize: 14, fontFamily: 'Inter, PingFang SC, sans-serif' },
      padding: [12, 16],
      axisPointer: {
        type: 'cross',
        lineStyle: { color: '#94a3b8', width: 1, type: 'dashed' }
      },
      formatter: (params) => {
        let result = `<div style="font-weight: 600; margin-bottom: 8px;">${params[0].axisValue}</div>`;
        params.forEach(item => {
          result += `<div style="display: flex; align-items: center; margin: 4px 0;">
            <span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background: ${item.color}; margin-right: 8px;"></span>
            <span style="flex: 1;">${item.seriesName}</span>
            <span style="font-weight: 600; margin-left: 12px;">${item.value[1]}</span>
          </div>`;
        });
        return result;
      }
    },
    legend: {
      data: legendData,
      bottom: 20,
      textStyle: { color: '#475569', fontSize: 14, fontFamily: 'Inter, PingFang SC, sans-serif' },
      type: 'scroll',
      pageIconColor: '#0ea5e9',
      pageTextStyle: { color: '#64748b' },
      itemGap: 20
    },
    grid: { left: '3%', right: '4%', bottom: '18%', top: '12%', containLabel: true },
    xAxis: {
      type: 'value',
      name: 'X',
      splitLine: { show: false },
      axisLine: { lineStyle: { color: '#e2e8f0' } },
      axisLabel: { color: '#64748b', fontSize: 14, fontFamily: 'Inter, sans-serif', margin: 12 },
      nameTextStyle: { color: '#0f172a', fontSize: 14, fontFamily: 'Inter, sans-serif', padding: [0, 0, 0, 40] }
    },
    yAxis: {
      type: 'value',
      name: 'Y',
      splitLine: { lineStyle: { color: '#f1f5f9', type: 'dashed', width: 1 } },
      axisLine: { show: false },
      axisLabel: { color: '#64748b', fontSize: 14, fontFamily: 'Inter, sans-serif', margin: 12 },
      nameTextStyle: { color: '#0f172a', fontSize: 14, fontFamily: 'Inter, sans-serif', padding: [0, 0, 10, 0] }
    },
    series: series,
    dataZoom: [
      { type: 'inside', filterMode: 'none' },
      {
        type: 'slider',
        height: 24,
        bottom: 60,
        backgroundColor: '#f8fafc',
        fillerColor: 'rgba(14, 165, 233, 0.15)',
        borderColor: '#e2e8f0',
        handleStyle: { color: '#0ea5e9', borderColor: '#0ea5e9' },
        textStyle: { color: '#64748b', fontFamily: 'Inter, sans-serif' },
        dataBackground: { lineStyle: { color: '#cbd5e1' }, areaStyle: { color: '#e2e8f0' } }
      }
    ]
  };
});

const performanceOption = computed(() => {
  if (!chartData.value) return {};

  const sorted = chartData.value.model_predictions
    .map(m => ({ name: m.model_name, mae: m.metrics.mae }))
    .sort((a, b) => a.mae - b.mae);

  const models = sorted.map(m => m.name);
  const maeValues = sorted.map(m => m.mae);

  return {
    title: {
      text: '性能对比 (MAE)',
      left: 'center',
      textStyle: { color: '#0f172a', fontSize: 18, fontWeight: 600, fontFamily: 'Inter, PingFang SC, sans-serif' }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow', shadowStyle: { color: 'rgba(14, 165, 233, 0.05)' } },
      backgroundColor: 'rgba(15, 23, 42, 0.95)',
      borderColor: 'transparent',
      textStyle: { color: '#f1f5f9', fontSize: 14, fontFamily: 'Inter, PingFang SC, sans-serif' },
      padding: [12, 16]
    },
    grid: { left: '3%', right: '4%', bottom: '8%', top: '15%', containLabel: true },
    xAxis: {
      type: 'category',
      data: models,
      axisLine: { lineStyle: { color: '#e2e8f0' } },
      axisLabel: { color: '#64748b', rotate: 20, fontSize: 14, fontFamily: 'Inter, sans-serif', margin: 12 }
    },
    yAxis: {
      type: 'value',
      name: 'MAE',
      splitLine: { lineStyle: { color: '#f1f5f9', type: 'dashed' } },
      axisLine: { show: false },
      axisLabel: { color: '#64748b', fontSize: 14, fontFamily: 'Inter, sans-serif', margin: 12 },
      nameTextStyle: { color: '#0f172a', fontSize: 14, fontFamily: 'Inter, sans-serif' }
    },
    series: [{
      type: 'bar',
      barWidth: '50%',
      itemStyle: {
        borderRadius: [6, 6, 0, 0],
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: '#0ea5e9' },
            { offset: 1, color: '#06b6d4' }
          ]
        }
      },
      label: {
        show: true,
        position: 'top',
        formatter: '{c}',
        color: '#0f172a',
        fontSize: 13,
        fontWeight: 600,
        fontFamily: 'Inter, sans-serif'
      },
      data: maeValues
    }]
  };
});

</script>

<style scoped>
.loading-container {
  height: 400px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 1rem;
}

.progress-bar {
  width: 60%;
  height: 8px;
  background: rgba(61, 40, 23, 0.6);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #FFD700, #E0BFB8);
  transition: width 0.3s ease;
}

.loading-text {
  color: #c9a87c;
  font-size: 0.9rem;
}
</style>
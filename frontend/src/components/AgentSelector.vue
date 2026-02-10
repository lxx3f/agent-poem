<template>
  <div class="agent-selector">
    <div class="agent-selection">
      <label for="agent-select">选择智能体：</label>
      <select id="agent-select" v-model="selectedId" @change="onSelect">
        <option v-for="agent in agents" :key="agent.id" :value="agent.id">
          {{ agent.name }}
        </option>
      </select>
    </div>
    
    <!-- 显示当前选中智能体的详细信息 -->
    <div v-if="currentAgent" class="agent-details">
      <h4>{{ currentAgent.name }}</h4>
      <p class="agent-description">{{ currentAgent.description || '暂无描述' }}</p>
      <div class="agent-meta">
        <span class="agent-created">创建时间: {{ formatDate(currentAgent.created_at) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { listAgents } from '../api/agent';
import { useAgentStore } from '../stores/agent';

const agentStore = useAgentStore();
const agents = ref<any[]>([]);
const selectedId = ref<number | null>(null);
const currentAgent = ref<any>(null);

onMounted(async () => {
  const res = await listAgents({limit:50});
  if (res.data && res.data.code === 200) {
    agents.value = res.data.data.agents;
    agentStore.setAgents(agents.value);
    if (agents.value.length > 0) {
      selectedId.value = agents.value[0].id;
      currentAgent.value = agents.value[0];
      agentStore.setSelected(agents.value[0]);
    }
  }
});

const onSelect = () => {
  const agent = agents.value.find(a => a.id === selectedId.value);
  if (agent) {
    currentAgent.value = agent;
    agentStore.setSelected(agent);
  }
};

// 监听store中的选中智能体变化
watch(() => agentStore.selected, (newAgent) => {
  if (newAgent) {
    currentAgent.value = newAgent;
    if (selectedId.value !== newAgent.id) {
      selectedId.value = newAgent.id;
    }
  }
});

// 格式化日期的辅助函数
const formatDate = (dateString?: string) => {
  if (!dateString) return '未知';
  const date = new Date(dateString);
  return isNaN(date.getTime()) ? '格式错误' : date.toLocaleDateString('zh-CN');
};
</script>

<style scoped>
.agent-selector {
  margin-bottom: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  min-height: 180px; /* 固定最小高度，避免界面跳动 */
}

.agent-selection {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

select {
  padding: 0.3rem 0.5rem;
  font-size: 1rem;
  width: 100%;
}

.agent-details {
  padding: 0.75rem;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  background-color: #fafafa;
  margin-top: 0.5rem;
  flex: 1; /* 占据剩余空间 */
  min-height: 120px; /* 最小高度 */
  max-height: 120px; /* 固定最大高度 */
  overflow-y: auto; /* 超出时显示滚动条 */
  display: flex;
  flex-direction: column;
}

.agent-details h4 {
  margin: 0 0 0.5rem 0;
  font-size: 1rem;
  color: #303133;
  flex-shrink: 0; /* 不压缩标题 */
}

.agent-description {
  margin: 0 0 0.5rem 0;
  font-size: 0.875rem;
  color: #606266;
  line-height: 1.4;
  flex: 1; /* 描述占据可用空间 */
  overflow-y: auto; /* 描述过长时滚动 */
}

.agent-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  font-size: 0.75rem;
  color: #909399;
  flex-shrink: 0; /* 不压缩元信息 */
}

.agent-type, .agent-created {
  background-color: #ecf5ff;
  padding: 0.125rem 0.375rem;
  border-radius: 8px;
}

/* 深色主题适配 */
@media (prefers-color-scheme: dark) {
  .agent-details {
    border: 1px solid #4a5568;
    background-color: #2d3748;
  }
  
  .agent-details h4 {
    color: #e2e8f0;
  }
  
  .agent-description {
    color: #cbd5e0;
  }
  
  .agent-meta {
    color: #a0aec0;
  }
  
  .agent-type, .agent-created {
    background-color: #4299e1;
    color: #fff;
  }
}
</style>
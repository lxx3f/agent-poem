<template>
  <div class="conversation-list">
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
      <div 
        v-for="conv in conversations" 
        :key="conv.id" 
        :class="['conversation-item', {'active': conv.id === currentId, 'inactive': conv.id !== currentId}]" 
        @click="select(conv)">
        <div class="conversation-content">
          <span class="conversation-title">{{ conv.title || '未命名会话' }}</span>
          <span class="conversation-date">{{ formatDate(conv.updated_at) }}</span>
        </div>
      </div>
      <div v-if="conversations.length === 0" class="empty-state">暂无对话</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { listConversations } from '../api/conversation';
import { useConversationStore } from '../stores/conversation';
import { useAgentStore } from '../stores/agent';

const conversationStore = useConversationStore();
const agentStore = useAgentStore();
const conversations = ref<any[]>([]);
const currentId = ref('');
const loading = ref(false);
const error = ref('');

const fetchList = async () => {
  if (!agentStore.selected) {
    error.value = '请先选择一个智能体';
    return;
  }
  
  loading.value = true;
  error.value = '';
  
  try {
    const res = await listConversations({ agent_id: agentStore.selected.id });
    if (res.data && res.data.code === 200 && res.data.data) {
      // API返回的数据结构是 {conversations: [...], total: x}
      // 所以需要从 res.data.data.conversations 获取实际的对话列表
      const apiData = res.data.data;
      if (apiData && Array.isArray(apiData.conversations)) {
        conversations.value = apiData.conversations;
      } else {
        // 如果数据结构不符合预期，尝试直接使用apiData（以防API改变）
        conversations.value = Array.isArray(apiData) ? apiData : [];
        console.warn('API返回数据结构不符合预期，使用默认处理:', apiData);
      }
      
      conversationStore.setConversations(conversations.value);
      if (conversations.value.length > 0 && !conversationStore.currentId) {
        // 如果当前没有选中的对话，则选择第一个
        const firstConv = conversations.value[0];
        if (firstConv && firstConv.id) {
          const convId = firstConv.id.toString();
          currentId.value = convId;
          conversationStore.setCurrentId(convId);
        }
      } else if (conversationStore.currentId) {
        // 如果store中已有选中的对话，同步到本地状态
        currentId.value = conversationStore.currentId;
      }
    } else {
      error.value = res.data?.message || '获取对话列表失败';
      console.error('获取对话列表失败:', error.value);
    }
  } catch (err) {
    error.value = '网络错误，请检查后端服务是否运行';
    console.error('获取对话列表时发生错误:', err);
  } finally {
    loading.value = false;
  }
};

// 监听智能体选择的变化
watch(() => agentStore.selected, fetchList, { immediate: true });

// 监听会话变化，当store中的currentId变化时同步本地状态
watch(() => conversationStore.currentId, (newId) => {
  if (newId) {
    currentId.value = newId;
  }
}, { immediate: true });

onMounted(fetchList);

const select = (conv: any) => {
  if (!conv || typeof conv !== 'object' || !conv.id) {
    console.error('无效的对话对象:', conv);
    return;
  }
  
  const convId = conv.id.toString();
  currentId.value = convId;
  conversationStore.setCurrentId(convId);
};

// 格式化日期的辅助函数
const formatDate = (dateString?: string) => {
  if (!dateString) return '未知';
  const date = new Date(dateString);
  return isNaN(date.getTime()) ? '格式错误' : date.toLocaleDateString('zh-CN');
};
</script>

<style scoped>
.conversation-list {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  overflow-y: auto;
  max-height: calc(100vh - 220px); /* 考虑到其他元素的高度 */
}
.conversation-item {
  padding: 0.875rem;
  cursor: pointer;
  border-radius: 10px;
  transition: all 0.2s ease;
  border: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  background: white;
}
.conversation-item.active {
  background: linear-gradient(to right, #e6f7ff, #dbeafe);
  border-color: #60a5fa;
  box-shadow: 0 4px 8px rgba(59, 130, 246, 0.15);
  transform: translateX(4px);
}
.conversation-item.inactive:hover {
  background: #f1f5f9;
  border-color: #cbd5e1;
  transform: translateX(2px);
}
.conversation-content {
  display: flex;
  flex-direction: column;
  flex: 1;
}
.conversation-title {
  font-weight: 500;
  color: #2d3748;
  font-size: 0.95rem;
}
.conversation-date {
  font-size: 0.75rem;
  color: #718096;
  margin-top: 0.25rem;
}
.loading, .error, .empty-state {
  padding: 1rem;
  text-align: center;
  color: #718096;
  font-size: 0.9rem;
}
.error {
  color: #e53e3e;
  background-color: #fff5f5;
  border-radius: 8px;
  margin: 0.5rem 0;
}
</style>
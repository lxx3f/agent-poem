<template>
  <div class="message-list">
    <div v-if="messages.length === 0" class="empty-state">
      <p>此对话暂无消息</p>
    </div>
    <div v-for="msg in messages" :key="msg.id" :class="['message-item', msg.role]">
      <span class="role">{{ msg.role === 'user' ? '我' : msg.role === 'assistant' ? 'AI' : '系统' }}</span>
      <span class="content">{{ msg.content }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue';
import { useConversationStore } from '../stores/conversation';
import { listMessagesByConversation } from '../api/conversation';

const conversationStore = useConversationStore();
const messages = ref<any[]>([]);

const fetchMessages = async () => {
  if (!conversationStore.currentId) return;
  try {
    const res = await listMessagesByConversation(parseInt(conversationStore.currentId), { conversation_id: parseInt(conversationStore.currentId) });
    if (res.data && res.data.code === 200 && res.data.data && res.data.data.messages) {
      messages.value = res.data.data.messages;
    } else {
      console.error('获取消息列表失败:', res.data?.message || '未知错误');
    }
  } catch (error) {
    console.error('请求消息列表时发生错误:', error);
  }
};

// 暴露刷新方法给父组件
defineExpose({
  refresh: fetchMessages
});

watch(() => conversationStore.currentId, fetchMessages, { immediate: true });
onMounted(fetchMessages);
</script>

<style scoped>
.message-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1.5rem;
  background: #f9fafb;
  min-height: 500px;
  width: 100%; /* 确保占满父容器的宽度 */
}
.message-item {
  padding: 1rem 1.25rem;
  border-radius: 12px;
  background: #ffffff;
  box-shadow: 0 2px 6px rgba(0,0,0,0.03);
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  animation: fadeInUp 0.3s ease-out;
  word-wrap: break-word;
  max-width: 75%;  /* 统一设置最大宽度 */
}
.message-item.user {
  background: linear-gradient(to right, #dbeafe, #e6f7ff);
  align-self: flex-end;
  border: 1px solid #bfdbfe;
}
.message-item.assistant {
  background: linear-gradient(to right, #f0fdf4, #f6ffed);
  align-self: flex-start;
  border: 1px solid #bbf7d0;
}
.message-item.system {
  background: linear-gradient(to right, #fffbeb, #fffbe6);
  align-self: center;
  border: 1px solid #fde68a;
  max-width: 50%;  /* 系统消息较小的宽度 */
}
.role {
  font-weight: 700;
  font-size: 0.9rem;
  color: #2d3748;
  display: flex;
  align-items: center;
}
.content {
  color: #4a5568;
  line-height: 1.6;
}
.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 400px; /* 固定高度，确保在没有消息时也有足够空间 */
  color: #a0aec0;
  font-size: 1.2rem;
  font-style: italic;
  text-align: center;
  width: 100%; /* 确保占满宽度 */
}
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
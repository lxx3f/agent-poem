<template>
  <div class="message-list" ref="messageListRef">
    <div v-if="allMessages.length === 0" class="empty-state">
      <p>此对话暂无消息</p>
    </div>
    <div 
      v-for="msg in allMessages" 
      :key="msg.id" 
      :class="['message-item', msg.role, { 'optimistic': msg.status === 'sending' }]"
    >
      <div class="message-header">
        <span class="role">{{ getRoleDisplayName(msg.role) }}</span>
        <span v-if="msg.status === 'sending'" class="sending-indicator">
          <span class="dot-pulse"></span>
          发送中...
        </span>
      </div>
      <div class="content">{{ msg.content }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, computed, nextTick } from 'vue';
import { useConversationStore } from '../stores/conversation';
import { listMessagesByConversation } from '../api/conversation';

const props = defineProps<{
  optimisticMessages?: Array<{
    id: string;
    content: string;
    role: 'user' | 'assistant';
    timestamp: string;
    status: 'sending' | 'sent';
  }>
}>();

const conversationStore = useConversationStore();
const messages = ref<any[]>([]);
const messageListRef = ref<HTMLElement | null>(null);

// 合并真实消息和乐观消息
const allMessages = computed(() => {
  const realMsgs = [...messages.value];
  const optMsgs = props.optimisticMessages || [];
  return [...realMsgs, ...optMsgs].sort((a, b) => {
    return new Date(a.timestamp || a.created_at).getTime() - new Date(b.timestamp || b.created_at).getTime();
  });
});

const getRoleDisplayName = (role: string) => {
  switch (role) {
    case 'user': return '我';
    case 'assistant': return 'AI';
    case 'system': return '系统';
    default: return role;
  }
};

const fetchMessages = async () => {
  if (!conversationStore.currentId) return;
  try {
    const res = await listMessagesByConversation(parseInt(conversationStore.currentId), { conversation_id: parseInt(conversationStore.currentId) });
    if (res.data && res.data.code === 200 && res.data.data && res.data.data.messages) {
      messages.value = res.data.data.messages.map((msg: any) => ({
        ...msg,
        timestamp: msg.created_at
      }));
    } else {
      console.error('获取消息列表失败:', res.data?.message || '未知错误');
    }
  } catch (error) {
    console.error('请求消息列表时发生错误:', error);
  }
};

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (messageListRef.value) {
      messageListRef.value.scrollTop = messageListRef.value.scrollHeight;
    }
  });
};

// 暴露方法给父组件
defineExpose({
  refresh: fetchMessages,
  scrollToBottom: scrollToBottom
});

watch(() => conversationStore.currentId, fetchMessages, { immediate: true });

// 监听消息变化，自动滚动
watch(allMessages, () => {
  scrollToBottom();
}, { deep: true });

onMounted(() => {
  fetchMessages();
  scrollToBottom();
});
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
  min-height: 0; /* 允许flex收缩 */
  width: 100%;
  scroll-padding-bottom: 80px; /* 滚动时的底部间距 */
  scrollbar-gutter: stable; /* 保持滚动条空间 */
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
  max-width: 75%;
  transition: all 0.2s ease;
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
  max-width: 50%;
}

/* 乐观消息样式 */
.message-item.optimistic {
  opacity: 0.8;
  border-style: dashed;
  animation: pulse 2s infinite;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.sending-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8rem;
  color: #718096;
}

.dot-pulse {
  width: 8px;
  height: 8px;
  background-color: #718096;
  border-radius: 50%;
  animation: dotPulse 1.5s infinite;
}

@keyframes dotPulse {
  0%, 60%, 100% { transform: scale(1); opacity: 1; }
  30% { transform: scale(1.2); opacity: 0.5; }
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 400px;
  color: #a0aec0;
  font-size: 1.2rem;
  font-style: italic;
  text-align: center;
  width: 100%;
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

@keyframes pulse {
  0% { box-shadow: 0 2px 6px rgba(0,0,0,0.03); }
  50% { box-shadow: 0 2px 12px rgba(66, 153, 225, 0.1); }
  100% { box-shadow: 0 2px 6px rgba(0,0,0,0.03); }
}
</style>

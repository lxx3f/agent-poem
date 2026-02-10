<template>
  <div class="message-input-container">
    <form @submit.prevent="onSend" class="input-form">
      <textarea
        ref="inputRef"
        v-model="content"
        :disabled="isLoading"
        placeholder="输入消息... (按 Enter 发送，Shift+Enter 换行)"
        class="message-textarea"
        rows="1"
        @keydown.enter="handleEnterKey"
        @input="adjustTextareaHeight"
      />
      <button 
        type="submit" 
        :disabled="isSendDisabled"
        class="send-button"
        :class="{ 'sending': isLoading }"
      >
        <span v-if="!isLoading">发送</span>
        <span v-else class="sending-content">
          <span class="spinner"></span>
          {{ sendingText }}
        </span>
      </button>
    </form>
    
    <!-- 错误提示 -->
    <div v-if="error" class="error-message">
      <div class="error-content">
        <span>{{ error }}</span>
        <button v-if="canRetry" @click="retrySend" class="retry-button">
          重试
        </button>
      </div>
    </div>
    
    <!-- 加载提示 -->
    <div v-if="isLoading && showLoadingHint" class="loading-hint">
      AI正在思考中，请稍候...
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue';
import { useConversationStore } from '../stores/conversation';
import { useAgentStore } from '../stores/agent';
import { runAgent } from '../api/agent';

// 响应式数据
const content = ref('');
const isLoading = ref(false);
const error = ref('');
const inputRef = ref<HTMLTextAreaElement | null>(null);
const sendingText = ref('发送中...');
const showLoadingHint = ref(false);
const canRetry = ref(false);
const failedMessage = ref('');

// 使用 stores
const conversationStore = useConversationStore();
const agentStore = useAgentStore();

// 定义 emits
const emit = defineEmits(['message-sent', 'optimistic-message']);

// 计算属性
const isSendDisabled = computed(() => {
  return !content.value.trim() || 
         !conversationStore.currentId || 
         !agentStore.selected || 
         isLoading.value;
});

// 加载提示定时器
let loadingHintTimer: number | null = null;
let sendingTextTimer: number | null = null;

// 处理回车键
const handleEnterKey = (e: KeyboardEvent) => {
  if (e.shiftKey) {
    // Shift+Enter 换行
    return;
  }
  
  // 阻止默认换行行为并发送
  e.preventDefault();
  onSend();
};

// 调整文本域高度
const adjustTextareaHeight = () => {
  const textarea = inputRef.value;
  if (textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = `${Math.min(textarea.scrollHeight, 150)}px`;
  }
};

// 显示加载提示
const showLoadingIndicators = () => {
  // 1秒后显示加载提示
  loadingHintTimer = window.setTimeout(() => {
    showLoadingHint.value = true;
  }, 1000);
  
  // 动态更新发送文本
  const texts = ['发送中...', 'AI思考中...', '正在检索...', '整理回复中...'];
  let index = 0;
  
  sendingTextTimer = window.setInterval(() => {
    index = (index + 1) % texts.length;
    sendingText.value = texts[index] || '发送中...'; // 添加默认值
  }, 2000);
};

// 隐藏加载提示
const hideLoadingIndicators = () => {
  showLoadingHint.value = false;
  sendingText.value = '发送中...';
  
  if (loadingHintTimer) {
    clearTimeout(loadingHintTimer);
    loadingHintTimer = null;
  }
  
  if (sendingTextTimer) {
    clearInterval(sendingTextTimer);
    sendingTextTimer = null;
  }
};

// 发送消息
const onSend = async () => {
  if (isSendDisabled.value) return;

  const messageContent = content.value.trim();
  if (!messageContent) return;

  error.value = '';
  canRetry.value = false;
  failedMessage.value = messageContent;
  
  isLoading.value = true;
  showLoadingIndicators();

  try {
    // 乐观更新：立即触发消息发送事件，让用户感觉更快
    emit('optimistic-message', {
      content: messageContent,
      role: 'user',
      timestamp: new Date().toISOString()
    });
    
    // 调用后端API
    await runAgent(agentStore.selected!.id, {
      user_input: messageContent,
      conversation_id: parseInt(conversationStore.currentId)
    });
    
    // 成功后清空输入框
    content.value = '';
    adjustTextareaHeight();
    
    // 触发消息发送事件，通知父组件刷新消息列表
    emit('message-sent');
    
  } catch (err: any) {
    console.error('发送失败:', err);
    let errorMessage = '发送失败，请稍后再试';
    
    // 根据错误类型提供更具体的提示
    if (err?.code === 'ECONNABORTED') {
      errorMessage = '请求超时，请检查网络连接或稍后重试';
    } else if (err?.response?.status === 401) {
      errorMessage = '认证已过期，请重新登录';
    } else if (err?.response?.data?.message) {
      errorMessage = err.response.data.message;
    } else if (err?.message) {
      errorMessage = err.message;
    }
    
    error.value = errorMessage;
    canRetry.value = true;
  } finally {
    isLoading.value = false;
    hideLoadingIndicators();
  }
};

// 重试发送
const retrySend = () => {
  if (failedMessage.value) {
    content.value = failedMessage.value;
    onSend();
  }
};

// 组件卸载时清理定时器
onUnmounted(() => {
  hideLoadingIndicators();
});
</script>

<style scoped>
.message-input-container {
  padding: 1rem;
  border-top: 1px solid #e2e8f0;
  background: linear-gradient(to bottom, #ffffff, #f8fafc);
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.05);
  height: 160px;
  display: flex;
  flex-direction: column;
}

.input-form {
  display: flex;
  gap: 0.75rem;
  align-items: flex-end;
  border-radius: 10px;
}

.message-textarea {
  flex: 1;
  padding: 0.75rem 1rem;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  font-size: 1rem;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  resize: none;
  min-height: 56px;
  max-height: 150px;
  transition: all 0.2s ease;
  background-color: #fff;
}

.message-textarea:focus {
  outline: none;
  border-color: #4299e1;
  box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.1);
}

.message-textarea:disabled {
  background-color: #f7fafc;
  cursor: not-allowed;
  opacity: 0.7;
}

.send-button {
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #4299e1, #3182ce);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 80px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.send-button:hover:not(:disabled) {
  background: linear-gradient(135deg, #63b3ed, #4299e1);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(66, 153, 225, 0.3);
}

.send-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.send-button.sending {
  background: linear-gradient(135deg, #a0aec0, #718096);
  cursor: wait;
}

.sending-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid #e2e8f0;
  border-top: 2px solid #ffffff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  margin-top: 0.75rem;
  padding: 0.75rem 1rem;
  background-color: #fff5f5;
  border: 1px solid #fed7d7;
  border-radius: 8px;
  color: #c53030;
  font-size: 0.9rem;
}

.error-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.retry-button {
  background: #fff;
  color: #c53030;
  border: 1px solid #fed7d7;
  border-radius: 4px;
  padding: 0.25rem 0.75rem;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.retry-button:hover {
  background: #fff5f5;
}

.loading-hint {
  margin-top: 0.5rem;
  padding: 0.5rem 1rem;
  background-color: #ebf8ff;
  border: 1px solid #bee3f8;
  border-radius: 6px;
  color: #2b6cb0;
  font-size: 0.9rem;
  text-align: center;
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>

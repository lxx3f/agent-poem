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
        :disabled="isSendDisabled || isLoading"
        class="send-button"
      >
        <span v-if="!isLoading">发送</span>
        <span v-else>发送中...</span>
      </button>
    </form>
    
    <!-- 错误提示 -->
    <div v-if="error" class="error-message">
      {{ error }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted, onUnmounted } from 'vue';
import { useConversationStore } from '../stores/conversation';
import { useAgentStore } from '../stores/agent';
import { runAgent } from '../api/agent';

// 响应式数据
const content = ref('');
const isLoading = ref(false);
const error = ref('');
const inputRef = ref<HTMLTextAreaElement | null>(null);

// 使用 stores
const conversationStore = useConversationStore();
const agentStore = useAgentStore();

// 定义 emits
const emit = defineEmits(['message-sent']);

// 计算属性
const isSendDisabled = computed(() => {
  return !content.value.trim() || 
         !conversationStore.currentId || 
         !agentStore.selected || 
         isLoading.value;
});

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

// 发送消息
const onSend = async () => {
  if (isSendDisabled.value) return;

  error.value = '';
  isLoading.value = true;

  try {
    await runAgent(agentStore.selected!.id, {
      user_input: content.value,
      conversation_id: parseInt(conversationStore.currentId)
    });
    
    // 清空输入框
    content.value = '';
    adjustTextareaHeight(); // 重置文本框高度
    
    // 触发消息发送事件，通知父组件刷新消息列表
    emit('message-sent');
  } catch (err: any) {
    console.error('发送失败:', err);
    let errorMessage = '发送失败，请稍后再试';
    
    if (err?.response?.data?.message) {
      errorMessage = err.response.data.message;
    } else if (err?.message) {
      errorMessage = err.message;
    }
    
    error.value = errorMessage;
  } finally {
    isLoading.value = false;
  }
};

// 组件挂载后聚焦到输入框
onMounted(() => {
  adjustTextareaHeight();
  if (inputRef.value) {
    inputRef.value.focus();
  }
});

// 监听窗口大小变化，调整文本框高度
const handleResize = () => {
  nextTick(() => {
    adjustTextareaHeight();
  });
};

onMounted(() => {
  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
});
</script>

<style scoped>
.message-input-container {
  padding: 1rem;
  border-top: 1px solid #e2e8f0;
  background: linear-gradient(to bottom, #ffffff, #f8fafc);
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.05);
}

.input-form {
  display: flex;
  gap: 0.75rem;
  align-items: flex-end;
  border-radius: 10px;
  padding: 0.75rem;
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  border: 1px solid #e2e8f0;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.input-form:focus-within {
  border-color: #63b3ed;
  box-shadow: 0 0 0 3px rgba(99, 179, 237, 0.2);
}

.message-textarea {
  flex: 1;
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  resize: none;
  font-family: inherit;
  font-size: 1rem;
  line-height: 1.5;
  min-height: 44px;
  max-height: 150px;
  transition: border-color 0.2s, box-shadow 0.2s;
  background-color: #f8fafc;
}

.message-textarea:focus {
  outline: none;
  border-color: #63b3ed;
  box-shadow: 0 0 0 3px rgba(99, 179, 237, 0.1);
  background-color: white;
}

.message-textarea:disabled {
  background-color: #edf2f7;
  cursor: not-allowed;
}

.send-button {
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  font-weight: 500;
  color: #fff;
  background: linear-gradient(135deg, #4299e1, #3182ce);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  box-shadow: 0 2px 4px rgba(66, 153, 225, 0.3);
}

.send-button:hover:not(:disabled) {
  background: linear-gradient(135deg, #63b3ed, #4299e1);
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(66, 153, 225, 0.4);
}

.send-button:disabled {
  background: #a0aec0;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.error-message {
  margin-top: 0.75rem;
  padding: 0.75rem;
  color: #e53e3e;
  font-size: 0.9rem;
  background-color: #fff5f5;
  border-radius: 8px;
  border-left: 4px solid #fc8181;
  animation: shake 0.3s ease-in-out;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}
</style>
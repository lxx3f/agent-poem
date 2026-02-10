<template>
  <div class="chat-view">
    <div v-if="error" class="error">
      <p>{{ error }}</p>
      <button @click="retryGetUserInfo">重试</button>
    </div>
    <div v-else-if="!user" class="loading">
      加载中...
    </div>
    <div v-else class="chat-layout">
      <div class="chat-sidebar">
        <div class="sidebar-header">诗云AI助手</div>
        
        <!-- 上半部分：Agent选择和Prompt编辑 -->
        <div class="sidebar-top">
          <AgentSelector />
          
          <!-- Agent Prompt 编辑区域 -->
          <div v-if="agentStore.selected" class="prompt-editor-section">
            <div class="prompt-header" @click="togglePromptEditor">
              <h3>游戏规则设置</h3>
              <span class="toggle-icon" :class="{ 'expanded': showPromptEditor }">
                ▼
              </span>
            </div>
            <div v-show="showPromptEditor" class="prompt-content">
              <textarea 
                v-model="agentPrompt"
                class="prompt-textarea"
                placeholder="请输入agent的游戏规则提示词..."
                rows="6"
              ></textarea>
              <div class="prompt-actions">
                <button 
                  @click="resetPrompt" 
                  class="btn-reset"
                  :disabled="isSaving"
                >
                  重置
                </button>
                <button 
                  @click="savePrompt" 
                  class="btn-save"
                  :disabled="isSaving || !hasPromptChanged"
                >
                  {{ isSaving ? '保存中...' : '保存' }}
                </button>
              </div>
              <div v-if="saveMessage" class="save-message" :class="saveMessageType">
                {{ saveMessage }}
              </div>
            </div>
          </div>
        </div>
        
        <!-- 下半部分：会话列表 -->
        <div class="sidebar-bottom">
          <div class="conversation-section">
            <div class="conversation-header">
              <h3>对话记录</h3>
              <button 
                v-if="agentStore.selected"
                @click="showCreateDialog = true"
                class="new-conversation-btn"
                title="新建对话"
              >+</button>
            </div>
            <div class="conversation-list-container">
              <ConversationList />
            </div>
          </div>
        </div>
      </div>
      
      <div class="chat-main">
        <div class="chat-header">
          <div class="user-info">
            欢迎, {{ user.nickname }}
          </div>
          <div class="user-actions">
            <router-link to="/profile" class="profile-link">个人资料</router-link>
          </div>
        </div>
        <div class="chat-content">
          <MessageList 
            ref="messageListRef" 
            v-if="conversationStore.currentId" 
            :optimistic-messages="optimisticMessages"
          />
          <div v-else class="no-conversation-selected">
            请选择一个对话开始聊天
          </div>
        </div>
        <div class="message-input-container">
          <MessageInput 
            v-if="conversationStore.currentId" 
            @message-sent="refreshMessages"
            @optimistic-message="handleOptimisticMessage"
          />
        </div>
      </div>
    </div>
    
    <!-- 创建新对话的模态框 -->
    <div v-if="showCreateDialog" class="modal-overlay" @click="closeCreateDialog">
      <div class="modal-content" @click.stop>
        <h3>创建新对话</h3>
        <div class="modal-body">
          <label>对话名称:</label>
          <input 
            v-model="newConversationTitle" 
            type="text" 
            class="title-input"
            placeholder="请输入对话名称"
            @keyup.enter="confirmCreateNewConversation"
            ref="titleInputRef"
          />
        </div>
        <div class="modal-footer">
          <button @click="closeCreateDialog" class="btn-cancel">取消</button>
          <button @click="confirmCreateNewConversation" class="btn-confirm">创建</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, watch, computed } from 'vue';
import { getMe } from '../api/auth';
import { useRouter } from 'vue-router';
import { useConversationStore } from '../stores/conversation';
import { useAgentStore } from '../stores/agent';
import { createConversation } from '../api/conversation';
import { updateAgentSystemPrompt } from '../api/agent';
import AgentSelector from '../components/AgentSelector.vue';
import ConversationList from '../components/ConversationList.vue';
import MessageList from '../components/MessageList.vue';
import MessageInput from '../components/MessageInput.vue';

const user = ref<{ nickname: string; email: string } | null>(null);
const error = ref('');
const router = useRouter();
const conversationStore = useConversationStore();
const agentStore = useAgentStore();
const showCreateDialog = ref(false);
const newConversationTitle = ref('');
const messageListRef = ref(null);
const titleInputRef = ref<HTMLInputElement|null>(null);

// Prompt编辑相关
const showPromptEditor = ref(false);
const agentPrompt = ref('');
const originalPrompt = ref('');
const isSaving = ref(false);
const saveMessage = ref('');
const saveMessageType = ref<'success' | 'error'>('success');

// 乐观更新相关
const optimisticMessages = ref<Array<{
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: string;
  status: 'sending' | 'sent';
}>>([]);

const getUserInfo = async () => {
  try {
    const res = await getMe();
    if (res.data && res.data.code === 200 && res.data.data) {
      user.value = res.data.data;
      error.value = '';
    } else {
      error.value = res.data?.message || '获取用户信息失败';
    }
  } catch (err: any) {
    console.error('获取用户信息出错:', err);
    error.value = err?.response?.data?.message || err?.message || '网络错误，请检查后端服务是否运行';
    
    // 如果是认证错误，跳转到登录页
    if (err?.response?.status === 401) {
      router.push('/login');
    }
  }
};

const retryGetUserInfo = () => {
  getUserInfo();
};

const closeCreateDialog = () => {
  showCreateDialog.value = false;
  newConversationTitle.value = '';
};

const confirmCreateNewConversation = async () => {
  if (!agentStore.selected) {
    alert('请先选择一个智能体');
    return;
  }

  try {
    const title = newConversationTitle.value.trim() || `新对话 ${new Date().toLocaleString('zh-CN')}`;
    const response = await createConversation({
      title: title,
      agent_id: agentStore.selected.id,
    });

    if (response.data && response.data.code === 200 && response.data.data) {
      // 检查返回的数据结构
      let newConv;
      if (response.data.data.conversation) {
        // 如果API返回的是 { conversation: {...} } 结构
        newConv = response.data.data.conversation;
      } else if (response.data.data.conversation_id) {
        // 如果API只返回了 conversation_id，需要获取完整的对话信息
        // 创建一个临时对象包含所需信息
        newConv = {
          id: response.data.data.conversation_id,
          title: title,
          agent_id: agentStore.selected.id,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        };
      } else {
        // 如果API直接返回对话对象
        newConv = response.data.data;
      }
      
      if (!newConv || !newConv.id) {
        console.error('API返回的数据中缺少必要的id字段:', newConv);
        throw new Error('创建的对话缺少ID');
      }
      
      // 更新会话列表和当前选中的会话
      conversationStore.conversations.unshift(newConv);
      conversationStore.setCurrentId(newConv.id.toString());
      
      // 关闭对话框
      closeCreateDialog();
    } else {
      throw new Error(response.data?.message || '创建对话失败');
    }
  } catch (err) {
    console.error('创建对话失败:', err);
    alert('创建新对话失败，请重试');
  }
};

// 刷新消息列表
const refreshMessages = () => {
  // 清除乐观消息
  optimisticMessages.value = [];
  
  if (messageListRef.value) {
    // 调用MessageList组件的refresh方法
    (messageListRef.value as any).refresh();
  }
};

// 处理乐观消息
const handleOptimisticMessage = (message: { content: string; role: 'user'; timestamp: string }) => {
  const optimisticMessage = {
    id: `optimistic-${Date.now()}`,
    content: message.content,
    role: message.role,
    timestamp: message.timestamp,
    status: 'sending' as const
  };
  
  optimisticMessages.value.push(optimisticMessage);
  
  // 滚动到底部
  nextTick(() => {
    if (messageListRef.value) {
      (messageListRef.value as any).scrollToBottom();
    }
  });
};

// Prompt编辑相关方法
const togglePromptEditor = () => {
  showPromptEditor.value = !showPromptEditor.value;
  if (showPromptEditor.value && agentStore.selected) {
    loadAgentPrompt();
  }
};

const loadAgentPrompt = () => {
  if (agentStore.selected) {
    agentPrompt.value = agentStore.selected.system_prompt || '';
    originalPrompt.value = agentPrompt.value;
  }
};

const hasPromptChanged = computed(() => {
  return agentPrompt.value !== originalPrompt.value;
});

const resetPrompt = () => {
  agentPrompt.value = originalPrompt.value;
  saveMessage.value = '';
};

const savePrompt = async () => {
  if (!agentStore.selected || !hasPromptChanged.value) return;
  
  isSaving.value = true;
  saveMessage.value = '';
  
  try {
    const response = await updateAgentSystemPrompt(agentStore.selected.id, {
      system_prompt: agentPrompt.value
    });
    
    if (response.data && response.data.code === 200) {
      // 更新store中的agent信息
      agentStore.selected.system_prompt = agentPrompt.value;
      originalPrompt.value = agentPrompt.value;
      
      saveMessageType.value = 'success';
      saveMessage.value = '保存成功！';
      
      // 3秒后清除消息
      setTimeout(() => {
        saveMessage.value = '';
      }, 3000);
    } else {
      throw new Error(response.data?.message || '保存失败');
    }
  } catch (err: any) {
    console.error('保存prompt失败:', err);
    saveMessageType.value = 'error';
    saveMessage.value = err?.response?.data?.message || err?.message || '保存失败，请重试';
  } finally {
    isSaving.value = false;
  }
};

onMounted(async () => {
  await getUserInfo();
  
  // 监听点击事件，当点击模态框外部时关闭
  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && showCreateDialog.value) {
      closeCreateDialog();
    }
  });
});

// 当模态框显示时，自动聚焦到输入框
watch(showCreateDialog, async (newValue) => {
  if (newValue) {
    await nextTick();
    if (titleInputRef.value) {
      titleInputRef.value.focus();
    }
  }
});

// 监听agent选择变化
watch(() => agentStore.selected, (newAgent) => {
  if (newAgent && showPromptEditor.value) {
    loadAgentPrompt();
  }
});

// 监听会话切换，清空乐观消息
watch(() => conversationStore.currentId, () => {
  optimisticMessages.value = [];
});

</script>

<style scoped>
.chat-view { 
  display: flex; 
  flex-direction: column; 
  height: 100vh; 
  background-color: #f9fafb;
  overflow: hidden; /* 防止整体页面溢出 */
}

.error { 
  padding: 2rem; 
  text-align: center; 
  color: #f56565;
  background-color: #fff5f5;
  border: 1px solid #fed7d7;
  border-radius: 8px;
  margin: 1rem;
}

.loading { 
  padding: 2rem; 
  text-align: center; 
  color: #4a5568;
}

.chat-layout {
  display: flex;
  height: 100%; /* 改为100%，继承父容器高度 */
  flex: 1;
  margin: 10px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

/* 左侧侧边栏核心布局修改 */
.chat-sidebar {
  width: 280px;
  background: linear-gradient(to bottom, #ffffff, #f8fafc);
  border-right: 1px solid #e2e8f0;
  padding: 1.5rem 1rem;
  /* 关键：设置垂直flex布局 */
  display: flex;
  flex-direction: column;
  gap: 1rem; /* 各部分之间的间距 */
  height: 100%;
  overflow: hidden; /* 防止侧边栏整体溢出 */
}

.sidebar-header {
  font-weight: 700;
  font-size: 1.3rem;
  color: #2d3748;
  text-align: center;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #ebf8ff;
  flex-shrink: 0; /* 固定头部，不压缩 */
}

/* 侧边栏上半部分：Agent选择+Prompt编辑 */
.sidebar-top {
  flex-shrink: 0; /* 自适应高度，不压缩 */
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* 侧边栏下半部分：会话列表 - 占剩余空间 */
.sidebar-bottom {
  flex: 1; /* 占据剩余所有空间 */
  overflow: hidden; /* 内部滚动，不影响外部 */
}

.conversation-section {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.conversation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #edf2f7;
  flex-shrink: 0; /* 固定头部，不压缩 */
}

.conversation-header h3 {
  margin: 0;
  font-size: 1.1rem;
  color: #4a5568;
  font-weight: 600;
}

/* 会话列表容器 - 可滚动 */
.conversation-list-container {
  flex: 1;
  overflow-y: auto; /* 内容超出时垂直滚动 */
  padding-right: 4px; /* 滚动条间距 */
}

/* 隐藏滚动条（可选，美化用） */
.conversation-list-container::-webkit-scrollbar {
  width: 6px;
}
.conversation-list-container::-webkit-scrollbar-thumb {
  background-color: #cbd5e0;
  border-radius: 3px;
}
.conversation-list-container::-webkit-scrollbar-track {
  background-color: #f1f5f9;
}

.new-conversation-btn {
  background: linear-gradient(135deg, #4299e1, #3182ce);
  color: white;
  border: none;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  cursor: pointer;
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 4px rgba(66, 153, 225, 0.4);
  transition: all 0.2s ease;
}

.new-conversation-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 4px 8px rgba(66, 153, 225, 0.5);
  background: linear-gradient(135deg, #63b3ed, #4299e1);
}

/* Prompt编辑区样式 */
.prompt-editor-section {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  overflow: hidden;
}

.prompt-header {
  padding: 0.75rem 1rem;
  background: linear-gradient(to right, #4299e1, #3182ce);
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  user-select: none;
  transition: background 0.2s ease;
}

.prompt-header:hover {
  background: linear-gradient(to right, #63b3ed, #4299e1);
}

.prompt-header h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
}

.toggle-icon {
  transition: transform 0.3s ease;
  font-size: 0.8rem;
}

.toggle-icon.expanded {
  transform: rotate(180deg);
}

.prompt-content {
  padding: 1rem;
  border-top: 1px solid #e2e8f0;
}

.prompt-textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 0.9rem;
  font-family: 'Courier New', monospace;
  resize: vertical;
  min-height: 120px;
  box-sizing: border-box;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.prompt-textarea:focus {
  outline: none;
  border-color: #63b3ed;
  box-shadow: 0 0 0 2px rgba(99, 179, 237, 0.2);
}

.prompt-actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 1rem;
  justify-content: flex-end;
}

.btn-reset, .btn-save {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.2s ease;
}

.btn-reset {
  background: #e2e8f0;
  color: #4a5568;
}

.btn-reset:hover:not(:disabled) {
  background: #cbd5e0;
}

.btn-reset:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-save {
  background: linear-gradient(135deg, #48bb78, #38a169);
  color: white;
}

.btn-save:hover:not(:disabled) {
  background: linear-gradient(135deg, #68d391, #48bb78);
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(72, 187, 120, 0.3);
}

.btn-save:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.save-message {
  margin-top: 0.75rem;
  padding: 0.5rem 0.75rem;
  border-radius: 4px;
  font-size: 0.85rem;
  text-align: center;
}

.save-message.success {
  background: #f0fff4;
  color: #38a169;
  border: 1px solid #9ae6b4;
}

.save-message.error {
  background: #fff5f5;
  color: #e53e3e;
  border: 1px solid #feb2b2;
}

/* 右侧聊天区域 */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #fff;
  overflow: hidden; /* 防止内部溢出 */
}

.chat-header {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e2e8f0;
  background: linear-gradient(to right, #ffffff, #f8fafc);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0; /* 固定头部 */
}

.user-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-info {
  font-weight: 600;
  color: #2b6cb0;
  font-size: 1.1rem;
}

.profile-link {
  color: #4299e1;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  background-color: #ebf8ff;
  transition: all 0.2s ease;
  font-weight: 500;
}

.profile-link:hover {
  background-color: #bee3f8;
  transform: translateY(-1px);
}

.chat-content {
  flex: 1;
  overflow-y: auto; /* 聊天记录可滚动 */
  background: #f9fafb;
  padding: 1rem; /* 内边距，优化显示 */
}

.no-conversation-selected {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #a0aec0;
  font-size: 1.1rem;
  font-weight: 500;
}

/* 输入框容器 - 固定在底部 */
.message-input-container {
  padding: 1rem;
  border-top: 1px solid #e2e8f0;
  background-color: #fff;
  flex-shrink: 0; /* 固定高度，不压缩 */
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal-content {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  width: 90%;
  max-width: 450px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  animation: modalSlideIn 0.3s ease-out;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-body {
  margin: 1.25rem 0;
}

.modal-body label {
  display: block;
  margin-bottom: 0.75rem;
  font-weight: 600;
  color: #4a5568;
}

.title-input {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 1rem;
  box-sizing: border-box;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.title-input:focus {
  outline: none;
  border-color: #63b3ed;
  box-shadow: 0 0 0 3px rgba(99, 179, 237, 0.2);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 0.5rem;
}

.btn-cancel, .btn-confirm {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  transition: all 0.2s ease;
}

.btn-cancel {
  background: #e2e8f0;
  color: #4a5568;
}

.btn-cancel:hover {
  background: #cbd5e0;
}

.btn-confirm {
  background: linear-gradient(135deg, #4299e1, #3182ce);
  color: white;
}

.btn-confirm:hover {
  background: linear-gradient(135deg, #63b3ed, #4299e1);
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(66, 153, 225, 0.3);
}
</style>

<template>
  <div class="chat-view">
    <div v-if="error" class="error">
      {{ error }}
      <button @click="retryGetUserInfo">重试</button>
    </div>
    <div v-else-if="!user" class="loading">正在加载用户信息...</div>
    <div v-else class="chat-layout">
      <div class="chat-sidebar">
        <div class="sidebar-header">智能助手</div>
        <AgentSelector />
        <div class="conversation-section">
          <div class="conversation-header">
            <h3>对话历史</h3>
            <button @click="showCreateDialog = true" class="new-conversation-btn" title="新建对话">
              +
            </button>
          </div>
          <ConversationList />
        </div>
      </div>
      <div class="chat-main">
        <div class="chat-header">
          <div class="user-actions">
            <span class="user-info">欢迎，{{ user.nickname || '用户' }}!</span>
            <router-link to="/profile" class="profile-link">个人资料</router-link>
          </div>
        </div>
        <div class="chat-content">
          <MessageList ref="messageListRef" v-if="conversationStore.currentId" />
          <div v-else class="no-conversation-selected">
            请选择一个对话开始聊天
          </div>
        </div>
        <MessageInput v-if="conversationStore.currentId" @message-sent="refreshMessages" />
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
import { ref, onMounted, nextTick, watch } from 'vue';
import { getMe } from '../api/auth';
import { useRouter } from 'vue-router';
import { useConversationStore } from '../stores/conversation';
import { useAgentStore } from '../stores/agent';
import { createConversation } from '../api/conversation';
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
  if (messageListRef.value) {
    // 调用MessageList组件的refresh方法
    (messageListRef.value as any).refresh();
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
</script>

<style scoped>
.chat-view { 
  display: flex; 
  flex-direction: column; 
  height: 100vh; 
  background-color: #f9fafb;
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
  height: calc(100vh - 20px);
  flex: 1;
  margin: 10px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}
.chat-sidebar {
  width: 280px;
  background: linear-gradient(to bottom, #ffffff, #f8fafc);
  border-right: 1px solid #e2e8f0;
  padding: 1.5rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  box-sizing: border-box;
  transition: all 0.3s ease;
}
.sidebar-header {
  font-weight: 700;
  margin-bottom: 1rem;
  font-size: 1.3rem;
  color: #2d3748;
  text-align: center;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #ebf8ff;
}
.conversation-section {
  flex: 1;
}
.conversation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #edf2f7;
}
.conversation-header h3 {
  margin: 0;
  font-size: 1.1rem;
  color: #4a5568;
  font-weight: 600;
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
.no-conversation-selected {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #a0aec0;
  font-size: 1.1rem;
  font-weight: 500;
}
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #fff;
}
.chat-header {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e2e8f0;
  background: linear-gradient(to right, #ffffff, #f8fafc);
  display: flex;
  justify-content: space-between;
  align-items: center;
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
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #f9fafb;
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
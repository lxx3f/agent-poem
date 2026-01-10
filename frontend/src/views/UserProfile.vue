<template>
  <div class="profile-container">
    <div class="profile-card">
      <div class="profile-header">
        <h2>个人资料</h2>
      </div>
      
      <div class="profile-content">
        <div class="avatar-section">
          <div class="avatar">
            <span class="initials">{{ userInitials }}</span>
          </div>
          <div class="upload-avatar">
            <button @click="changeAvatar" class="avatar-btn">更换头像</button>
          </div>
        </div>

        <div class="info-section">
          <div class="info-row">
            <label>用户名：</label>
            <div class="editable-field">
              <span v-if="!editingNickname" @dblclick="enableEditNickname" class="field-value">{{ user?.nickname || '未设置' }}</span>
              <input 
                v-else 
                v-model="tempNickname" 
                type="text" 
                class="edit-input"
                @blur="saveNickname"
                @keyup.enter="saveNickname"
                ref="nicknameInputRef"
              />
              <button 
                v-if="editingNickname" 
                @click="saveNickname" 
                class="save-btn"
                :disabled="!tempNickname.trim()"
              >
                保存
              </button>
            </div>
          </div>
          
          <div class="info-row">
            <label>邮箱：</label>
            <span>{{ user?.email || '未设置' }}</span>
          </div>
          
          <div class="info-row">
            <label>注册时间：</label>
            <span>{{ formatDate(user?.created_at) || '未知' }}</span>
          </div>
          
          <div class="info-row">
            <label>最后登录：</label>
            <span>{{ formatDate(user?.last_login) || '未知' }}</span>
          </div>
        </div>

        <div class="actions">
          <button @click="changePassword" class="password-btn">修改密码</button>
          <button @click="logout" class="logout-btn">退出登录</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue';
import { getMe, updateProfile } from '../api/auth';
import { useRouter } from 'vue-router';

const user = ref<{ nickname: string; email: string; created_at?: string; last_login?: string } | null>(null);
const editingNickname = ref(false);
const tempNickname = ref('');
const router = useRouter();
const nicknameInputRef = ref<HTMLInputElement|null>(null);

const userInitials = computed(() => {
  if (!user.value?.nickname) return '?';
  return user.value.nickname.charAt(0).toUpperCase();
});

const getUserInfo = async () => {
  try {
    const res = await getMe();
    if (res.data && res.data.code === 200 && res.data.data) {
      user.value = res.data.data;
    } else {
      console.error('获取用户信息失败:', res.data?.message);
    }
  } catch (err) {
    console.error('获取用户信息时发生错误:', err);
  }
};

const enableEditNickname = () => {
  if (!user.value) return;
  tempNickname.value = user.value.nickname;
  editingNickname.value = true;
  
  // 在下一个tick聚焦输入框
  nextTick(() => {
    if (nicknameInputRef.value) {
      nicknameInputRef.value.focus();
      nicknameInputRef.value.select(); // 选中文本以便用户可以直接输入
    }
  });
};

const saveNickname = async () => {
  if (!editingNickname.value || !tempNickname.value.trim()) return;
  
  if (!user.value) return;
  
  try {
    const response = await updateProfile({ nickname: tempNickname.value.trim() });
    
    if (response.data && response.data.code === 200) {
      // 更新本地用户信息
      user.value.nickname = tempNickname.value.trim();
      editingNickname.value = false;
      alert('用户名更新成功！');
    } else {
      alert(response.data?.message || '更新失败，请重试');
    }
  } catch (err: any) {
    console.error('更新用户名时发生错误:', err);
    let errorMessage = '更新失败，请重试';
    
    if (err?.response?.data?.message) {
      errorMessage = err.response.data.message;
    } else if (err?.message) {
      errorMessage = err.message;
    }
    
    alert(errorMessage);
  }
};

const formatDate = (dateStr?: string) => {
  if (!dateStr) return '未知';
  const date = new Date(dateStr);
  return isNaN(date.getTime()) ? '格式错误' : date.toLocaleDateString('zh-CN');
};

const changeAvatar = () => {
  alert('头像上传功能将在后续版本中实现');
};

const changePassword = () => {
  alert('修改密码功能将在后续版本中实现');
};

const logout = () => {
  localStorage.removeItem('token');
  router.push('/login');
};

onMounted(() => {
  getUserInfo();
});
</script>

<style scoped>
.profile-container {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: 2rem;
  min-height: 100vh;
  background-color: #f9fafb;
}

.profile-card {
  width: 100%;
  max-width: 600px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.profile-header {
  background: linear-gradient(135deg, #4299e1, #3182ce);
  color: white;
  padding: 1.5rem;
  text-align: center;
}

.profile-header h2 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
}

.profile-content {
  padding: 2rem;
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 2rem;
}

.avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1rem;
}

.initials {
  font-size: 2.5rem;
  font-weight: bold;
  color: white;
}

.upload-avatar .avatar-btn {
  padding: 0.5rem 1rem;
  background: #e2e8f0;
  border: none;
  border-radius: 6px;
  color: #4a5568;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
}

.upload-avatar .avatar-btn:hover {
  background: #cbd5e0;
}

.info-section {
  margin-bottom: 2rem;
}

.info-row {
  display: flex;
  padding: 0.75rem 0;
  border-bottom: 1px solid #edf2f7;
}

.info-row:last-child {
  border-bottom: none;
}

.info-row label {
  width: 100px;
  font-weight: 600;
  color: #4a5568;
}

.field-value {
  flex: 1;
  color: #718096;
  cursor: pointer;
}

.field-value:hover {
  background-color: #f7fafc;
  padding: 0.25rem;
  border-radius: 4px;
  color: #2d3748;
}

.editable-field {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
}

.edit-input {
  flex: 1;
  padding: 0.5rem;
  border: 1px solid #cbd5e0;
  border-radius: 4px;
  font-size: 0.9rem;
}

.edit-input:focus {
  outline: none;
  border-color: #63b3ed;
  box-shadow: 0 0 0 2px rgba(99, 179, 237, 0.2);
}

.save-btn {
  padding: 0.4rem 0.8rem;
  background: #4299e1;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
  transition: background 0.2s;
}

.save-btn:disabled {
  background: #a0aec0;
  cursor: not-allowed;
}

.save-btn:not(:disabled):hover {
  background: #63b3ed;
}

.actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.password-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  background: #e2e8f0;
  color: #4a5568;
}

.password-btn:hover {
  background: #cbd5e0;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.logout-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  background: linear-gradient(135deg, #e53e3e, #c53030);
  color: white;
}

.logout-btn:hover {
  background: linear-gradient(135deg, #fc8181, #e53e3e);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(229, 62, 62, 0.3);
}
</style>
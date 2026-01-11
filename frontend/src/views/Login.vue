
<template>
	<div class="login-view">
		<h2>登录</h2>
		<form @submit.prevent="onSubmit" class="login-form">
			<div class="form-item">
				<label for="email">邮箱</label>
				<input v-model="email" id="email" type="email" required autocomplete="username" />
			</div>
			<div class="form-item">
				<label for="password">密码</label>
				<input v-model="password" id="password" type="password" required autocomplete="current-password" />
			</div>
			<div class="form-item">
				<button type="submit" :disabled="loading">{{ loading ? '登录中...' : '登录' }}</button>
			</div>
			<div v-if="error" class="error">{{ error }}</div>
		</form>
		<div class="register-link">
      <p>还没有账号？<a href="/register">立即注册</a></p>
    </div>
	</div>
</template>

<script setup lang="ts">
import { logInfo } from '../utils/logger';
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { login } from '../api/auth';

const email = ref('');
const password = ref('');
const loading = ref(false);
const error = ref('');
const router = useRouter();

const onSubmit = async () => {
	error.value = '';
	loading.value = true;
	try {
		const response = await login({ email: email.value, password: password.value });
    // logInfo('response:', { user: response });
    // 检查 data 子对象是否存在，且包含 access_token
		if (response && response.data.code === 200) {
			const accessToken = response.data.data.access_token; // 从 data 中读取
      logInfo('access_token:', { accessToken });
			localStorage.setItem('token', accessToken);
			// logInfo('登录成功', { user: response });
			router.push('/chat');
		} else {
			error.value = response.data.message;
		}
	} catch (e: any) {
		// 提供更详细的错误信息
		if (e?.response?.data?.message) {
			error.value = e.response.data.message;
		} else if (e?.message) {
			error.value = e.message;
		} else {
			error.value = '网络错误，请稍后重试';
		}
	} finally {
		loading.value = false;
	}
};
</script>

<style scoped>
.login-form {
  width: 100%;
  max-width: 400px;
  margin: 0 auto;
  padding: 2rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.form-item {
  display: flex;
  flex-direction: column;
  margin-bottom: 1rem;
}

.form-item label {
  margin-bottom: 0.5rem;
  font-weight: bold;
}

.form-item input {
  padding: 0.75rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 1rem;
  width: 100%; /* 确保输入框占满容器 */
  box-sizing: border-box; /* 包含padding在内的总宽度计算 */
}

.form-item button {
  width: 100%;
  padding: 0.75rem;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
}

.form-item button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.error { 
  color: red; 
  margin-top: 0.5rem; 
  text-align: center;
}

.register-link { 
  margin-top: 1rem; 
  text-align: center; 
}

.register-link a { 
  color: #007bff; 
  text-decoration: none; 
}

.register-link a:hover { 
  text-decoration: underline; 
}
</style>

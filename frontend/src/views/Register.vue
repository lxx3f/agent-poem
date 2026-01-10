<template>
  <div class="register-view">
    <h2>注册</h2>
    <form @submit.prevent="onSubmit" class="register-form">
      <div class="form-item">
        <label for="email">邮箱</label>
        <input v-model="email" id="email" type="email" required autocomplete="username" />
      </div>
      <div class="form-item">
        <label for="password">密码</label>
        <input v-model="password" id="password" type="password" required minlength="6" autocomplete="new-password" />
      </div>
      <div class="form-item">
        <label for="nickname">昵称</label>
        <input v-model="nickname" id="nickname" type="text" />
      </div>
      <div class="form-item">
        <button type="submit" :disabled="loading">{{ loading ? '注册中...' : '注册' }}</button>
      </div>
      <div v-if="error" class="error">{{ error }}</div>
      <div v-if="success" class="success">注册成功，请前往登录！</div>
    </form>
    <div class="login-link">
      <p>已有账号？<a href="/login">立即登录</a></p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { register } from '../api/auth';

const email = ref('');
const password = ref('');
const nickname = ref('');
const loading = ref(false);
const error = ref('');
const success = ref(false);
const router = useRouter();

const onSubmit = async () => {
  error.value = '';
  success.value = false;
  loading.value = true;
  try {
    const response = await register({ email: email.value, password: password.value, nickname: nickname.value });
    // 检查响应中是否包含用户信息（注册成功后返回的用户数据）
    if (response && response.data.code === 200) {
      success.value = true;
      // console.log('注册成功', { user: response });
      setTimeout(() => {
        router.push('/login');
      }, 1000);
    } else {
      error.value = response?.data?.message || '注册失败';
    }
  } catch (e: any) {
    error.value = e?.response?.data?.message || '网络错误';
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.register-view { padding: 2rem; max-width: 350px; margin: 0 auto; }
.register-form { display: flex; flex-direction: column; gap: 1rem; }
.form-item { display: flex; flex-direction: column; }
input { padding: 0.5rem; font-size: 1rem; }
button { padding: 0.5rem; font-size: 1rem; cursor: pointer; }
.error { color: red; margin-top: 0.5rem; }
.success { color: green; margin-top: 0.5rem; }
</style>

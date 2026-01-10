import { createRouter, createWebHistory } from 'vue-router';
import Login from '../views/Login.vue';
import Register from '../views/Register.vue';
import Chat from '../views/Chat.vue';
import UserProfile from '../views/UserProfile.vue';

const routes = [
    {
        path: '/',
        redirect: '/login',
    },
    {
        path: '/login',
        name: 'Login',
        component: Login,
        meta: { guest: true },
    },
    {
        path: '/register',
        name: 'Register',
        component: Register,
        meta: { guest: true },
    },
    {
        path: '/chat',
        name: 'Chat',
        component: Chat,
        meta: { requiresAuth: true },
    },
    {
        path: '/profile',
        name: 'UserProfile',
        component: UserProfile,
        meta: { requiresAuth: true },
    },
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

router.beforeEach((to, _from, next) => {
    const token = localStorage.getItem('token');
    if (to.meta.requiresAuth && !token) {
        next('/login');
    } else if (to.name === 'Login' && token) {
        // 当用户访问登录页且已登录时，可以选择是否仍停留在登录页还是跳转到聊天页
        next();
    } else if (to.name === 'Register' && token) {
        next();
    } else {
        next();
    }
});

export default router;
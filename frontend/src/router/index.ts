import { createRouter, createWebHistory } from "vue-router";
import Login from "@/views/Login.vue";
import Chat from "@/views/Chat.vue";

const router = createRouter({
    history: createWebHistory(),
    routes: [
        { path: "/login", component: Login },
        { path: "/", component: Chat },
    ],
});

export default router;

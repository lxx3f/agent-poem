import { createApp } from 'vue'
import { createPinia } from 'pinia'
import './style.css'
import App from './App.vue'
import router from './router'
import { logger, logInfo, LogLevel } from './utils/logger';

logger.setLogLevel(LogLevel.INFO);
// 记录应用启动
logInfo('Application starting...', {
    userAgent: navigator.userAgent,
    timestamp: new Date().toISOString()
});

// 全局错误处理
window.addEventListener('error', (event) => {
    logger.error(`Global error: ${event.message}`, {
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
        error: event.error?.stack
    });
});

window.addEventListener('unhandledrejection', (event) => {
    logger.error(`Unhandled promise rejection: ${event.reason}`, {
        reason: event.reason instanceof Error ? event.reason.stack : event.reason
    });
});

const app = createApp(App);
const pinia = createPinia();
app.use(router);
app.use(pinia);
app.mount('#app');

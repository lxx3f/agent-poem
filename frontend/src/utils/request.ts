import axios from "axios";

const request = axios.create({
    baseURL: import.meta.env.VITE_API_BASE || "http://localhost:8000/api",
    timeout: 60000, // 从20秒增加到60秒，适应LLM处理时间
});

request.interceptors.request.use((config) => {
    const token = localStorage.getItem("token");
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

request.interceptors.response.use(
    (res) => {
        return res;
    },
    (err) => {
        if (err.response?.status === 401) {
            localStorage.removeItem("token");
            window.location.href = "/login";
        }
        return Promise.reject(err);
    }
);


export default request;
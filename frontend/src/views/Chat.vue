<template>
  <div class="chat-view">
    <AgentSelector />
    <ConversationList />
    <MessageList />
    <MessageInput />
  </div>
</template>
<script setup lang="ts">
import AgentSelector from '../components/AgentSelector.vue';
import ConversationList from '../components/ConversationList.vue';
import MessageList from '../components/MessageList.vue';
import MessageInput from '../components/MessageInput.vue';
</script>
<style scoped>
.chat-view { display: flex; flex-direction: column; height: 100vh; }
</style>

import { defineStore } from 'pinia';

export const useConversationStore = defineStore('conversation', {
  state: () => ({
    conversations: [] as any[],
    currentId: '',
  }),
  actions: {
    setConversations(list: any[]) {
      this.conversations = list;
    },
    setCurrentId(id: string) {
      this.currentId = id;
    },
  },
});

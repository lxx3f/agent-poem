import { defineStore } from 'pinia';

export const useAgentStore = defineStore('agent', {
  state: () => ({
    agents: [] as any[],
    selected: null as any,
  }),
  actions: {
    setAgents(list: any[]) {
      this.agents = list;
    },
    setSelected(agent: any) {
      this.selected = agent;
    },
  },
});

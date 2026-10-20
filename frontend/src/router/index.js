import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({

  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/paciente/conta',
      name: 'geranciarContaDoPaciente',
      component: () => import('@/views/paciente/grenciarContaPaciente.vue'),
    },
    {
      path: '/profissional/conta',
      name: 'gerenciarContaDoProfissional',
      component: () => import('@/views/profissional/gerenciarContaProfissional.vue'),
    },
  ],
})

export default router
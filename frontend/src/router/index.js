import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({

  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/home/HomeView.vue'),
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/auth/ModalidadeView.vue'),
      meta: { modo: 'login' },
    },
    // Telas ainda não criadas: usam a página provisória "Em breve".
    ...['cadastro/paciente', 'cadastro/profissional', 'login/paciente', 'login/profissional', 'login/administrador'].map(
      (path) => ({ path: `/${path}`, name: path, component: () => import('@/views/EmBreve.vue') }),
    ),
    {
      path: '/busca',
      name: 'busca-profissionais',
      component: () => import('@/views/EmBreve.vue'),
    },
    {
      path: '/profissionais/:id',
      name: 'perfil-profissional',
      component: () => import('@/views/EmBreve.vue'),
    },
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
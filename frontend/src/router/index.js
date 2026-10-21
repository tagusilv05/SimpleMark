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
      path: '/administracao',
      children: [
        {
          path: 'usuarios',
          name: 'gestaoDeUsuarios',
          component: () => import('@/views/administracao/GestaoUsuarios.vue'),
        },
        {
          path: 'validacao-profissionais',
          name: 'validacaoDeProfissionais',
          component: () => import('@/views/administracao/ValidacaoProfissionais.vue'),
        },
      ],
    },
    {
      path: '/profissional',
      children: [
        {
          path: 'dashboard',
          name: 'dashboardDoProfissional',
          component: () => import('@/views/profissional/dashboardProfissional.vue'),
        },
        {
          path: 'conta',
          name: 'gerenciarContaDoProfissional',
          component: () => import('@/views/profissional/gerenciarContaProfissional.vue'),
          meta: { voltar: true },
        },
        {
          path: 'configuracao-agenda',
          name: 'configuracaoAgendaDoProfissional',
          component: () => import('@/views/profissional/configuraçãoAgendaProfissional.vue'),
          meta: { voltar: true },
        }
      ]
    },
  ],
})

export default router
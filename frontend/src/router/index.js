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
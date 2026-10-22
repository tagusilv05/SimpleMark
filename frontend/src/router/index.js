import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({

  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/home/HomeView.vue'),
    },
    // Escolha da modalidade de login (destino do botão "Entrar" da home)
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/auth/ModalidadeView.vue'),
    },
    // Login do paciente
    {
      path: '/login/paciente',
      name: 'login/paciente',
      component: () => import('@/views/paciente/LoginPacienteView.vue'),
   },
    // Login do profissional
    {
      path: '/login/profissional',
      name: 'login/profissional',
      component: () => import('@/views/profissional/LoginProfissionalView.vue'),
    },
    //Cadastro do paciente
    {
      path: '/cadastro/paciente',
      name: 'cadastro/paciente',
      component: () => import('@/views/paciente/CadastroPacienteView.vue'),
   },
   //sucesso cadastro do paciente
    {
     path: '/cadastro/paciente/sucesso',
     name: 'cadastro/paciente/sucesso',
    component: () => import('@/views/paciente/CadastroPacienteSucessoView.vue'),
   },
   //Recuperar senha do paciente
   {
    path: '/login/paciente/recuperarsenha',
    name: 'login/paciente/recuperarsenha',
    component: () => import('@/views/paciente/RecuperarSenhaView.vue'),
   },
   //Redefinir senha do paciente
   {
    path: '/login/paciente/redefinirsenha',
    name: 'login/paciente/redefinirsenha',
    component: () => import('@/views/paciente/RedefinirSenhaView.vue'),
   },
   //sucesso na redefinicao de senha do paciente
   {
    path: '/login/paciente/sucessoredefinirsenha',
    name: 'login/paciente/sucessoredefinirsenha',
    component: () => import('@/views/paciente/SenhaRedefinidaView.vue'),
   },
    // Telas ainda não criadas: usam a página provisória "Em breve".
    ...['cadastro', 'cadastro/profissional', 'login/administrador'].map(
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
        },
        {
          path: 'atendimento',
          name: 'chamadaDoAtendimento',
          component: () => import('@/views/profissional/chamadaAtendimento.vue'),
        },
        {
          path: 'atendimento/receita',
          name: 'receitaDoAtendimento',
          component: () => import('@/views/profissional/receitaMedica.vue'),
        },
        {
          path: 'atendimento/atestado',
          name: 'atestadoDoAtendimento',
          component: () => import('@/views/profissional/atestadoMedico.vue'),
        },
      ]
    },
    // Qualquer outra rota (links do header/rodapé ainda sem tela) cai na página "Em breve"
    { path: '/:pathMatch(.*)*', name: 'em-breve', component: () => import('@/views/EmBreve.vue') },
  ],
})

export default router
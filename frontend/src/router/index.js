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
    // Escolha da modalidade de cadastro (destino do botão "Cadastrar-se" da home)
    {
      path: '/cadastro',
      name: 'cadastro',
      component: () => import('@/views/auth/ModalidadeCadastroView.vue'),
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
    // Recuperar senha do profissional
    {
      path: '/login/profissional/recuperarsenha',
      name: 'login/profissional/recuperarsenha',
      component: () => import('@/views/profissional/RecuperarSenhaProfissionalView.vue'),
    },
    // Redefinir senha do profissional (código + nova senha)
    {
      path: '/login/profissional/redefinirsenha',
      name: 'login/profissional/redefinirsenha',
      component: () => import('@/views/profissional/RedefinirSenhaProfissionalView.vue'),
    },
    // Sucesso na redefinição de senha do profissional
    {
      path: '/login/profissional/sucessoredefinirsenha',
      name: 'login/profissional/sucessoredefinirsenha',
      component: () => import('@/views/profissional/SenhaRedefinidaProfissionalView.vue'),
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
    // Cadastro do profissional de saúde
    {
      path: '/cadastro/profissional',
      name: 'cadastro/profissional',
      component: () => import('@/views/profissional/CadastroProfissionalView.vue'),
    },
    // Sucesso do cadastro do profissional
    {
      path: '/cadastro/profissional/sucesso',
      name: 'cadastro/profissional/sucesso',
      component: () => import('@/views/profissional/CadastroProfissionalSucessoView.vue'),
    },
    //Login do Admin
    {
      path: '/login/administrador',
      name: 'login/administrador',
      component: () => import('@/views/administracao/LoginAdminView.vue'),
    },
    //Como Funciona 
    {
      path: '/como-funciona',
      name: 'como-funciona',
      component: () => import('@/views/home/ComoFuncionaView.vue'),
   },
    // Sobre Nós
    {
      path: '/sobre-nos',
      name: 'sobre-nos',
      component: () => import('@/views/home/SobreNosView.vue'),
    },
    // Ouvidoria
    {
      path: '/ouvidoria',
      name: 'ouvidoria',
      component: () => import('@/views/home/OuvidoriaView.vue'),
    },
    // Páginas institucionais (links do rodapé)
    {
      path: '/quem-somos',
      name: 'quem-somos',
      component: () => import('@/views/home/QuemSomosView.vue'),
    },
    {
      path: '/termos',
      name: 'termos',
      component: () => import('@/views/home/TermosCondicoesView.vue'),
    },
    {
      path: '/privacidade',
      name: 'privacidade',
      component: () => import('@/views/home/PoliticaPrivacidadeView.vue'),
    },
    {
      path: '/duvidas-frequentes',
      name: 'duvidas-frequentes',
      component: () => import('@/views/home/DuvidasFrequentesView.vue'),
    },
    // Agendamento de consulta (paciente) -> confirmação -> pagamento
    {
      path: '/agendamento',
      name: 'agendamento',
      component: () => import('@/views/paciente/AgendamentoView.vue'),
    },
    {
      path: '/agendamento/confirmacao/:idConsulta',
      name: 'confirmacaoAgendamento',
      component: () => import('@/views/paciente/ConfirmacaoAgendamentoView.vue'),
    },
    {
      path: '/pagamento',
      name: 'pagamento',
      component: () => import('@/views/pagamento/PagamentoView.vue'),
    },
    {
      path: '/pagamento/:idConsulta',
      name: 'pagamento-consulta',
      component: () => import('@/views/pagamento/PagamentoView.vue'),
    },
    {
      path: '/busca',
      name: 'busca-profissionais',
      component: () => import('@/views/EmBreve.vue'),
    },
    {
      path: '/profissionais/:id?/avaliacoes',
      name: 'avaliacoesDoProfissional',
      component: () => import('@/views/paciente/AvaliacoesProfissional.vue'),
      alias: ['/avaliacoes-profissional'],
    },
    {
      path: '/profissionais/:id?',
      name: 'perfil-profissional',
      component: () => import('@/views/paciente/PerfilProfissional.vue'),
    },

    
    // {
    //   path: '/paciente/conta',
    //   name: 'geranciarContaDoPaciente',
    //   component: () => import('@/views/paciente/grenciarContaPaciente.vue'),
    // },

    {
      path: '/paciente/conta',
      name: 'geranciarContaDoPaciente',
      component: () => import('@/views/shared/GerenciarConta.vue'),
      props: { role: 'paciente' },
    },
    {
      path: '/paciente',
      component: () => import('@/layouts/paciente/consultasAgendadasLayout.vue'),
      children: [
        {
          path: 'agendamentos',
          name: 'meusAgendamentos',
          component: () => import('@/views/paciente/consultasAgendadas.vue'),
          meta: { voltar: true },
        },
        {
          path: 'agendamentos/:id/avaliar',
          name: 'avaliarConsulta',
          component: () => import('@/views/paciente/avaliarConsulta.vue'),
          meta: { voltar: true },
        },
      ],
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
        // {
        //   path: 'conta',
        //   name: 'gerenciarContaDoProfissional',
        //   component: () => import('@/views/profissional/gerenciarContaProfissional.vue'),
        //   meta: { voltar: true },
        // },
        {
          path: 'conta',
          name: 'gerenciarContaDoProfissional',
          component: () => import('@/views/shared/GerenciarConta.vue'),
          props: { role: 'profissional' },
          meta: { voltar: true },
        },
        {
          path: 'configuracao-agenda',
          name: 'configuracaoAgendaDoProfissional',
          component: () => import('@/views/profissional/configuracaoAgendaProfissional.vue'),
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
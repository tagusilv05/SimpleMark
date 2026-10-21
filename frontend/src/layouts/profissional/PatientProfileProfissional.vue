<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import ProfileCard from '@/components/shared/ProfileCard.vue'
import SideMenu from '@/components/shared/SideMenu.vue'
import FormCardDadosPessoais from '@/components/shared/FormCardDadosPessoais.vue'
import FormCardEndereco from '@/components/shared/FormCardEndereco.vue'
import FormCardSeguranca from '@/components/shared/FormCardSeguranca.vue'
import FormCardExcluirConta from '@/components/shared/FormCardExcluirConta.vue'
import ProfessionalManagement from '@/components/profissional/ProfessionalManagement.vue'

const router = useRouter()

// Aba selecionada no menu lateral
const aba = ref('dados')

// Valores iniciais. A "key" é o nome do campo dentro do formulário.
const dados = ref({
  nome: 'Nome Paciente',
  cpf: '123.456.789-00',
  orgao: 'SSP / PI',
  nascimento: '14/06/1988',
  genero: 'Masculino',
  telefone: '(11) 98765-4321',
  email: 'nomepaciente@email.com',
})

const endereco = ref({
  cep: '01310-100',
  cidade: 'Piauí',
  logradouro: 'Rua Projetada',
  numero: '1000',
  bairro: 'Meu Bairro',
  complemento: 'Sem Informação',
})

function salvar(valores) {
  // TODO: enviar para a API
  console.log('Salvar dados:', valores)
}

function salvarEndereco(valores) {
  // TODO: enviar para a API
  console.log('Salvar endereço:', valores)
}

function salvarSenha({ atual, nova }) {
  // TODO: enviar para a API (nunca use console.log com senha em produção)
  console.log('Trocar senha: ok')
}

function buscarCep() {
  // TODO: abrir a página de busca de CEP dos Correios
  window.open('https://buscacepinter.correios.com.br/app/endereco/index.php', '_blank')
}

const profissional = ref({
  fotoUrl: '',
  verificado: true,
  apresentacao: 'Cardiologista com mais de 15 anos de experiência clínica, especializado em diagnóstico cardiovascular e telemedicina preventiva.',
  especialidades: [
    { id: 1, name: 'Cardiologia Clínica', registration: 'CRM 12345-SP', council: 'CREMESP', price: 'R$ 200,00' },
  ],
})

const especialidadesDisponiveis = ['Cardiologia', 'Dermatologia', 'Pediatria', 'Ortopedia']

function trocarFoto(file) {
  // TODO: enviar para a API. Por enquanto só mostra o preview.
  profissional.value.fotoUrl = URL.createObjectURL(file)
}

function salvarProfissional() {
  // TODO: enviar para a API
  console.log('Salvar profissional:', profissional.value)
}

function desativarConta() {
  // TODO: chamar a API para deixar a conta inativa
  console.log('Desativar conta')
}

function excluirConta() {
  // TODO: chamar a API para excluir a conta
  console.log('Excluir conta')
}
</script>

<template>
  <div class="flex flex-col gap-6">
    <!-- Lê o "dados" salvo: só muda depois de clicar em Salvar -->
    <ProfileCard
      :name="dados.nome"
      role="Paciente"
      :email="dados.email"
      :phone="dados.telefone"
      member-since="Fevereiro de 2026"
    />

    <div class="grid grid-cols-1 items-start gap-8 md:grid-cols-[16rem_1fr]">
      <SideMenu v-model="aba" role="profissional" />

      <FormCardDadosPessoais
        v-if="aba === 'dados'"
        v-model="dados"
        @submit="salvar"
        @back="router.back()"
      />

      <FormCardEndereco
        v-else-if="aba === 'endereco'"
        v-model="endereco"
        @submit="salvarEndereco"
        @hint="buscarCep"
      />

      <FormCardSeguranca v-else-if="aba === 'seguranca'" @submit="salvarSenha" />

      <FormCardExcluirConta
        v-else-if="aba === 'excluir'"
        @desativar="desativarConta"
        @excluir="excluirConta"
      />
      
      <ProfessionalManagement
        v-else-if="aba === 'perfil'"
        v-model:bio="profissional.apresentacao"
        v-model:specialties="profissional.especialidades"
        :photo="profissional.fotoUrl"
        :verified="profissional.verificado"
        :specialty-options="especialidadesDisponiveis"
        @photo-change="trocarFoto"
        @save="salvarProfissional"
      />

      <!-- Outras abas: ainda não criadas -->
      <section
        v-else
        class="rounded-xl bg-white p-8 text-gray-500 shadow-[0_2px_12px_rgba(11,47,91,0.08)]"
      >
        <!-- Mostra a chave da aba clicada: use-a no v-else-if do painel acima -->
        Em breve. (aba: {{ aba }})
      </section>
    </div>
  </div>
</template>
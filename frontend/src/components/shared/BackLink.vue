<script setup>
/**
 * BackLink — botão "← Voltar"
 *
 * COMO USAR (na página):
 *
 *   import BackLink from '@/components/shared/BackLink.vue'
 *
 *   <BackLink />                          // volta para a página anterior
 *   <BackLink label="Início" to="/" />    // vai para uma rota específica
 *   <BackLink to="/minha-conta" />        // texto padrão "Voltar", rota fixa
 *   <BackLink :to="{ name: 'home' }" />   // também aceita objeto de rota
 *
 * PROPS
 *   label  String  (padrão: 'Voltar')
 *            texto exibido ao lado da seta.
 *   to     String | Object  (padrão: null)
 *            - sem valor  -> router.back() (volta no histórico do navegador)
 *            - com valor  -> router.push(to). Aceita caminho ('/login')
 *                            ou objeto de rota ({ name: 'home' }).
 *            Atenção: sem `to`, se o usuário abriu a página direto (sem histórico),
 *            "voltar" pode sair do site. Nesse caso, passe um `to`.
 *
 * EVENTOS
 *   Nenhum. A navegação já é feita dentro do componente.
 *
 * ESTILO
 *   Já vem com Tailwind (texto azul, hover com transparência, recuo pl-8 pt-2).
 *   Para ajustar o espaçamento, edite as classes do botão no template abaixo.
 *
 * DEPENDÊNCIAS
 *   - vue-router
 *   - Tailwind CSS
 */

import { useRouter } from 'vue-router'

const props = defineProps({
  label: { type: String, default: 'Voltar' },
  // Se informado, vai para essa rota. Se não, volta para a página anterior.
  to: { type: [String, Object], default: null },
})

const router = useRouter()

function goBack() {
  if (props.to) router.push(props.to)
  else router.back()
}
</script>

<template>
  <button
    type="button"
    class="inline-flex cursor-pointer items-center gap-2 text-sm font-semibold text-[#0b2f5b] transition-opacity hover:opacity-70 pl-8 pt-2"
    @click="goBack"
  >
    <svg
      class="size-4"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      stroke-width="2.5"
      stroke="currentColor"
      aria-hidden="true"
    >
      <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 19.5 3 12m0 0 7.5-7.5M3 12h18" />
    </svg>
    <span>{{ label }}</span>
  </button>
</template>

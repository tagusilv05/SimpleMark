"""Regras da avaliação do profissional pelo paciente, após a consulta."""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from core.excecoes import ErroNegocio
from core.tempo import agora_utc
from models.models import Avaliacao, Paciente
from repositories.avaliacao import RepositorioAvaliacao
from schemas.avaliacao import (
    AvaliacaoEntrada,
    ProfissionalMelhorAvaliadoResposta,
    ResumoAvaliacoesResposta,
)

# Status da consulta que libera a avaliação. Ajuste aqui se o grupo usar outro valor.
STATUS_CONSULTA_REALIZADA = "realizada"

# Peso da média geral no ranking: com poucas avaliações, a nota do profissional
# "puxa" para a média da plataforma. Assim, uma única nota 5 não supera 4,9 em 200.
MINIMO_AVALIACOES_CONFIANCA = 5


class ServicoAvaliacao:
    """O paciente avalia uma única vez cada consulta realizada.

    A nota é opcional: 1 a 5 estrelas ou nenhuma. A média por especialidade
    do profissional (profissional_especialidade.avaliacao) é atualizada na
    mesma transação.
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self.avaliacoes = RepositorioAvaliacao(db)

    def avaliar(self, paciente: Paciente, id_consulta: int, dados: AvaliacaoEntrada) -> Avaliacao:
        consulta = self.avaliacoes.buscar_consulta(id_consulta)
        # Consulta de outro paciente responde 404, para não revelar que ela existe.
        if consulta is None or consulta.id_paciente != paciente.id_paciente:
            raise ErroNegocio("Não encontramos esta consulta.", 404)
        if consulta.status != STATUS_CONSULTA_REALIZADA:
            raise ErroNegocio("Você só pode avaliar uma consulta depois de ela ser realizada.", 409)
        if self.avaliacoes.buscar_por_consulta(id_consulta) is not None:
            raise ErroNegocio("Você já avaliou esta consulta.", 409)

        agora = agora_utc()
        avaliacao = self.avaliacoes.adicionar(
            Avaliacao(
                id_consulta=id_consulta,
                nota=dados.nota,
                feedback=dados.feedback,
                data=agora.date(),
                hora=agora.time().replace(microsecond=0),
            )
        )
        try:
            self.db.flush()
            if dados.nota is not None:
                self._atualizar_media(consulta.id_esp_prof)
            self.db.commit()
        except IntegrityError as exc:
            # Duas requisições ao mesmo tempo: a chave primária barra a segunda.
            self.db.rollback()
            raise ErroNegocio("Você já avaliou esta consulta.", 409) from exc
        return avaliacao

    def minha_avaliacao(self, paciente: Paciente, id_consulta: int) -> Avaliacao:
        consulta = self.avaliacoes.buscar_consulta(id_consulta)
        if consulta is None or consulta.id_paciente != paciente.id_paciente:
            raise ErroNegocio("Não encontramos esta consulta.", 404)
        avaliacao = self.avaliacoes.buscar_por_consulta(id_consulta)
        if avaliacao is None:
            raise ErroNegocio("Esta consulta ainda não foi avaliada.", 404)
        return avaliacao

    def resumo_do_profissional(self, id_profissional: int) -> ResumoAvaliacoesResposta:
        if self.avaliacoes.buscar_profissional(id_profissional) is None:
            raise ErroNegocio("Não encontramos este profissional de saúde.", 404)
        contagem = self.avaliacoes.contar_notas_do_profissional(id_profissional)
        distribuicao = {estrelas: contagem.get(estrelas, 0) for estrelas in range(1, 6)}
        total = sum(distribuicao.values())
        soma = sum(estrelas * quantidade for estrelas, quantidade in distribuicao.items())
        return ResumoAvaliacoesResposta(
            id_profissional=id_profissional,
            media=round(soma / total, 2) if total else None,
            total_avaliacoes=total,
            distribuicao=distribuicao,
        )

    def ranking(self, id_especialidade: int | None, limite: int) -> list[ProfissionalMelhorAvaliadoResposta]:
        """Profissionais ativos ordenados pela média ponderada (bayesiana) das estrelas."""
        linhas = self.avaliacoes.agregar_por_profissional(id_especialidade)
        if not linhas:
            return []
        total_geral = sum(total for _, _, _, total in linhas)
        media_geral = sum(media * total for _, _, media, total in linhas) / total_geral
        m = MINIMO_AVALIACOES_CONFIANCA

        def pontuacao(media: float, total: int) -> float:
            return (total / (total + m)) * media + (m / (total + m)) * media_geral

        ordenadas = sorted(
            linhas,
            key=lambda linha: (-pontuacao(linha[2], linha[3]), -linha[3], linha[1]),
        )[:limite]
        especialidades = self.avaliacoes.nomes_especialidades([linha[0] for linha in ordenadas])
        return [
            ProfissionalMelhorAvaliadoResposta(
                posicao=posicao,
                id_profissional=id_prof,
                nome=nome,
                especialidades=especialidades.get(id_prof, []),
                media=round(media, 2),
                total_avaliacoes=total,
                pontuacao=round(pontuacao(media, total), 2),
            )
            for posicao, (id_prof, nome, media, total) in enumerate(ordenadas, start=1)
        ]

    def _atualizar_media(self, id_esp_prof: int) -> None:
        vinculo = self.avaliacoes.buscar_vinculo_para_atualizar(id_esp_prof)
        if vinculo is None:
            return
        media = self.avaliacoes.media_do_vinculo(id_esp_prof)
        vinculo.avaliacao = None if media is None else round(media, 2)

# Busca de profissionais de saúde por especialidade, data, horário livre e
# valor da consulta.
#
# Rota aberta: o paciente precisa comparar preço e agenda antes de decidir se
# cria conta. Nada aqui expõe dado de outro paciente — só o que o profissional
# publica para ser encontrado.
#
# A unidade da resposta é o vínculo profissional+especialidade: o mesmo médico
# pode cobrar um valor em Cardiologia e outro em Clínica Geral, com agendas
# separadas, então cada vínculo vira uma ficha na lista.
from datetime import datetime

from sqlalchemy.orm import Session

from core.excecoes import ErroNegocio
from core.tempo import agora_local
from models.models import DataHorario, ProfissionalEspecialidade
from repositories.busca_profissional import buscar_horarios_disponiveis
from schemas.busca_profissional import (
    FiltroBuscaProfissional,
    HorarioDisponivelOutput,
    OrdenacaoBusca,
    ProfissionalBuscaOutput,
)


def _validar(filtro: FiltroBuscaProfissional) -> None:
    """Recusa intervalo invertido, que nunca devolveria resultado."""
    if filtro.data_inicio and filtro.data_fim and filtro.data_inicio > filtro.data_fim:
        raise ErroNegocio("A data inicial não pode ser posterior à data final.", 400)

    if filtro.hora_inicio and filtro.hora_fim and filtro.hora_inicio >= filtro.hora_fim:
        raise ErroNegocio("O horário inicial deve ser anterior ao horário final.", 400)

    if (
        filtro.valor_min is not None
        and filtro.valor_max is not None
        and filtro.valor_min > filtro.valor_max
    ):
        raise ErroNegocio("O valor mínimo não pode ser maior que o valor máximo.", 400)


def _normalizar(filtro: FiltroBuscaProfissional, momento: datetime) -> FiltroBuscaProfissional:
    """Puxa a data inicial para hoje. Agenda que já passou não é vaga."""
    hoje = momento.date()
    if filtro.data_inicio is None or filtro.data_inicio < hoje:
        return filtro.model_copy(update={"data_inicio": hoje})
    return filtro


def _descrever_conselho(conselho) -> str | None:
    if conselho is None:
        return None
    return f"{conselho.orgao_conselho} {conselho.numero_conselho}"


def _ficha(vinculo: ProfissionalEspecialidade) -> ProfissionalBuscaOutput:
    profissional = vinculo.profissional
    return ProfissionalBuscaOutput(
        id_esp_prof=vinculo.id_esp_prof,
        id_profissional=profissional.id_profissional,
        nome=profissional.usuario.nome,
        especialidade=vinculo.especialidade.especialidade,
        valor_consulta=vinculo.valor_consulta,
        avaliacao=vinculo.avaliacao,
        conselho=_descrever_conselho(vinculo.conselho),
        info_profissional=profissional.info_profissional,
        path_imagem=profissional.path_imagem,
        horarios_disponiveis=[],
    )


def _agrupar_por_vinculo(horarios: list[DataHorario]) -> list[ProfissionalBuscaOutput]:
    """Transforma as linhas de agenda em uma ficha por profissional.

    O repositório devolve um horário por linha, com o profissional repetido.
    O dicionário preserva a ordem de chegada, que já veio ordenada por nome.
    """
    fichas: dict[int, ProfissionalBuscaOutput] = {}
    for horario in horarios:
        vinculo = horario.profissional_especialidade
        ficha = fichas.get(vinculo.id_esp_prof)
        if ficha is None:
            ficha = _ficha(vinculo)
            fichas[vinculo.id_esp_prof] = ficha
        ficha.horarios_disponiveis.append(
            HorarioDisponivelOutput(
                id_horario=horario.id_horario,
                data_consulta=horario.data_consulta,
                hora_inicio=horario.hora_inicio,
                hora_fim=horario.hora_fim,
            )
        )
    return list(fichas.values())


def _chave_valor(ficha: ProfissionalBuscaOutput):
    return (ficha.valor_consulta, ficha.nome.casefold())


def _chave_avaliacao(ficha: ProfissionalBuscaOutput):
    # Maior nota primeiro; quem ainda não foi avaliado fica no fim da lista.
    return (ficha.avaliacao is None, -(ficha.avaliacao or 0.0), ficha.nome.casefold())


_CHAVES = {
    OrdenacaoBusca.NOME: lambda ficha: ficha.nome.casefold(),
    OrdenacaoBusca.VALOR: _chave_valor,
    OrdenacaoBusca.AVALIACAO: _chave_avaliacao,
}


def buscar_profissionais(
    db: Session,
    filtro: FiltroBuscaProfissional,
) -> list[ProfissionalBuscaOutput]:
    """Profissionais que atendem ao filtro, cada um com os horários que sobraram.

    Quem não tem horário livre no período não entra na lista: a busca existe
    para agendar, e ficha sem agenda não leva o paciente a lugar nenhum.
    """
    _validar(filtro)

    momento = agora_local()
    horarios = buscar_horarios_disponiveis(db, _normalizar(filtro, momento), momento)

    fichas = _agrupar_por_vinculo(horarios)
    return sorted(fichas, key=_CHAVES[filtro.ordenar_por])

"""Busca pública de profissionais por especialidade, data, horário e valor."""

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
    """Recusa intervalo invertido, que nunca devolveria resultado.

    Args:
        filtro (FiltroBuscaProfissional): Filtros informados na busca.

    Raises:
        ErroNegocio: 400 se a data inicial for posterior à final, se o horário
            inicial não for anterior ao final ou se o valor mínimo for maior que
            o máximo.
    """
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
    """Puxa a data inicial para hoje. Agenda que já passou não é vaga.

    Args:
        filtro (FiltroBuscaProfissional): Filtros informados na busca.
        momento (datetime): Momento atual de referência.

    Returns:
        FiltroBuscaProfissional: Cópia do filtro com ``data_inicio`` ajustada
        para hoje, ou o próprio filtro se já for hoje ou depois.
    """
    hoje = momento.date()
    if filtro.data_inicio is None or filtro.data_inicio < hoje:
        return filtro.model_copy(update={"data_inicio": hoje})
    return filtro


def _descrever_conselho(conselho) -> str | None:
    """Conselho no formato "ÓRGÃO NÚMERO", ou None se não houver.

    Args:
        conselho: Registro do conselho profissional, ou None.

    Returns:
        str | None: Órgão e número do conselho, ou None.
    """
    if conselho is None:
        return None
    return f"{conselho.orgao_conselho} {conselho.numero_conselho}"


def _ficha(vinculo: ProfissionalEspecialidade) -> ProfissionalBuscaOutput:
    """Ficha do vínculo profissional+especialidade, ainda sem horários.

    Args:
        vinculo (ProfissionalEspecialidade): Vínculo do profissional com a
            especialidade.

    Returns:
        ProfissionalBuscaOutput: Ficha com a lista de horários vazia.
    """
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

    Args:
        horarios (list[DataHorario]): Horários livres devolvidos pelo repositório.

    Returns:
        list[ProfissionalBuscaOutput]: Uma ficha por vínculo, com seus horários.
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
    """Ordena pelo menor valor da consulta e, no empate, pelo nome.

    Args:
        ficha (ProfissionalBuscaOutput): Ficha a ordenar.

    Returns:
        tuple: Chave de ordenação (valor da consulta, nome normalizado).
    """
    return (ficha.valor_consulta, ficha.nome.casefold())


def _chave_avaliacao(ficha: ProfissionalBuscaOutput):
    """Ordena pela maior avaliação, com os não avaliados no fim.

    Args:
        ficha (ProfissionalBuscaOutput): Ficha a ordenar.

    Returns:
        tuple: Chave de ordenação (sem avaliação, nota negativa, nome normalizado).
    """
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

    Args:
        db (Session): Sessão do banco de dados.
        filtro (FiltroBuscaProfissional): Especialidade, período, horário, faixa
            de valor e ordenação desejados.

    Returns:
        list[ProfissionalBuscaOutput]: Fichas com horários livres, na ordenação
        pedida.
    """
    _validar(filtro)

    momento = agora_local()
    horarios = buscar_horarios_disponiveis(db, _normalizar(filtro, momento), momento)

    fichas = _agrupar_por_vinculo(horarios)
    return sorted(fichas, key=_CHAVES[filtro.ordenar_por])

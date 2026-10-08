from typing import Optional, Tuple

from sqlalchemy.orm import Session

from models.models import Avaliacao, Consulta, ProfissionalEspecialidade

from sqlalchemy import func, select

from models.models import (
    Avaliacao,
    Consulta,
    Especialidade,
    Profissional,
    ProfissionalEspecialidade,
    Usuario,
)


def buscar_consulta(db: Session, id_consulta: int) -> Optional[Consulta]:
    return (
        db.query(Consulta)
        .filter(Consulta.id_consulta == id_consulta)
        .first()
    )


def buscar_avaliacao(db: Session, id_consulta: int) -> Optional[Avaliacao]:
    return (
        db.query(Avaliacao)
        .filter(Avaliacao.id_consulta == id_consulta)
        .first()
    )


def criar_avaliacao(db: Session, avaliacao: Avaliacao) -> Avaliacao:
    db.add(avaliacao)
    db.commit()
    db.refresh(avaliacao)
    return avaliacao


def calcular_media_profissional(
    db: Session, id_profissional: int
) -> Tuple[Optional[float], int]:
    media, total = (
        db.query(func.avg(Avaliacao.avaliacao), func.count(Avaliacao.id_consulta))
        .join(Consulta, Consulta.id_consulta == Avaliacao.id_consulta)
        .join(
            ProfissionalEspecialidade,
            ProfissionalEspecialidade.id_esp_prof == Consulta.id_esp_prof,
        )
        .filter(ProfissionalEspecialidade.id_profissional == id_profissional)
        .one()
    )
    return (round(float(media), 2) if media is not None else None), total


class RepositorioAvaliacao:
    """Consultas de avaliacao. Não aplica regra de negócio."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def buscar_consulta(self, id_consulta: int) -> Consulta | None:
        return self.db.get(Consulta, id_consulta)

    def buscar_por_consulta(self, id_consulta: int) -> Avaliacao | None:
        return self.db.get(Avaliacao, id_consulta)

    def adicionar(self, avaliacao: Avaliacao) -> Avaliacao:
        self.db.add(avaliacao)
        return avaliacao

    def buscar_profissional(self, id_profissional: int) -> Profissional | None:
        return self.db.get(Profissional, id_profissional)

    def buscar_vinculo_para_atualizar(self, id_esp_prof: int) -> ProfissionalEspecialidade | None:
        """Trava a linha para duas avaliações simultâneas não gravarem médias antigas."""
        comando = (
            select(ProfissionalEspecialidade)
            .where(ProfissionalEspecialidade.id_esp_prof == id_esp_prof)
            .with_for_update()
        )
        return self.db.scalar(comando)

    def media_do_vinculo(self, id_esp_prof: int) -> float | None:
        comando = (
            select(func.avg(Avaliacao.nota))
            .join(Consulta, Consulta.id_consulta == Avaliacao.id_consulta)
            .where(Consulta.id_esp_prof == id_esp_prof, Avaliacao.nota.is_not(None))
        )
        media = self.db.scalar(comando)
        return None if media is None else float(media)

    def contar_notas_do_profissional(self, id_profissional: int) -> dict[int, int]:
        """Quantidade de avaliações por nota (1 a 5), somando todas as especialidades."""
        comando = (
            select(Avaliacao.nota, func.count())
            .join(Consulta, Consulta.id_consulta == Avaliacao.id_consulta)
            .join(ProfissionalEspecialidade, ProfissionalEspecialidade.id_esp_prof == Consulta.id_esp_prof)
            .where(
                ProfissionalEspecialidade.id_profissional == id_profissional,
                Avaliacao.nota.is_not(None),
            )
            .group_by(Avaliacao.nota)
        )
        return {int(nota): int(total) for nota, total in self.db.execute(comando)}

    def agregar_por_profissional(self, id_especialidade: int | None = None) -> list[tuple[int, str, float, int]]:
        """(id_profissional, nome, média, total) dos profissionais ativos com ao menos uma nota."""
        comando = (
            select(
                Profissional.id_profissional,
                Usuario.nome,
                func.avg(Avaliacao.nota),
                func.count(Avaliacao.nota),
            )
            .join(Usuario, Usuario.id == Profissional.id_usuario)
            .join(ProfissionalEspecialidade, ProfissionalEspecialidade.id_profissional == Profissional.id_profissional)
            .join(Consulta, Consulta.id_esp_prof == ProfissionalEspecialidade.id_esp_prof)
            .join(Avaliacao, Avaliacao.id_consulta == Consulta.id_consulta)
            .where(Usuario.status.is_(True), Avaliacao.nota.is_not(None))
            .group_by(Profissional.id_profissional, Usuario.nome)
        )
        if id_especialidade is not None:
            comando = comando.where(ProfissionalEspecialidade.id_especialidade == id_especialidade)
        return [
            (int(id_prof), nome, float(media), int(total))
            for id_prof, nome, media, total in self.db.execute(comando)
        ]

    def nomes_especialidades(self, ids_profissionais: list[int]) -> dict[int, list[str]]:
        if not ids_profissionais:
            return {}
        comando = (
            select(ProfissionalEspecialidade.id_profissional, Especialidade.especialidade)
            .join(Especialidade, Especialidade.id_especialidade == ProfissionalEspecialidade.id_especialidade)
            .where(ProfissionalEspecialidade.id_profissional.in_(ids_profissionais))
            .order_by(Especialidade.especialidade)
        )
        nomes: dict[int, list[str]] = {}
        for id_prof, nome in self.db.execute(comando):
            nomes.setdefault(int(id_prof), []).append(nome)
        return nomes

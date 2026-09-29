# Define os modelos do banco de dados utilizando SQLAlchemy,
# incluindo as tabelas, campos, chaves estrangeiras e relacionamentos entre elas.
from sqlalchemy import (
    Column,
    Boolean,
    Date,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    Time,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from database.connection import Base
import uuid

class Usuario(Base):
    __tablename__ = "usuario"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String(150), nullable=False)
    cpf = Column(String(14), unique=True, nullable=False)
    orgao_emissor = Column(String(50), nullable=False)
    data_nascimento = Column(Date, nullable=False)
    genero = Column(String(30), nullable=False)
    telefone = Column(String(20), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    status = Column(Boolean, nullable=False, default=True)

    paciente = relationship("Paciente", back_populates="usuario", uselist=False)
    administrador = relationship("Administrador", back_populates="usuario", uselist=False)
    profissional = relationship("Profissional", back_populates="usuario", uselist=False)


class Paciente(Base):
    __tablename__ = "paciente"

    id_paciente = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(UUID(as_uuid=True), ForeignKey("usuario.id"), unique=True, nullable=False)

    usuario = relationship("Usuario", back_populates="paciente")
    consultas = relationship("Consulta", back_populates="paciente")


class Administrador(Base):
    __tablename__ = "administrador"

    id_administrador = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(UUID(as_uuid=True), ForeignKey("usuario.id"), unique=True, nullable=False)

    usuario = relationship("Usuario", back_populates="administrador")


class Profissional(Base):
    __tablename__ = "profissional"

    id_profissional = Column(Integer, primary_key=True, index=True)
    path_imagem = Column(String(255), nullable=True)
    id_usuario = Column(UUID(as_uuid=True), ForeignKey("usuario.id"), unique=True, nullable=False)
    info_profissional = Column(Text, nullable=True)

    usuario = relationship("Usuario", back_populates="profissional")
    especialidades = relationship("ProfissionalEspecialidade", back_populates="profissional")


class InfoConselho(Base):
    __tablename__ = "info_conselho"

    id_conselho = Column(Integer, primary_key=True, index=True)
    numero_conselho = Column(String(30), nullable=False)
    orgao_conselho = Column(String(30), nullable=False)

    profissionais_especialidades = relationship("ProfissionalEspecialidade", back_populates="conselho")


class Especialidade(Base):
    __tablename__ = "especialidade"

    id_especialidade = Column(Integer, primary_key=True, index=True)
    especialidade = Column(String(100), unique=True, nullable=False)

    profissionais = relationship("ProfissionalEspecialidade", back_populates="especialidade")


class ProfissionalEspecialidade(Base):
    __tablename__ = "profissional_especialidade"

    id_esp_prof = Column(Integer, primary_key=True, index=True)
    id_especialidade = Column(Integer, ForeignKey("especialidade.id_especialidade"),nullable=False)
    id_profissional = Column(Integer, ForeignKey("profissional.id_profissional"), nullable=False)
    id_conselho = Column(Integer, ForeignKey("info_conselho.id_conselho"), nullable=True)
    valor_consulta = Column(Float, nullable=False, default=0.0)
    avaliacao = Column(Float, nullable=True)

    profissional = relationship( "Profissional", back_populates="especialidades")
    especialidade = relationship("Especialidade", back_populates="profissionais")
    conselho = relationship("InfoConselho", back_populates="profissionais_especialidades")
    horarios = relationship("DataHorario", back_populates="profissional_especialidade")
    consultas = relationship("Consulta", back_populates="profissional_especialidade")


class DataHorario(Base):
    __tablename__ = "data_horario"

    id_horario = Column(Integer, primary_key=True, index=True)
    id_esp_prof = Column(Integer, ForeignKey("profissional_especialidade.id_esp_prof"), nullable=False)
    data_consulta = Column(Date, nullable=False)
    hora_inicio = Column(Time, nullable=False)
    hora_fim = Column(Time, nullable=False)
    ocupado = Column( Boolean, nullable=False, default=False)

    profissional_especialidade = relationship("ProfissionalEspecialidade", back_populates="horarios")


class Consulta(Base):
    __tablename__ = "consulta"

    id_consulta = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(UUID(as_uuid=True), ForeignKey("usuario.id"), nullable=False)
    id_esp_prof = Column(Integer, ForeignKey("profissional_especialidade.id_esp_prof"), nullable=False)
    data = Column(Date, nullable=False)
    hora = Column(Time, nullable=False)
    tipo = Column(String(30), nullable=False)
    status = Column(String(30), nullable=False, default="agendada")
    valor = Column(Numeric(10, 2), nullable=False)

    paciente = relationship("Paciente", back_populates="consultas")
    profissional_especialidade = relationship("ProfissionalEspecialidade", back_populates="consultas")
    avaliacao = relationship("Avaliacao", back_populates="consulta", uselist=False)
    pagamento = relationship("Pagamento", back_populates="consulta", uselist=False)
    documentos = relationship("DocumentoClinico", back_populates="consulta")


class Avaliacao(Base):
    __tablename__ = "avaliacao"

    id_consulta = Column(Integer, ForeignKey("consulta.id_consulta"), primary_key=True)
    feedback = Column(Text, nullable=True)
    data = Column(Date, nullable=False)
    hora = Column(Time, nullable=False)

    consulta = relationship("Consulta", back_populates="avaliacao")


class Pagamento(Base):
    __tablename__ = "pagamento"

    id_consulta = Column(Integer, ForeignKey("consulta.id_consulta"), primary_key=True)
    status = Column(String(30), nullable=False, default="pendente")
    data = Column(Date, nullable=False)
    hora = Column(Time, nullable=False)

    consulta = relationship("Consulta", back_populates="pagamento")


class DocumentoClinico(Base):
    __tablename__ = "documento_clinico"

    id_documento = Column(Integer, primary_key=True, index=True)
    id_consulta = Column(Integer, ForeignKey("consulta.id_consulta"), nullable=False)
    observacoes = Column(Text, nullable=True)
    tipo = Column(Boolean, nullable=False)

    consulta = relationship("Consulta", back_populates="documentos")
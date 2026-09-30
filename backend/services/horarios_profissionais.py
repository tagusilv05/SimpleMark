from models.models import DataHorario, ProfissionalEspecialidade
from repositories import horarios_profissional as horario_repository

def listar_horarios(db, id_esp_prof: int, data):
    """
    Busca os horarios de um profissional com base no vinculo com a especialidade
    
    Args:
        db: Sessão do banco de dados
        id_esp_prof (int): ID do vínculo entre profissional e especialidade
        data (date): Data para filtrar os horarios
        
    Returns:
        List[DataHorario]: Lista de horarios encontrados
    
    """
    
    return horario_repository.listar(
        db,
        id_esp_prof=id_esp_prof,
        data_consulta=data
    )

def criar_horarios_em_lote(db, dados_lote):
    
    """
    Cadastro os novos horarios de um profissional
    
    Args:
        db: Sessão do banco de dados
        dados_lote (HorariosEmLoteCreate): Dados contendo o ID do vínculo entre profissional e especialidade, 
                                           as datas e os horarios a serem cadastrados.
    
    Returns:
        dict: Mensagem de sucesso ou erro
    """
    
    try:
        vinculo_existe = db.query(ProfissionalEspecialidade).filter(
            ProfissionalEspecialidade.id_esp_prof == dados_lote.id_esp_prof
        ).first()

        if not vinculo_existe:
            raise LookupError("Vínculo entre profissional e especialidade não encontrado.")

        for data_consulta in dados_lote.datas:
            for item in dados_lote.lista_horarios:
                if not horario_repository.existe_horario(
                    db,
                    dados_lote.id_esp_prof,
                    data_consulta,
                    item.hora_inicio,
                ):
                    horario_repository.criar(
                        db,
                        DataHorario(
                            id_esp_prof=dados_lote.id_esp_prof,
                            data_consulta=data_consulta,
                            hora_inicio=item.hora_inicio,
                            hora_fim=item.hora_fim,
                            ocupado=False
                        ),
                    )

        db.commit()
        return {"status": "success", "message": "Horarios processados com sucesso!"}

    except Exception:
        db.rollback()
        raise

def deletar_horario(db, id_horario: int):
    
    """
    Deleta um horario específico com base no ID fornecido.
    
    Args:
        db: Sessão do banco de dados
        id_horario (int): ID do horario a ser deletado.
        
    Returns:
        dict: Mensagem de sucesso ou None se o horario não for encontrado.
    """
    
    
    horario = horario_repository.buscar_por_id(db, id_horario)
    if not horario:
        return None
    horario_repository.deletar(db, horario)
    db.commit()
    return {"msg": "Horario removido"}

def atualizar_horario(db, id_horario: int, dados_atualizacao):
    
    """
    Atualiza um horario específico com base no ID fornecido.
    
    Args:
        db: Sessão do banco de dados
        id_horario (int): ID do horario a ser atualizado.
        dados_atualizacao: Dados contendo os novos horarios.
        
    Returns:
        dict: Mensagem de sucesso ou None se o horario não for encontrado.
    """
    
    
    horario = horario_repository.atualizar_por_id(db, id_horario=id_horario, novo_inicio=dados_atualizacao.hora_inicio, novo_fim=dados_atualizacao.hora_fim)
    if not horario:
        return None
    db.commit()
    db.refresh(horario)
    return horario
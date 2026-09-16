from ..models import *
from..connection import init_db

def filter_ia(phone:str) -> IA:
    db = init_db()

    if not db:
        raise(Exception("Não consegui conectar com databse"))
    
    try:
        ia = db.query(IA).filter(IA.phone_number == phone).first()
        if not ia:
            print(f"Nenhuma IA cadastrada com esse numero de telefone {phone}")
            return None
        
        # Adicionar as Fks
        ia.ia_config
        ia.active_prompt

        print(f"IA Localizada: {ia.name} - {ia.phone_number}")
        return ia
    
    except Exception as ex:
        print(f"Error : {ex}")

    finally:
        if db:
            db.close()

    return None


def filter_ia_by_id(ia_id: int) -> IA:
    db = init_db()

    if not db:
        raise Exception("Nao consegui conectar com database")

    try:
        ia = db.query(IA).filter(IA.id == ia_id).first()
        if not ia:
            print(f"Nenhuma IA cadastrada com esse ID {ia_id}")
            return None

        # Carrega os relacionamentos antes de fechar a sessao.
        ia.ia_config
        ia.active_prompt

        print(f"IA localizada por ID: {ia.name} - {ia.id}")
        return ia

    except Exception as ex:
        print(f"Error : {ex}")

    finally:
        if db:
            db.close()

    return None

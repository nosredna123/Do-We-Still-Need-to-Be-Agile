from app.routes_back.habilcompDB_routes import getCompetenciaByID, getHabilidadeByID

def teste_getCompetenciaByID(id_comp = 1, id_habil = 1):
    return getCompetenciaByID(id_comp, id_habil)

def teste_getHabilidadeByID(id = 1):
    return getHabilidadeByID(id)


if __name__ == "__main__":
    id_habil, id_comp = 1, 1

    print("Habilidade: ", getHabilidadeByID(id_habil))
    print("Competencia: ", getCompetenciaByID(id_comp, id_habil))
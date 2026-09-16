from app.routes_back.questionDB_routes import getQuestionByID, getUnsolvedQuestion


def teste_getQuestionByID(id = 1):
    questao = getQuestionByID(id)
    print(questao)


# Testar

if __name__ == "__main__":
    user_id, habil, competencia = 1, 1, 1 
    print(getUnsolvedQuestion(user_id, habil, competencia))


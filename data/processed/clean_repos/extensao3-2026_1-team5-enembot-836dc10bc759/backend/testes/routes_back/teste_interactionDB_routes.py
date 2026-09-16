from app.routes_back.interactionDB_routes import getInteractionsByUser, createInteraction

def teste_getInteractionsByUser(user_id = 1):
    return getInteractionsByUser(user_id)

def teste_createInteraction(
    interaction: dict = {
        'user_id': 1,
        'question_id': 1,
        'tempo_gasto': 100,
        'resposta_user': 'resposta',
        'acertou': False,
        'n_dicas': 3

    }
):
    return createInteraction(**interaction)

if __name__ == "__main__":
    print(teste_getInteractionsByUser())
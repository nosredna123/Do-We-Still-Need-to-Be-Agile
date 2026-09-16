from app.routes_back.chatmessageDB_routes import createChatMessage, getChatsMessagesByChat, updateChatMessage, deleteChatMessage
from app.schemas.chatmessage import ChatMessageSchema

def teste_getChatMessagesByChat(chat_id):
    print(f"Mensagens do chat {chat_id}\n")
    print(getChatsMessagesByChat(chat_id))

    return getChatsMessagesByChat(chat_id)

def teste_createChatMessage():

    question = """
    Um banho propicia ao indivíduo um momento de conforto e reenergização. Porém, o desperdício de água gera prejuízo para todos. Considere que cada uma das cinco pessoas de uma família toma dois banhos por dia, de 15 minutos cada. Sabe-se que a cada hora de banho são gastos aproximadamente 540 litros de água. Considerando que um mês tem 30 dias, podemos perceber que o consumo de água é bem significativo. A quantidade total de litros de água consumida, nos banhos dessa família, durante um mês, é mais próxima de:
    A) 1 350.
    B) 2 700.
    C) 20 250.
    D) 20 520.
    E) 40 500. 
    """

    chat_message = {
        "chat_id": 5,
        "author": 'llm',
        "texto": question,
        "question_id": 2,
    }

    return createChatMessage(**chat_message)

def teste_updateChatMessage(chat_id):
    chat_message_schema = teste_getChatMessagesByChat(chat_id)[-1]
    chat_message_schema.texto = 'mensagem3_atualizada'
    updated_schema = updateChatMessage(chat_message_schema)

    teste_getChatMessagesByChat(chat_id)

    return updated_schema

def teste_deleteChatMessage(chat_id):
    print(deleteChatMessage(chat_id))
    teste_getChatMessagesByChat(chat_id)



if __name__ == "__main__":
    chat_id = 4

    teste_createChatMessage()
    
    # chat_message_schema.texto = 'mensagem3_atualizada'
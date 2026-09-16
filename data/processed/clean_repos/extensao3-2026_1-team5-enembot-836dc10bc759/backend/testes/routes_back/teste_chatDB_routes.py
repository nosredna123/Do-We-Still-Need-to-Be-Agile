from app.routes_back.chatDB_routes import getChatByID, getChatsByUser, createChat, updateChat
from app.schemas.chat import ChatSchema


def teste_getChatByID(id: int):
    chat = getChatByID(id)

    return chat

def teste_getChatsByUser(user_id: int):
    chats = getChatsByUser(user_id)
    return chats

def teste_createChat(chat: dict):
    return createChat(**chat)

def teste_updateChat(chat: ChatSchema):
    return updateChat(chat)

def teste_1_update_with_chat():
    chat_to_update = getChatByID(5)
    chat_to_update.chat_name = 'teste_dev3'

    
    print(updateChat(chat_to_update))

    print("\nChats do usuario 1:\n")
    print(getChatsByUser(user_id))
# Testar
if __name__ == "__main__":
    chat_id, user_id = 4, 1

    print(teste_getChatByID(chat_id))


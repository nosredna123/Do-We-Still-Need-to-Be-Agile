from app.routes_back.llm_routes import getAnswertheQuery
from app.routes_back.chatmessageDB_routes import createChatMessage

dict_questoes = [
    {"chat_id":5,"question_id":1,}, # qnto é 1+1
    {"chat_id":5,"question_id":2,}, # questao do banho
    {"chat_id":36,"question_id":4,}, # questao custo cada hotel

]


if __name__ == "__main__":
    
    query = input("Digite sua consulta: ") 


    # createChatMessage(5, 'user', query, 2)


    answ = getAnswertheQuery(
        **dict_questoes[2],
        query=query
    )

    # createChatMessage(5, 'llm', answ, 2)


    print(answ)     

from fastapi import APIRouter, HTTPException, Body
from app.schemas.user import UserSchema

from app.routes_back.userDB_routes import getUserByID

router = APIRouter(prefix="/user", tags=["user"])

@router.get("/login/")
def login(email: str = Body(), password: str = Body()):
    """
        Recebe email e senha como json e retorna uma mensagem de sucesso, setando o user no back e retornando o UserSchema completo.

        Ex de uso: GET http://127.0.0.1:8000/user/login (corpo no formato {"email": "fulano@mail.com", "password": "123456"})
    """
    #chama função de verificar se dados estão corretos e retornar estudante se sim
    user = UserSchema(id=2, username= "fulano", email= "fulano@mail.com", password="123")#placeholder
    if not user:
        raise HTTPException(status_code=404, detail="Username ou senha incorretos")
    #colocar aqui função de setar dependency com esse usuário atual
    return user

@router.get("/logout/")
def login():
    """
        Faz logout do usuário.

        Ex de uso: GET http://127.0.0.1:8000/user/logout
    """
    #colocar função de tirar o user atual como dependency
    return {"message": "Usuário saiu com sucesso"}

@router.get("/")
def userinfo():
    """
        Retorna UserSchema do usuário atualmente logado.

        Ex de uso: GET http://127.0.0.1:8000/user/
    """
    user = getUserByID(4) #sempre puxa o user 4 por enquanto
    return user

@router.post("/")
def register(username: str = Body(), email: str = Body(), password: str = Body()):
    """
        Chama a função de adicionar no banco de dados, retorna o UserSchema completo se o username não existe E a senha é válida.

        Ex de uso: POST http://127.0.0.1:8000/user/ (corpo no formato {"username": "fulano", "email": "fulano@mail.com", "password": "123456"})
    """
    #verifica se a senha é válida, daí chama createUser em userDB_routes diretamente
    user = UserSchema(id=3, username= "fulano", email= "fulano@gmail.com", password="123") #placeholder
    if not user:
        raise HTTPException(status_code=400, detail="Username já existe ou senha é inválida")
    return user

@router.put("/")
def updateUserInfo(item: UserSchema):
    """
        Usa um UserSchema modificado e usa seu id para atualizar o banco de dados. Retorna mensagem de sucesso ou fracasso.

        Ex de uso: PUT http://127.0.0.1:8000/user/ (corpo é UserSchema)
    """
    #chama updateUser em userDB_routes diretamente
    user_atualizado = item #placeholder
    if not user_atualizado:
        raise HTTPException(status_code=404, detail="Não existe usuário com esse id")
    return {"message": "Usuário atualizado com sucesso!"}

@router.delete("/")
def deleteUser():
    """
        Apaga o usuário atualmente logado no sistema.

        Ex de uso: DELETE http://127.0.0.1:8000/user/
    """
    #usa dependency para pega o user atual, chama a função de logout nele e por fim chama deleteUser nele em userDB_routes
    return {"message": "Usuário apagado com sucesso"}
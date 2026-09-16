from app.routes_back.userDB_routes import getUserByID, createUser


def teste_getUserByID(id = 1):
    user = getUserByID(id)
    print(user)

def teste_createUser():
    user = {
        'username': 'lucas',
        'email': 'lucas@email.com',
        'password': 'senha123'
    }

    return createUser(**user)

# Testar
user = teste_createUser()
print(user)

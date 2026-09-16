import os
import sys
from dotenv import load_dotenv

# Define o caminho absoluto para a pasta 'interface'
interface_path = os.path.join(os.path.dirname(__file__), 'interface')

# Adiciona a pasta 'interface' ao início do sys.path para dar prioridade
sys.path.insert(0, interface_path)

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Importa o módulo app.app (o arquivo app.py dentro da pasta app)
import app.app

# Agora, acessamos a variável 'app' e 'db' de dentro do módulo importado
flask_app = app.app.app
db = app.app.db

# Cria as tabelas dentro do contexto da aplicação Flask
with flask_app.app_context():
    print("Criando as tabelas no banco de dados...")
    db.create_all()
    print("Tabelas criadas com sucesso!")

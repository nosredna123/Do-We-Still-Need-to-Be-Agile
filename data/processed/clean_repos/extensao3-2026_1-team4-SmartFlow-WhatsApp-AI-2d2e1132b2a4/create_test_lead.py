import os
import sys
import json
from dotenv import load_dotenv

# --- Configuração para acessar os módulos da interface ---
interface_path = os.path.join(os.path.dirname(__file__), 'interface')
sys.path.insert(0, interface_path)
load_dotenv()

# Importa o app e os modelos do Flask
import app.app
flask_app = app.app.app
db = app.app.db
Lead = app.app.Lead
IA = app.app.IA
# --- Fim da Configuração ---


def create_lead():
    with flask_app.app_context():
        print("Procurando por uma IA para associar o lead...")
        # Pega a primeira IA que encontrar no banco, ou cria uma se não houver nenhuma.
        target_ia = db.session.query(IA).first()
        if not target_ia:
            print("Nenhuma IA encontrada. Criando uma IA de teste chamada 'Julie'...")
            target_ia = IA(name="Julie", phone_number="5511999998888", status=True)
            db.session.add(target_ia)
            db.session.commit()
            print("IA 'Julie' criada com sucesso.")

        print(f"Associando o lead à IA: '{target_ia.name}' (ID: {target_ia.id})")

        # Dados do lead de teste
        lead_name = "Cliente Teste"
        lead_phone = "5511912345678"
        
        # Verifica se o lead já existe
        existing_lead = db.session.query(Lead).filter_by(phone=lead_phone).first()
        if existing_lead:
            print(f"Lead para o número {lead_phone} já existe. Nenhuma ação necessária.")
            return

        print("Criando um novo lead de teste...")
        new_lead = Lead(
            ia_id=target_ia.id,
            name=lead_name,
            phone=lead_phone,
            message=json.dumps([{"role": "user", "content": "Olá, gostaria de um orçamento."}]),
            resume="Este é um lead de teste gerado automaticamente."
        )
        db.session.add(new_lead)
        db.session.commit()
        print("Lead de teste criado com sucesso!")

if __name__ == "__main__":
    create_lead()

from app.RAGcore.Knowledge_ingestor import KnowledgeIngestor
from app.database.connection import init_db
from app.database.models import IA

def main():
    
    db = init_db()
    
    try:
       
        ias = db.query(IA).order_by(IA.id).all()

        if not ias:
            print("Nenhuma IA cadastrada.")
            return

        
        print("\nIAs disponíveis:\n")
        for ia in ias:
            status = "Ativa" if ia.status else "Inativa"
            print(f"ID: {ia.id} | Nome: {ia.name} | Status: {status}")

    finally:
        db.close()

   
    ingestor = KnowledgeIngestor()

    print("\nSelecione o tipo de ingestão:")
    print("1 - Texto direto")
    print("2 - Arquivo TXT")
    print("3 - Arquivo PDF")

    opcao = input("\nOpção: ")


    id_ia = int(input("\nID da IA para associar o conhecimento: "))

    if opcao == "1":
        
        texto = input("\nDigite o texto que deseja ingerir:\n\n")
        ingestor.ingest_text(
            ia_id=id_ia,
            text=texto
        )

    elif opcao == "2":
       
        caminho_do_arquivo = input("\nCaminho do arquivo TXT: ")
        ingestor.ingest_txt(
            ia_id=id_ia,
            file_path=caminho_do_arquivo
        )

    elif opcao == "3":
        
        caminho_do_arquivo = input("\nCaminho do arquivo PDF: ")
        ingestor.ingest_pdf(
            ia_id=id_ia,
            file_path=caminho_do_arquivo
        )

    else:
        print("\nOpção inválida.")
        return

    print("\nProcesso finalizado!")

if __name__ == "__main__":
    main()
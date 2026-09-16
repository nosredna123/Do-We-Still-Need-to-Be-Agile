import asyncio
import os
import sys

# Adicionar o diretório atual ao path para importar módulos do app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.vector_service import VectorService

async def main():
    print("=== Iniciando Ingestão de Dados ===")
    
    # Caminho para a pasta batches
    batches_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app", "batches")
    
    if not os.path.exists(batches_dir):
        print(f"Erro: Diretório não encontrado: {batches_dir}")
        return

    service = VectorService()
    
    print(f"Lendo arquivos de: {batches_dir}")
    count = await service.process_directory(batches_dir)
    
    print(f"=== Ingestão Concluída ===")
    print(f"Total de arquivos processados: {count}")

if __name__ == "__main__":
    asyncio.run(main())

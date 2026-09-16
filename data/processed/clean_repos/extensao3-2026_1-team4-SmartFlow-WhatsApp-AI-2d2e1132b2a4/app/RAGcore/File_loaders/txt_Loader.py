# app/RAGcore/loaders/txt_loader.py

from pathlib import Path


class TXTLoader:

    def load(
        self,
        file_path: str,
        encoding: str = "utf-8"
    ) -> str:

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Arquivo não encontrado: {file_path}"
            )

        if path.suffix.lower() != ".txt":
            raise ValueError(
                "O arquivo precisa ser .txt"
            )

        with open(
            path,
            "r",
            encoding=encoding
        ) as file:

            text = file.read()

        return text
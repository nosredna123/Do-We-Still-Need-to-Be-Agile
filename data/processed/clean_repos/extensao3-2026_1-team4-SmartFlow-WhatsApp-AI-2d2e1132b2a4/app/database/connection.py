#Exclusivo para fazer a conexão com o BD

import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

#Carrega diretamente os arquivos da pasta ambientevirtual
load_dotenv()

database_url = os.getenv("DATABASE_URL")

project_root = Path(__file__).resolve().parents[2]
interface_db = project_root / "interface" / "instance" / "smartflow.db"

if not database_url:
    database_url = "sqlite:///smartflow.db"

if database_url == "sqlite:///smartflow.db" and interface_db.exists():
    database_url = f"sqlite:///{interface_db.as_posix()}"

engine_options = {"echo": False}

if not database_url.startswith("sqlite"):
    engine_options.update(
        {
            "pool_size": 10,
            "max_overflow": 20,
            "pool_timeout": 120,
            "pool_recycle": 1800,
        }
    )

engine = create_engine(database_url, **engine_options)

SessinLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    return SessinLocal()

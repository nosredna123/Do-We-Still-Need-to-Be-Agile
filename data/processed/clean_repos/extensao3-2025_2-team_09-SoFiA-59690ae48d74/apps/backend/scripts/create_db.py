import sys
import os
import datetime
from sqlalchemy.orm import Session

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.db.database.base import Base
from src.db.database.connection import engine, SessionLocal
from src.db.models.models import Category

INITIAL_CATEGORIES = [
    {"id": 1, "name": "Lazer"},
    {"id": 2, "name": "Transporte"},
    {"id": 3, "name": "Impostos"},
    {"id": 4, "name": "Tecnologia"},
    {"id": 5, "name": "Viagem"},
    {"id": 6, "name": "Pets"},
    {"id": 7, "name": "Alimentação"},
    {"id": 8, "name": "Casa"},
    {"id": 9, "name": "Educação"},
    {"id": 10, "name": "Saúde"},
    {"id": 11, "name": "Despesas Pessoais"},
]


def seed_categories(db: Session):
    """
    Populates the database with initial categories if they do not exist.
    """
    print("Seeding categories...")
    count = 0
    now = datetime.datetime.now()
    for cat_data in INITIAL_CATEGORIES:
        existing_category = (
            db.query(Category).filter(Category.name == cat_data["name"]).first()
        )
        existing_id = db.query(Category).filter(Category.id == cat_data["id"]).first()

        if not existing_category and not existing_id:
            new_category = Category(
                id=cat_data["id"], name=cat_data["name"], updated_at=now
            )
            db.add(new_category)
            count += 1
        else:
            print(f"  Skipping '{cat_data['name']}' (already exists).")

    if count > 0:
        db.commit()
        print(f"Successfully added {count} categories.")
    else:
        print("No new categories were added.")


def init_db():
    """
    Creates all database tables defined in models.py and seeds initial data.
    """
    print("Connecting to the database and creating tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully.")
        db = SessionLocal()
        try:
            seed_categories(db)
        finally:
            db.close()

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    init_db()

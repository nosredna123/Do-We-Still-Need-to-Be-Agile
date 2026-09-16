from app.database import engine, Base
from app.models import question_model, topic_model, subject_model, student_model, chat_model,\
                       chatquestion_model, prompt_model, image_model  # Importante importar os models para o Base conhecê-los

# Cria todas as tabelas definidas que herdam de Base
Base.metadata.create_all(bind=engine)
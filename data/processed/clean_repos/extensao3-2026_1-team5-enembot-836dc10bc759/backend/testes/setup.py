from app.database import engine, Base
from app.models import topic_model, subject_model, student_model, chat_model,\
                       chatquestion_model, prompt_model, question_model, image_model

# Cria todas as tabelas definidas que herdam de Base
Base.metadata.create_all(bind=engine)
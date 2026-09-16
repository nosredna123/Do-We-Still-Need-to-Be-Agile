from rest_framework.exceptions import APIException
from rest_framework import status

class ChatClosedException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Você não pode mais enviar mensagens neste chat, pois ele foi encerrado após a atualização da sua anamnese."
    default_code = "chat_closed"
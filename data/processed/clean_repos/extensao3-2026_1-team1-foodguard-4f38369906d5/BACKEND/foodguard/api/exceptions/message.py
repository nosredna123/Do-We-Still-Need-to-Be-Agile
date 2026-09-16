from rest_framework.exceptions import APIException
from rest_framework import status


class RoleNotAllowedException(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Seu perfil de usuário não possui privilégios para executar operações como Sistema."
    default_code = "role_not_allowed"
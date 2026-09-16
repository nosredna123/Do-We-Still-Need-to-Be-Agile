from rest_framework.exceptions import APIException
from rest_framework import status


class AnamneseHasAlreadyBeenCreatedException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Usuário já possui uma anamnese cadastrada.'
    default_code = 'anamnese_already_exists'


class AnamneseObjectiveRequiredException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'O campo "Qual era o objetivo na época?" é obrigatório quando "Já fez consulta prévia com nutricionista?" é marcado como sim.'
    default_code = 'anamnese_objective_required'
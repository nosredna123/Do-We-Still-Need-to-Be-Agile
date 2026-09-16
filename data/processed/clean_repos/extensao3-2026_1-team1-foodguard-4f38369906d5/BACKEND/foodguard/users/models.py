from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

class User(AbstractUser):
    validador_name = RegexValidator(
        regex=r"^[a-zA-ZÀ-ÿ \'-]+$",
        message="O nome deve conter apenas letras, espaços, apóstrofos e hífens.",
        code="nome_invalido"
    )

    name = models.CharField(
        max_length=250,
        blank=False,
        null=False,
        validators=[validador_name],
    )
    email = models.EmailField(
        unique=True,
        blank=False,
        null=False,
        verbose_name="Email",
    )
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data de Nascimento"
    )

    def __str__(self):
        return self.username

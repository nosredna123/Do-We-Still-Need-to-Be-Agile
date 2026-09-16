import re
from django.core.exceptions import ValidationError

class CustomPasswordValidator:
    def validate(self, password, user=None):
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                "A senha deve conter pelo menos uma letra maiúscula.",
                code='password_no_upper',
            )
        
        if not re.search(r'[a-z]', password):
            raise ValidationError(
                "A senha deve conter pelo menos uma letra minúscula.",
                code='password_no_lower',
            )
            
        if not re.search(r'\d', password):
            raise ValidationError(
                "A senha deve conter pelo menos um número.",
                code='password_no_number',
            )

    def get_help_text(self):
        return "Sua senha deve conter pelo menos uma letra maiúscula, uma minúscula e um número."
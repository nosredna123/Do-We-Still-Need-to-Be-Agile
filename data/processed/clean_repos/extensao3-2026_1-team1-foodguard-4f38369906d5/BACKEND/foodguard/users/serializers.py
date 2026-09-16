from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from foodguard.core.models.anamnese import Anamnese

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'name', 'username', 'email', 'date_of_birth', 'password', 'password_confirm']
        read_only_fields = ['id']

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Já existe uma conta com este email.")
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError({"password_confirm": "As senhas não coincidem."})
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    """Leitura do perfil do usuário autenticado (RF014/RF015)."""

    has_anamnese = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'name', 'username', 'email', 'date_of_birth', 'has_anamnese']
        read_only_fields = ['id', 'name', 'email', 'date_of_birth', 'has_anamnese']

    def get_has_anamnese(self, obj) -> bool:
        return Anamnese.objects.filter(user=obj).exists()


class UserUpdateSerializer(serializers.ModelSerializer):
    """Edição de perfil restrita (RN010): username e senha editáveis."""

    password = serializers.CharField(write_only=True, required=False, validators=[validate_password])

    class Meta:
        model = User
        fields = ['username', 'password']

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Autentica por email (RF003) em vez de username."""

    username_field = User.EMAIL_FIELD

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['name'] = user.name
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['has_anamnese'] = Anamnese.objects.filter(user=self.user).exists()
        data['user'] = UserSerializer(self.user).data
        return data

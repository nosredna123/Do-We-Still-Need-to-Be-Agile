"""Testes da feature "galeria de chats": persistência da imagem do produto
(OpenFoodFacts) e da severidade (veredito mais recente) no registro do Chat,
exposição desses campos pela API e sobrevivência da imagem na validação.
"""
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient, APIRequestFactory

from foodguard.api.serializers.chat import ChatSerializer
from foodguard.api.serializers.openfoodfacts import OpenFoodFactsSerializer
from foodguard.api.views.message import _food_image_url
from foodguard.core.models.chat import Chat

User = get_user_model()

FRONT = "https://images.openfoodfacts.org/front.jpg"
GENERIC = "https://images.openfoodfacts.org/generic.jpg"

SEND_URL = "/api/chats/message/send/"
LIST_URL = "/api/chats/"


def make_food_data(front=None, generic=None, name="Biscoito Recheado"):
    product = {"product_name": name}
    if front is not None:
        product["image_front_url"] = front
    if generic is not None:
        product["image_url"] = generic
    return {"code": "789", "product": product, "status": 1, "status_verbose": "ok"}


def make_user(email="u@example.com", username="u"):
    return User.objects.create_user(
        username=username, email=email, password="Senha123", name="Usuário Teste"
    )


# --------------------------------------------------------------------------- #
# Unidade: helper de imagem                                                    #
# --------------------------------------------------------------------------- #
class FoodImageHelperTests(TestCase):
    def test_prefers_front_image(self):
        self.assertEqual(
            _food_image_url(make_food_data(front=FRONT, generic=GENERIC)), FRONT
        )

    def test_falls_back_to_generic_image(self):
        self.assertEqual(_food_image_url(make_food_data(generic=GENERIC)), GENERIC)

    def test_none_food_data_returns_empty(self):
        self.assertEqual(_food_image_url(None), "")

    def test_product_without_image_returns_empty(self):
        self.assertEqual(_food_image_url(make_food_data()), "")


# --------------------------------------------------------------------------- #
# Unidade: serializers                                                         #
# --------------------------------------------------------------------------- #
class OpenFoodFactsSerializerTests(TestCase):
    def test_image_fields_survive_validation(self):
        serializer = OpenFoodFactsSerializer(
            data=make_food_data(front=FRONT, generic=GENERIC)
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        product = serializer.validated_data["product"]
        self.assertEqual(product["image_front_url"], FRONT)
        self.assertEqual(product["image_url"], GENERIC)


class ChatSerializerTests(TestCase):
    def test_exposes_image_url_and_severity(self):
        user = make_user()
        chat = Chat.objects.create(
            user=user, title="Doce", image_url=FRONT, severity="HIGH_RISK"
        )
        request = APIRequestFactory().get(LIST_URL)
        data = ChatSerializer(chat, context={"request": request}).data
        self.assertEqual(data["image_url"], FRONT)
        self.assertEqual(data["severity"], "HIGH_RISK")
        self.assertIn("messages", data)


# --------------------------------------------------------------------------- #
# Integração: fluxo de envio de mensagem alimentando a galeria                 #
# --------------------------------------------------------------------------- #
class MessageGalleryIntegrationTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    @staticmethod
    def _mock_ai(verdict):
        # spec restringe os atributos: hasattr(client, "continue_conversation")
        # é False, forçando sempre o caminho de avaliação (assess_safety), que
        # produz um veredito — simplifica os testes (sem modo conversacional).
        client = Mock(spec=["assess_safety"])
        client.assess_safety.return_value = {
            "explanation": "Análise de segurança.",
            "verdict": verdict,
            "recommends_doctor": False,
        }
        return client

    @patch("foodguard.api.views.message._extract_and_store_context")
    @patch("foodguard.api.views.message.get_ai_client")
    def test_new_chat_persists_image_and_severity(self, mock_get_ai, _ext):
        mock_get_ai.return_value = self._mock_ai("HIGH_RISK")
        resp = self.client.post(
            SEND_URL,
            {
                "role": "U",
                "content": "Posso comer isso?",
                "food_data": make_food_data(front=FRONT, generic=GENERIC),
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201, resp.data)
        self.assertEqual(resp.data["verdict"], "HIGH_RISK")
        chat = Chat.objects.get(id=resp.data["chat_id"])
        self.assertEqual(chat.image_url, FRONT)
        self.assertEqual(chat.severity, "HIGH_RISK")
        # Título vem do nome do produto escaneado.
        self.assertEqual(chat.title, "Biscoito Recheado")

    @patch("foodguard.api.views.message._extract_and_store_context")
    @patch("foodguard.api.views.message.get_ai_client")
    def test_chat_without_product_has_no_image(self, mock_get_ai, _ext):
        mock_get_ai.return_value = self._mock_ai("SAFE")
        resp = self.client.post(
            SEND_URL, {"role": "U", "content": "Olá, tudo bem?"}, format="json"
        )
        self.assertEqual(resp.status_code, 201, resp.data)
        chat = Chat.objects.get(id=resp.data["chat_id"])
        self.assertIsNone(chat.image_url)
        self.assertEqual(chat.severity, "SAFE")

    @patch("foodguard.api.views.message._extract_and_store_context")
    @patch("foodguard.api.views.message.get_ai_client")
    def test_severity_reflects_most_recent_verdict(self, mock_get_ai, _ext):
        # 1ª avaliação → LOW_CONCERN
        mock_get_ai.return_value = self._mock_ai("LOW_CONCERN")
        r1 = self.client.post(
            SEND_URL, {"role": "U", "content": "primeira"}, format="json"
        )
        chat_id = r1.data["chat_id"]
        self.assertEqual(Chat.objects.get(id=chat_id).severity, "LOW_CONCERN")

        # 2ª avaliação no mesmo chat → HIGH_RISK (mais recente prevalece)
        mock_get_ai.return_value = self._mock_ai("HIGH_RISK")
        r2 = self.client.post(
            SEND_URL,
            {"role": "U", "content": "segunda", "chat_id": chat_id},
            format="json",
        )
        self.assertEqual(r2.status_code, 201, r2.data)
        self.assertEqual(Chat.objects.get(id=chat_id).severity, "HIGH_RISK")

    @patch("foodguard.api.views.message._extract_and_store_context")
    @patch("foodguard.api.views.message.get_ai_client")
    def test_image_backfilled_when_initially_absent(self, mock_get_ai, _ext):
        # 1ª mensagem sem produto → sem imagem
        mock_get_ai.return_value = self._mock_ai("SAFE")
        r1 = self.client.post(
            SEND_URL, {"role": "U", "content": "sem produto"}, format="json"
        )
        chat_id = r1.data["chat_id"]
        self.assertIsNone(Chat.objects.get(id=chat_id).image_url)

        # 2ª mensagem com produto → imagem preenchida
        mock_get_ai.return_value = self._mock_ai("SAFE")
        self.client.post(
            SEND_URL,
            {
                "role": "U",
                "content": "agora com produto",
                "chat_id": chat_id,
                "food_data": make_food_data(front=FRONT),
            },
            format="json",
        )
        self.assertEqual(Chat.objects.get(id=chat_id).image_url, FRONT)

    @patch("foodguard.api.views.message._extract_and_store_context")
    @patch("foodguard.api.views.message.get_ai_client")
    def test_chat_list_endpoint_returns_image_and_severity(self, mock_get_ai, _ext):
        mock_get_ai.return_value = self._mock_ai("MODERATE_RISK")
        self.client.post(
            SEND_URL,
            {
                "role": "U",
                "content": "Avalie",
                "food_data": make_food_data(front=FRONT),
            },
            format="json",
        )
        resp = self.client.get(LIST_URL)
        self.assertEqual(resp.status_code, 200)
        results = resp.data["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["image_url"], FRONT)
        self.assertEqual(results[0]["severity"], "MODERATE_RISK")

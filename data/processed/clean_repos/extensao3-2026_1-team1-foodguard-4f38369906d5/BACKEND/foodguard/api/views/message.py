import logging
import re
import threading

import dspy
from django.conf import settings
from django.db import connections, transaction
from django.http import Http404
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.exceptions import APIException
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle

from foodguard.api.exceptions.chat import ChatClosedException
from foodguard.api.exceptions.message import RoleNotAllowedException
from foodguard.api.serializers.message import MessageSerializer
from foodguard.core.models.anamnese import Anamnese
from foodguard.core.models.chat import Chat
from foodguard.core.models.message import Message
from foodguard.core.models.user_context import UserContext
from foodguard.core.services.context_extractor import ContextExtractorClient
from foodguard.core.services.gemini_client import GeminiClient
from foodguard.core.services.openai_client import OpenAIClient

logger = logging.getLogger('django')


class AIThrottle(UserRateThrottle):
    """Throttle dedicado aos endpoints de IA (rate definido em settings)."""
    scope = 'ai'


def _build_ai_client():
    if settings.AI_PROVIDER == "openai":
        return OpenAIClient()
    return GeminiClient()


_ai_client = None


def get_ai_client():
    """Lazy singleton — evita instanciar o client (e exigir API key) no import,
    o que quebraria commands como migrate/collectstatic."""
    global _ai_client
    if _ai_client is None:
        _ai_client = _build_ai_client()
    return _ai_client


_context_extractor = None


def get_context_extractor():
    """Lazy singleton do extrator de contexto. Retorna None se não houver
    OPENAI_API_KEY configurada (o recurso fica desligado, sem quebrar o chat)."""
    global _context_extractor
    if not settings.OPENAI_API_KEY:
        return None
    if _context_extractor is None:
        _context_extractor = ContextExtractorClient()
    return _context_extractor


def _get_user_context_text(user) -> str:
    ctx = UserContext.objects.filter(user=user).only("content").first()
    return ctx.content.strip() if ctx and ctx.content else ""


# Mensagem que é só o template de escaneamento (sem texto do usuário).
_SCAN_ONLY_RE = re.compile(
    r"^Acabei de escanear o produto:.*?O que você pode me dizer sobre ele\?\s*$",
    re.DOTALL,
)
# Sufixo "[Produto escaneado: ...]" anexado quando o usuário também digitou texto.
_SCAN_SUFFIX_RE = re.compile(r"\n\n\[Produto escaneado:.*?\]\s*$", re.DOTALL)


def _user_text_for_context(content: str) -> str:
    """Isola o que o usuário REALMENTE digitou, removendo o texto automático de
    escaneamento. Evita que o nome do produto influencie a extração de contexto
    (ex.: escanear um biscoito de chocolate não pode mexer na alergia a chocolate)."""
    if not content:
        return ""
    stripped = content.strip()
    if _SCAN_ONLY_RE.match(stripped):
        return ""  # nada além do template de escaneamento
    return _SCAN_SUFFIX_RE.sub("", stripped).strip()


def _extract_and_store_context(user_id, user_message, anamnesis_text, existing_context_text):
    """Roda em thread separada (paralela ao modelo principal): extrai fatos
    duráveis da mensagem e os persiste no contexto do usuário.

    Concorrência: usa transação + select_for_update para serializar leituras/
    escritas concorrentes do mesmo UserContext (evita lost update). Usa conexão
    de banco própria da thread, fechada no finally.
    """
    try:
        extractor = get_context_extractor()
        if extractor is None:
            return

        # Usa apenas o que o usuário digitou (sem o boilerplate de escaneamento).
        clean_message = _user_text_for_context(user_message)
        if not clean_message:
            return

        ops = extractor.analyze(clean_message, anamnesis_text, existing_context_text)
        to_add, to_remove = ops["add"], ops["remove"]
        if not to_add and not to_remove:
            return

        # Garante a existência da linha antes do lock (get_or_create trata a
        # corrida de criação da OneToOne via IntegrityError internamente).
        UserContext.objects.get_or_create(user_id=user_id)

        with transaction.atomic():
            ctx = UserContext.objects.select_for_update().get(user_id=user_id)
            lines = [ln.strip() for ln in ctx.content.splitlines() if ln.strip()]

            # Remoções (resolvidos/contraditos) — match case-insensitive.
            remove_keys = {r.lower() for r in to_remove}
            kept = [ln for ln in lines if ln.lower() not in remove_keys]

            # Adições (sem duplicar).
            seen = {ln.lower() for ln in kept}
            for fact in to_add:
                if fact.lower() not in seen:
                    seen.add(fact.lower())
                    kept.append(fact)

            new_content = "\n".join(kept)
            if new_content != ctx.content:
                ctx.content = new_content
                ctx.save(update_fields=["content", "updated_at"])
                logger.info(
                    "Contexto do usuário %s atualizado (+%d/-%d).",
                    user_id, len(to_add), len(remove_keys),
                )
    except Exception as e:
        logger.error("Erro ao analisar/salvar contexto do usuário: %s", str(e), exc_info=True)
    finally:
        # Fecha a conexão de banco aberta nesta thread.
        connections.close_all()


_VERDICT_CODES_RE = re.compile(
    r"\b(?:SAFE|LOW_CONCERN|MODERATE_RISK|HIGH_RISK|INSUFFICIENT_DATA)\b"
)


def _strip_verdict_codes(text: str) -> str:
    """Remove qualquer código de veredito que o modelo tenha vazado no texto —
    o veredito vai à parte no campo `verdict`, não na resposta ao usuário."""
    if not text:
        return text
    cleaned = _VERDICT_CODES_RE.sub("", text)
    cleaned = re.sub(r"\(\s*\)|\[\s*\]", "", cleaned)  # parênteses/colchetes vazios
    # Remove rótulos órfãos deixados pela remoção do código (ex.: "Veredito: .")
    cleaned = re.sub(
        r"(?i)\b(veredito|classifica[çc][ãa]o|classificado como)\s*[:\-]?\s*(?=[.,;]|$)",
        "",
        cleaned,
    )
    cleaned = re.sub(r"\s+([,.;:!?])", r"\1", cleaned)  # espaço antes de pontuação
    cleaned = re.sub(r"([,;:]\s*){2,}", lambda m: m.group(0)[-2:], cleaned)  # pontuação repetida
    cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)
    cleaned = re.sub(r"^[\s,.;:]+", "", cleaned)  # pontuação/espaço no início
    return cleaned.strip()


def _format_anamnesis(anamnese: Anamnese) -> str:
    lines = [
        f"Estilo alimentar: {anamnese.get_eating_style_display()}",
        f"Sentimento sobre o corpo e alimentação: {anamnese.get_body_feeling_display() or 'Não informado'}",
        f"Consumo de álcool: {'Sim' if anamnese.alcohol_intake else 'Não'}",
        f"Tabagismo: {'Sim' if anamnese.smoking else 'Não'}",
        f"Alergias alimentares: {anamnese.food_allergies or 'Nenhuma relatada'}",
        f"Intolerâncias alimentares: {anamnese.food_intolerances or 'Nenhuma relatada'}",
        f"Alimentos favoritos: {anamnese.favorite_foods or 'Não informado'}",
        f"Aversões alimentares: {anamnese.food_aversions or 'Nenhuma relatada'}",
        f"Histórico de doenças: {anamnese.disease_history or 'Nenhum relatado'}",
        f"Medicamentos em uso: {anamnese.medications or 'Nenhum'}",
    ]
    if anamnese.previous_consultation:
        lines.append(
            f"Consulta prévia com nutricionista — Objetivo: {anamnese.previous_consultation_objective}"
        )
        if anamnese.previous_consultation_result:
            lines.append(f"Resultado da consulta: {anamnese.previous_consultation_result}")

    return "\n".join(lines)


_NUTRIMENT_FIELDS = [
    ("energy-kcal_100g", "Energia", "kcal"),
    ("carbohydrates_100g", "Carboidratos", "g"),
    ("sugars_100g", "Açúcares", "g"),
    ("fat_100g", "Gorduras totais", "g"),
    ("saturated-fat_100g", "Gorduras saturadas", "g"),
    ("fiber_100g", "Fibras", "g"),
    ("proteins_100g", "Proteínas", "g"),
    ("salt_100g", "Sal", "g"),
    ("sodium_100g", "Sódio", "g"),
]


def _format_nutriments(nutriments: dict | None) -> str:
    if not nutriments:
        return ""
    parts = [
        f"{label}: {nutriments[key]}{unit}"
        for key, label, unit in _NUTRIMENT_FIELDS
        if nutriments.get(key) is not None
    ]
    return "; ".join(parts)


def _format_food_data(food_data: dict | None) -> str:
    if not food_data:
        return "Nenhum produto específico fornecido. Análise baseada apenas na query do usuário."

    product = food_data.get('product', {})
    product_name = product.get('product_name') or 'Nome não disponível'

    ingredients = product.get('ingredients', [])
    ingredient_list = ", ".join(
        f"{ing['text']} ({ing.get('percent_estimate', 0):.1f}%)"
        for ing in ingredients
        if ing.get('text')
    )
    if not ingredient_list:
        ingredient_list = (product.get('ingredients_text') or "").strip()

    allergens = ", ".join(product.get('allergens_tags', [])) or "Nenhum declarado"
    additives = ", ".join(product.get('additives_tags', [])) or "Nenhum"

    lines = [
        f"Produto: {product_name}",
        f"Ingredientes: {ingredient_list or 'Não disponível'}",
        f"Alérgenos declarados: {allergens}",
        f"Aditivos: {additives}",
    ]

    nutriments = _format_nutriments(product.get('nutriments'))
    if nutriments:
        lines.append(f"Informação nutricional (por 100g): {nutriments}")

    return "\n".join(lines)


def _chat_title(food_data: dict | None, fallback: str) -> str:
    """Título do chat: nome do produto escaneado quando disponível, senão a
    mensagem do usuário truncada até a 4ª palavra (sem quebrar palavras),
    com reticências quando houver mais palavras."""
    if food_data:
        name = (food_data.get('product', {}).get('product_name') or "").strip()
        if name:
            return name[:255]
    words = fallback.split()
    title = " ".join(words[:4])
    if len(words) > 4:
        title += "..."
    return title[:255]


def _food_image_url(food_data: dict | None) -> str:
    """URL da imagem do produto escaneado (OpenFoodFacts), exibida no card da
    galeria. Prefere a imagem frontal; cai para a imagem genérica."""
    if not food_data:
        return ""
    product = food_data.get('product', {})
    return (product.get('image_front_url') or product.get('image_url') or "").strip()


def _build_history(chat: Chat, exclude_message_id) -> dspy.History:
    """Monta o histórico DSPy pareando mensagens U -> A em ordem cronológica.

    Exclui a mensagem de usuário recém-salva (a que está sendo respondida agora).
    """
    messages = (
        Message.objects.filter(chat=chat)
        .exclude(id=exclude_message_id)
        .order_by('created_at')
    )

    turns = []
    pending_user = None
    for message in messages:
        if message.role == Message.Role.USER:
            if pending_user is not None:
                logger.warning(
                    "Mensagem de usuário sem resposta da IA no chat %s; "
                    "incluindo turno com answer vazia.", chat.id,
                )
                turns.append({"user_query": pending_user, "answer": ""})
            pending_user = message.content
        elif message.role == Message.Role.ASSISTANT and pending_user is not None:
            turns.append({"user_query": pending_user, "answer": message.content})
            pending_user = None

    return dspy.History(messages=turns)


@extend_schema(
    summary="Cria uma nova mensagem de chat",
    description=(
        "Recebe o texto do usuário e, opcionalmente, dados de produto via OpenFoodFacts. "
        "Na primeira interação (ou quando um produto é enviado) executa o pipeline DSPy de "
        "análise de segurança alimentar e retorna o veredito estruturado (verdict). Em "
        "mensagens de acompanhamento sem produto, responde em modo conversacional usando o "
        "histórico do chat (verdict = null). O modo conversacional requer AI_PROVIDER=openai."
    ),
    responses={
        201: inline_serializer(
            name="MessageCreateResponse",
            fields={
                "chat_id": serializers.UUIDField(),
                "response": serializers.CharField(),
                "verdict": serializers.ChoiceField(
                    choices=[
                        "SAFE", "LOW_CONCERN", "MODERATE_RISK",
                        "HIGH_RISK", "INSUFFICIENT_DATA",
                    ],
                    allow_null=True,
                ),
                "recommends_doctor": serializers.BooleanField(),
            },
        )
    },
)
class MessageCreateAPIView(CreateAPIView):
    serializer_class = MessageSerializer
    throttle_classes = [AIThrottle]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        role = serializer.validated_data.get('role')
        if role == Message.Role.ASSISTANT:
            raise RoleNotAllowedException()

        chat_id = serializer.validated_data.get('chat_id')
        user_message_content = serializer.validated_data.get('content', '')

        ai_client = get_ai_client()
        food_data = serializer.validated_data.get('food_data')

        try:
            with transaction.atomic():
                if not chat_id:
                    chat = Chat.objects.create(
                        user=request.user,
                        title=_chat_title(food_data, user_message_content),
                        image_url=_food_image_url(food_data) or None,
                    )
                else:
                    chat = get_object_or_404(Chat, id=chat_id, user=request.user)

                if not chat.is_open:
                    raise ChatClosedException()

                has_prior_assistant = Message.objects.filter(
                    chat=chat, role=Message.Role.ASSISTANT
                ).exists()
                supports_conversation = hasattr(ai_client, "continue_conversation")
                is_follow_up = (
                    not food_data and has_prior_assistant and supports_conversation
                )

                user_message = serializer.save(chat=chat)

                anamnese = Anamnese.objects.filter(user=request.user).first()
                anamnesis_text = (
                    _format_anamnesis(anamnese) if anamnese else "Anamnese não disponível."
                )
                # Contexto acumulado de conversas anteriores (fatos fora da anamnese).
                existing_context_text = _get_user_context_text(request.user)
                user_anamnesis = anamnesis_text
                if existing_context_text:
                    user_anamnesis += (
                        "\n\nInformações adicionais que o usuário mencionou em "
                        "conversas anteriores:\n" + existing_context_text
                    )

                if is_follow_up:
                    result = ai_client.continue_conversation(
                        user_anamnesis=user_anamnesis,
                        food_context=_format_food_data(food_data),
                        history=_build_history(chat, exclude_message_id=user_message.id),
                        user_query=user_message.content,
                    )
                    ai_content = result["response"]
                    verdict = None
                else:
                    result = ai_client.assess_safety(
                        user_anamnesis=user_anamnesis,
                        food_ingredients=_format_food_data(food_data),
                        user_query=user_message.content,
                    )
                    ai_content = result["explanation"]
                    verdict = result["verdict"]

                ai_content = _strip_verdict_codes(ai_content)

                ai_message = Message.objects.create(
                    chat=chat,
                    role=Message.Role.ASSISTANT,
                    content=ai_content,
                    verdict=verdict,
                    recommends_doctor=result.get("recommends_doctor", False),
                )

                # Cache desnormalizado para a galeria: severidade = veredito mais
                # recente; preenche a imagem do chat se ainda não houver uma e este
                # produto trouxer imagem (ex.: produto escaneado num follow-up).
                chat_updates = []
                if verdict is not None:
                    chat.severity = verdict
                    chat_updates.append('severity')
                if not chat.image_url:
                    new_image = _food_image_url(food_data)
                    if new_image:
                        chat.image_url = new_image
                        chat_updates.append('image_url')
                if chat_updates:
                    chat_updates.append('updated_at')
                    chat.save(update_fields=chat_updates)
        except (Http404, APIException):
            raise
        except Exception as e:
            logger.error("Erro no pipeline de IA: %s", str(e), exc_info=True)
            return Response(
                {"error": "Erro ao processar sua resposta"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Extração de contexto do usuário em paralelo (fire-and-forget): não
        # bloqueia a resposta. Usa valores já capturados (strings/ids), sem
        # compartilhar objetos do ORM nem a transação entre threads.
        threading.Thread(
            target=_extract_and_store_context,
            args=(
                request.user.id,
                user_message_content,
                anamnesis_text,
                existing_context_text,
            ),
            daemon=True,
        ).start()

        return Response(
            {
                "chat_id": chat.id,
                "response": ai_message.content,
                "verdict": verdict,
                "recommends_doctor": result["recommends_doctor"],
            },
            status=status.HTTP_201_CREATED,
        )


@extend_schema(summary="Lista mensagens de um chat específico do usuário")
class MessageListAPIView(ListAPIView):
    serializer_class = MessageSerializer

    def get_queryset(self):
        chat_id = self.kwargs['chat_id']
        return (
            Message.objects.filter(chat_id=chat_id, chat__user=self.request.user)
            .order_by('created_at')
        )

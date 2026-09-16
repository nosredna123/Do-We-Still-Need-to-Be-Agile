package com.sergio.chatbot.services

import java.time.ZonedDateTime
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import io.ktor.http.content.TextContent
import io.ktor.client.*
import io.ktor.client.call.*
import io.ktor.client.request.*
import io.ktor.client.statement.*
import io.ktor.client.plugins.contentnegotiation.*
import io.ktor.http.*
import io.ktor.serialization.kotlinx.json.*
import kotlinx.serialization.json.*

object GroqService {

    private val client = HttpClient {
        install(ContentNegotiation) {
            json(Json {
                ignoreUnknownKeys = true
            })
        }
    }

    // ⚠️ Remover antes do commit
    private val apiKey: String =
        ""

    private val mensagens = mutableListOf<Pair<String, String>>() // (role, content)

    // ============================================================
    //  GERAR RESPOSTA
    // ============================================================
    suspend fun gerarResposta(pergunta: String): String {

        // Hora real do Brasil
        val horarioBrasil = ZonedDateTime.now(ZoneId.of("America/Sao_Paulo"))
        val horaAtual = horarioBrasil.format(DateTimeFormatter.ofPattern("HH:mm"))

        // Dia da semana PT-BR
        val diaSemanaPt = when (horarioBrasil.dayOfWeek) {
            java.time.DayOfWeek.MONDAY -> "segunda-feira"
            java.time.DayOfWeek.TUESDAY -> "terça-feira"
            java.time.DayOfWeek.WEDNESDAY -> "quarta-feira"
            java.time.DayOfWeek.THURSDAY -> "quinta-feira"
            java.time.DayOfWeek.FRIDAY -> "sexta-feira"
            java.time.DayOfWeek.SATURDAY -> "sábado"
            java.time.DayOfWeek.SUNDAY -> "domingo"
        }

        mensagens.add("user" to pergunta)

        // ============================================================
        //  SYSTEM PROMPT
        // ============================================================
        val systemMessageRaw = """
Você é um assistente especializado nos locais do campus UECE – Campus Itaperi.

Use SEMPRE o horário oficial do Brasil (Horário de Brasília).
Agora é $diaSemanaPt e o horário atual é $horaAtual.
Caso o usuário não diga horário, use exatamente este: $horaAtual.

Funções:
1. Identificar corretamente o local citado.
2. Interpretar horários.
3. Responder apenas em texto natural.
4. Informar se está aberto ou fechado.
5. Fornecer telefone correto.
6. Avisar se o local não existe.

LOCAIS + HORÁRIOS + TELEFONES:

Biblioteca Central – (85) 3101-9892
Seg–Sex: 08h–21h | Sáb: 08h–14h | Dom fechado

Reitoria – (85) 3101-9600
Seg–Sex: 08h–17h | Sáb–Dom fechado

Restaurante Universitário (RU) – (85) 3101-9885
Almoço 11–14h | Jantar 17–19h | Seg–Sex

Centro de Humanidades (CH) – (85) 3101-9791
Seg–Sex 07h30–22h | Sáb 08–17h | Dom fechado

Centro de Ciências da Saúde (CCS) – (85) 3101-9642
Seg–Sex 08h–18h | Sáb–Dom fechado

Centro de Ciências e Tecnologia (CCT) – (85) 3101-9640
Seg–Sex 08h–18h | Sáb–Dom fechado

Centro de Ciências Agrárias (CCA) – (85) 3101-9650
Seg–Sex 08h–17h | Sáb–Dom fechado

Departamento de Línguas Estrangeiras (DLLE) – (85) 3101-9715
Seg–Sex 08h–21h | Sáb 08–12h | Dom fechado

Coordenação de Computação – (85) 3101-9855
Seg–Sex 08h–17h | Sáb–Dom fechado

Regra final: nunca use JSON, nunca use listas. Apenas texto natural.
        """.trimIndent()

        // Escapar para JSON
        val systemMessage = systemMessageRaw
            .replace("\n", " ")
            .replace("\"", "\\\"")

        // ============================================================
        //  MONTAR A LISTA DE MENSAGENS
        // ============================================================
        val jsonMessages = buildString {
            append("[")
            append("""{"role": "system", "content": "$systemMessage"}""")

            if (mensagens.isNotEmpty()) append(",")

            mensagens.forEachIndexed { i, (role, content) ->
                val escaped = content.replace("\"", "\\\"")
                append("""{"role": "$role", "content": "$escaped"}""")
                if (i < mensagens.size - 1) append(",")
            }
            append("]")
        }

        val jsonBody = """
        {
            "model": "llama-3.1-8b-instant",
            "messages": $jsonMessages
        }
        """.trimIndent()

        // ============================================================
        //  FAZER REQUISIÇÃO
        // ============================================================
        return try {
            val response: HttpResponse = client.post(
                "https://api.groq.com/openai/v1/chat/completions"
            ) {
                headers {
                    append(HttpHeaders.Authorization, "Bearer $apiKey")
                    append(HttpHeaders.ContentType, "application/json")
                }
                setBody(TextContent(jsonBody, ContentType.Application.Json))
            }

            val raw = response.bodyAsText()
            println("RAW RESPONSE >>> $raw")

            val json = Json.parseToJsonElement(raw).jsonObject
            val content = json["choices"]
                ?.jsonArray?.get(0)
                ?.jsonObject?.get("message")
                ?.jsonObject?.get("content")
                ?.jsonPrimitive?.content

            if (!content.isNullOrBlank()) {
                mensagens.add("assistant" to content)
                return content
            }

            "Erro: resposta vazia"

        } catch (e: Exception) {
            e.printStackTrace()
            "Erro ao chamar a API"
        }
    }

    fun limparHistorico() {
        mensagens.clear()
    }
}

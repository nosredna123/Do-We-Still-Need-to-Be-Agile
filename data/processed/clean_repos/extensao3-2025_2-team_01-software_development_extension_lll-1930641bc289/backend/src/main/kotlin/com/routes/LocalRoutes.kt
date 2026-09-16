package com.sergio.chatbot.routes

import com.models.Local
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import io.ktor.http.*
import io.ktor.server.application.*
import io.ktor.server.response.*
import io.ktor.server.routing.*

fun Route.localRoutes() {

    val locais = listOf(
        Local(1, "Biblioteca Central", "biblioteca", "Aberta", -3.7765, -38.5772, "08:00 - 20:00"),
        Local(2, "Bloco F", "bloco", "Fechado para manutenção", -3.7750, -38.5780, null),
        Local(3, "Restaurante Universitário", "RU", "Aberto", -3.7768, -38.5765, "11:00 - 14:00"),
        Local(4, "Centro Acadêmico de História", "centro_academico", "Aberto", -3.7762, -38.5775, "09:00 - 17:00")
    )

    // Rota: /locais?nome=X&tipo=Y
    get("/locais") {
        val nome = call.request.queryParameters["nome"]
        val tipo = call.request.queryParameters["tipo"]

        val resultado = locais.filter {
            (nome == null || it.nome.contains(nome, ignoreCase = true)) &&
            (tipo == null || it.tipo.equals(tipo, ignoreCase = true))
        }

        call.respondText(
            Json.encodeToString(resultado),
            ContentType.Application.Json
        )
    }

    // Rota: /local/{nome}
    get("/local/{nome}") {
        val nome = call.parameters["nome"]
        val local = locais.find { it.nome.equals(nome, ignoreCase = true) }

        if (local != null) {
            call.respond(local)
        } else {
            call.respondText("Local não encontrado", status = HttpStatusCode.NotFound)
        }
    }
}

package com.sergio.chatbot

import io.ktor.server.http.content.*
import io.ktor.server.plugins.cors.routing.*
import io.ktor.http.*
import io.ktor.server.application.*
import io.ktor.server.engine.*
import io.ktor.server.netty.*
import io.ktor.server.plugins.contentnegotiation.*
import io.ktor.serialization.kotlinx.json.*
import io.ktor.server.response.*
import io.ktor.server.routing.*
import kotlinx.serialization.builtins.ListSerializer
import kotlinx.serialization.json.Json
import com.models.Local
import com.sergio.chatbot.routes.localRoutes
import com.sergio.chatbot.routes.chatRoutes


fun main() {
    embeddedServer(Netty, port = 8080) {
        module()
    }.start(wait = true)
}

fun Application.module() {
    install(ContentNegotiation) {
        json(
            Json {
                prettyPrint = true
                isLenient = true
            }
        )
    }

    install(CORS) {
        anyHost() // permite qualquer origem (para testes)
        allowHeader(HttpHeaders.ContentType)
        allowHeader(HttpHeaders.Authorization)
        allowHeader(HttpHeaders.AccessControlAllowOrigin)
        allowMethod(HttpMethod.Options)
        allowMethod(HttpMethod.Get)
        allowMethod(HttpMethod.Post)
        allowMethod(HttpMethod.Put)
        allowMethod(HttpMethod.Delete)
        allowMethod(HttpMethod.Patch)
        allowCredentials = true
        allowNonSimpleContentTypes = true
    }

    routing {
        static {
            resources("static")
            defaultResource("static/index.html")
        }
        
        localRoutes() // rota /locais
        chatRoutes()
        
        get("/") {
            call.respondText("Servidor Ktor rodando com sucesso!")
        }
    }
}


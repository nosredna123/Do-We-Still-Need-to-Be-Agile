package com.sergio.chatbot.services

import com.models.Local
import kotlinx.serialization.decodeFromString
import kotlinx.serialization.json.Json

object LocalService {

    init {
        println("🔍 Carregando locais.json...")
    }

    private val json = Json { ignoreUnknownKeys = true }

    val locais: List<Local> by lazy {
        val file = this::class.java.classLoader
            .getResource("locais.json")
            ?: throw RuntimeException("Arquivo locais.json não encontrado")

        val conteudo = file.readText()
        json.decodeFromString(conteudo)
    }

    fun buscarLocalPorNome(pergunta: String): Local? {
        return locais.firstOrNull { local ->
            pergunta.lowercase().contains(local.nome.lowercase())
        }
    }
}


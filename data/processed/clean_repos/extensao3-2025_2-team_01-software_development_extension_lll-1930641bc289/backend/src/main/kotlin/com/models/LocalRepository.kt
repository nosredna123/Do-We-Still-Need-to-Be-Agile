package com.models

import com.fasterxml.jackson.module.kotlin.readValue
import com.fasterxml.jackson.module.kotlin.jacksonObjectMapper
import java.io.File

object LocalRepository {

    private val mapper = jacksonObjectMapper()
    val locais: List<Local>

    init {
        println("🔍 Carregando locais.json...")

        val file = File("src/main/resources/locais.json")
        locais = mapper.readValue(file)

        println("✅ locais.json carregado! Total: ${locais.size}")
    }
}

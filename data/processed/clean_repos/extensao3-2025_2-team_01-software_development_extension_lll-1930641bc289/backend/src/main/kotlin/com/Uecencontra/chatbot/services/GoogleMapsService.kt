package com.sergio.chatbot.services

import io.ktor.client.*
import io.ktor.client.call.*
import io.ktor.client.engine.cio.*
import io.ktor.client.request.*
import kotlinx.serialization.json.*
import java.net.URLEncoder

data class Localizacao(val lat: Double, val lng: Double)

object GoogleMapsService {
    private val apiKey = ""
    private val client = HttpClient(CIO)

    suspend fun buscarCoordenadas(destino: String): Localizacao? {
    val url = "https://maps.googleapis.com/maps/api/place/textsearch/json?query=" +
        URLEncoder.encode(destino, "UTF-8") + "&key=$apiKey"

    val response: String = client.get(url).body()

    println("Buscando coordenadas para: $destino")
    println("URL: $url")
    println("Resposta da API: $response")

    val json = Json.parseToJsonElement(response).jsonObject
    val resultado = json["results"]?.jsonArray?.firstOrNull()?.jsonObject ?: return null

    val lat = resultado["geometry"]?.jsonObject
        ?.get("location")?.jsonObject?.get("lat")?.jsonPrimitive?.doubleOrNull
    val lng = resultado["geometry"]?.jsonObject
        ?.get("location")?.jsonObject?.get("lng")?.jsonPrimitive?.doubleOrNull

    return if (lat != null && lng != null) Localizacao(lat, lng) else null
}


    suspend fun buscarDescricaoDoLugar(destino: String): String? {
    val url = "https://maps.googleapis.com/maps/api/place/textsearch/json?query=" +
        URLEncoder.encode(destino, "UTF-8") + "&key=$apiKey"

    val response: String = client.get(url).body()
    
    val json = Json.parseToJsonElement(response).jsonObject

    val status = json["status"]?.jsonPrimitive?.contentOrNull
    if (status != "OK") {
        println("Erro da API do Google Maps: $status")
        return null
    }

    val resultado = json["results"]?.jsonArray?.firstOrNull()?.jsonObject ?: return null






    val nome = resultado["name"]?.jsonPrimitive?.contentOrNull
    val endereco = resultado["formatted_address"]?.jsonPrimitive?.contentOrNull

    return if (nome != null && endereco != null) "$nome fica em: $endereco" else null
}






}

package com.models


import kotlinx.serialization.Serializable

@Serializable
data class Local(
    val id: Int,
    val nome: String,
    val tipo: String,
    val descricao: String,
    val latitude: Double,
    val longitude: Double,
    val telefone: String? = null,
    val horarioFuncionamento: String? = null
)

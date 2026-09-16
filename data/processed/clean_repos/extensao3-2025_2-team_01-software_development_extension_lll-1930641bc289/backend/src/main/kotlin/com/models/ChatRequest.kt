package com.models

import kotlinx.serialization.Serializable

@Serializable
data class ChatRequest(
    val mensagem: String
)


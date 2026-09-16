import os
from dotenv import load_dotenv
from app.service.llm.hf import * 
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama


load_dotenv()


def get_llm(provider: str | None = None, model: str | None = None):
    
    lista_providers = ["openai", "gemini", "ollama"]
    if provider == "openai":
        return ChatOpenAI(
            model=model or os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0,
        )

    if provider == "gemini":
        return ChatGoogleGenerativeAI(
            model=model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite"),
            google_api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0,
        )

    if provider == "ollama":
        return ChatOllama(
            model=model or os.getenv("OLLAMA_MODEL", "llama3.1"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            temperature=0,
        )
    if provider == "hugging face":
        return build_hf_model(
            model_name=model or os.getenv("HF_MODEL"),
            backend="local",
            task="text-generation",
            max_new_tokens=1000,
            temperature=0.7, 
            do_sample=True,
            huggingface_api_token=os.getenv("HUGGINGFACE_API_TOKEN")
        )
        
        

    raise ValueError(f"o provedorque voce forneceu nao é suportado suportado: {provider} , escolha entre {lista_providers}")
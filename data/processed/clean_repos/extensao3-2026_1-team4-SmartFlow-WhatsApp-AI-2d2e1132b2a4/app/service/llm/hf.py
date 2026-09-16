from __future__ import annotations

from typing import Literal, Optional

import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    pipeline,
)

from langchain_huggingface import HuggingFacePipeline, ChatHuggingFace, HuggingFaceEndpoint


def build_hf_model(
    model_name: str,
    backend: Literal["local", "endpoint"] = "local",
    task: str = "text-generation",
    max_new_tokens: int = 256,
    temperature: float = 0.7,
    do_sample: bool = True,
    huggingface_api_token: Optional[str] = None,
):
    if backend == "local":
        tokenizer = AutoTokenizer.from_pretrained(model_name)

        if tokenizer.pad_token is None and tokenizer.eos_token is not None:
            tokenizer.pad_token = tokenizer.eos_token 
          
        if torch.cuda.is_available():
            device_map = "auto"
            torch_dtype = torch.float16
        else:
            device_map = None
            torch_dtype = torch.float32

        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch_dtype,
            device_map=device_map,
        )

        text_pipe = pipeline(
            task=task,
            model=model,
            tokenizer=tokenizer,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            do_sample=do_sample,
            pad_token_id=tokenizer.pad_token_id,
        )

        llm = HuggingFacePipeline(pipeline=text_pipe)
        return ChatHuggingFace(llm=llm)

    if backend == "endpoint":
        if not huggingface_api_token:
            raise ValueError(
                "Para backend='endpoint', informe huggingface_api_token."
            )

        llm = HuggingFaceEndpoint(
            repo_id=model_name,
            huggingfacehub_api_token=huggingface_api_token,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            task=task,
        )

        return ChatHuggingFace(llm=llm)

    raise ValueError("backend deve ser 'local' ou 'endpoint'")
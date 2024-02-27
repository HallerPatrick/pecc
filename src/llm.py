from typing import Dict, Optional

from langchain.chat_models import ChatOpenAI, ChatLiteLLM
from langchain.llms.fake import FakeListLLM
from langchain import HuggingFaceHub, HuggingFacePipeline
from langchain.llms import VLLMOpenAI


class LLMLoader:

    @staticmethod
    def chat_lite(model_name):
        return ChatLiteLLM(model=model_name)

    @staticmethod
    def dummy_llm():
        return FakeListLLM(responses=["print(15)\n", "15", "print(17)\n", "17"])

    @staticmethod
    def load_hf():
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
        except ImportError:
            raise ImportError(
                "Please install the transformers package with `pip install transformers` for local inference")
        model = AutoModelForCausalLM.from_pretrained("gpt2")
        tokenizer = AutoTokenizer.from_pretrained("gpt2")
        pipe = pipeline("text-generation", model=model,
                        tokenizer=tokenizer, max_length=1000)
        return HuggingFacePipeline(pipeline=pipe)

    @staticmethod
    def load_hf_inference_model(model_name: str = "WizardLM/WizardCoder-Python-34B-V1.0", model_kwargs: Optional[Dict] = None):
        # "Phind/Phind-CodeLlama-34B-v2"
        return HuggingFaceHub(repo_id=model_name, model_kwargs=model_kwargs)

    @staticmethod
    def open_ai(openai_model: str):
        return ChatOpenAI(model=openai_model)

    @staticmethod
    def vllm(model: str = "WizardLM/WizardCoder-Python-34B-V1.0"):
        return VLLMOpenAI(
            openai_api_key="EMPTY",
            openai_api_base="https://opiniongpt.informatik.hu-berlin.de/custom_api/v1",
            model_name=model,
            max_tokens=2048,
            model_kwargs={"max_length": 2048}
        )


MODEL_LOADER_MAP = {
    "gpt-3.5-turbo-16k": LLMLoader.open_ai,
    "gpt-3.5-turbo-turbo": LLMLoader.open_ai,
    "vertex_ai/chat-bison": LLMLoader.chat_lite,
    "vertex_ai/codechat-bison": LLMLoader.chat_lite,
    "WizardLM/WizardCoder-Python-34B-V1.0": LLMLoader.vllm,
    "Mistral-Instruct": LLMLoader.vllm,
}

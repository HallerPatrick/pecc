from typing import Dict, Optional
from functools import partial

from langchain.llms.fake import FakeListLLM
from langchain_community.chat_models import ChatOpenAI, ChatLiteLLM
from langchain_community.llms import VLLMOpenAI, HuggingFaceHub, HuggingFacePipeline

# from google.cloud.aiplatform_v1beta1.types import gapic_content_types


class LLMLoader:

    @staticmethod
    def chat_lite(model_name):
        llm = ChatLiteLLM(
            model=model_name,
            # model_kwargs={"safety_settings": [
            #     {gapic_content_types.ContentType.TEXT: gapic_content_types.SafetySettings.SAFE_FOR_CHILDREN},
            #
            # ]}
        )

        llm.max_tokens = 4096
        return llm

    @staticmethod
    def dummy_llm():
        return FakeListLLM(responses=["print(15)\n", "15", "print(17)\n", "17"])

    @staticmethod
    def load_hf():
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
        except ImportError:
            raise ImportError(
                "Please install the transformers package with `pip install transformers` for local inference"
            )
        model = AutoModelForCausalLM.from_pretrained("gpt2")
        tokenizer = AutoTokenizer.from_pretrained("gpt2")
        pipe = pipeline(
            "text-generation", model=model, tokenizer=tokenizer, max_length=1000
        )
        return HuggingFacePipeline(pipeline=pipe)

    @staticmethod
    def load_hf_inference_model(
        model_name: str = "WizardLM/WizardCoder-Python-34B-V1.0",
        model_kwargs: Optional[Dict] = None,
    ):
        # "Phind/Phind-CodeLlama-34B-v2"
        return HuggingFaceHub(repo_id=model_name, model_kwargs=model_kwargs)

    @staticmethod
    def open_ai(openai_model: str):
        return ChatOpenAI(model=openai_model)

    @staticmethod
    def vllm_custom(model: str = "WizardLM/WizardCoder-Python-34B-V1.0"):
        return VLLMOpenAI(
            openai_api_key="EMPTY",
            openai_api_base="https://opiniongpt.informatik.hu-berlin.de/custom_api/v1",
            model_name=model,
            max_tokens=2048,
            model_kwargs={"max_length": 2048},
        )


MODEL_LOADER_MAP = {
    "gpt-3.5-turbo-16k": partial(LLMLoader.open_ai, "gpt-3.5-turbo-16k"),
    "gpt-3.5-turbo-turbo": partial(LLMLoader.open_ai, "gpt-3.5-turbo-turbo"),
    "vertex_ai/chat-bison": partial(LLMLoader.chat_lite, "vertex_ai/chat-bison"),
    "vertex_ai/codechat-bison": partial(
        LLMLoader.chat_lite, "vertex_ai/codechat-bison"
    ),
    "vertex_ai/gemini-pro": partial(LLMLoader.chat_lite, "vertex_ai/gemini-pro"),
    "vertex_ai/gemini-1.5-pro": partial(
        LLMLoader.chat_lite, "vertex_ai/gemini-1.5-pro"
    ),
    "WizardCoder-34B": partial(
        LLMLoader.vllm_custom, model="WizardLM/WizardCoder-Python-34B-V1.0"
    ),
    # "Mistral-Instruct": LLMLoader.vllm,
    "mixtral": partial(
        LLMLoader.chat_lite, "replicate/mistralai/mixtral-8x7b-instruct-v0.1"
    ),
    "claude-3-opus": partial(LLMLoader.chat_lite, "anthropic/claude-3-opus-20240229"),
    "claude-3-sonnet": partial(
        LLMLoader.chat_lite, "anthropic/claude-3-sonnet-20240229"
    ),
    "claude-3-haiku": partial(LLMLoader.chat_lite, "anthropic/claude-3-haiku-20240307"),
}

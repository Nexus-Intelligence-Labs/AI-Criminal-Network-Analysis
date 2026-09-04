import json
import os

import torch
from transformers import AutoModelForMultimodalLM, AutoProcessor


class GemmaClient:

    MODEL_ID = "google/gemma-4-12B-it"

    def __init__(self, model_id=None):

        self.model_id = model_id or os.getenv(
            "GEMMA_MODEL_ID",
            self.MODEL_ID
        )

        self.processor = None
        self.model = None

    def load_model(self):

        if self.model is not None:
            return

        self.processor = AutoProcessor.from_pretrained(
            self.model_id
        )

        self.model = AutoModelForMultimodalLM.from_pretrained(
            self.model_id,
            dtype="auto",
            device_map="auto"
        )

    def generate(
        self,
        prompt: str,
        max_new_tokens: int = 512
    ):

        if not isinstance(prompt, str):
            raise TypeError("prompt must be a string")

        if not prompt.strip():
            raise ValueError("prompt cannot be empty")

        self.load_model()

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an investigative information extraction "
                    "assistant. Extract only information supported by "
                    "the supplied source text. Never invent evidence."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        inputs = self.processor.apply_chat_template(
            messages,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
            add_generation_prompt=True,
            enable_thinking=False
        ).to(self.model.device)

        input_len = inputs["input_ids"].shape[-1]

        with torch.inference_mode():

            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens
            )

        response = self.processor.decode(
            outputs[0][input_len:],
            skip_special_tokens=False
        )

        return self.processor.parse_response(response)
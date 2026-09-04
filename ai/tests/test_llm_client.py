from models.llm_client import GemmaClient


def test_gemma_client_configuration():

    client = GemmaClient()

    assert client.model_id == "google/gemma-4-12B-it"
    assert client.model is None
    assert client.processor is None


def test_custom_model_configuration():

    client = GemmaClient(
        model_id="test-model"
    )

    assert client.model_id == "test-model"


def test_model_is_lazy_loaded():

    client = GemmaClient()

    assert client.model is None
    assert client.processor is None
import sys
from unittest.mock import MagicMock

import pytest
import pytorch_lightning as pl
from transformers import AutoTokenizer

from lightning_transformers.task.nlp.translation import (
    TranslationConfig,
    TranslationDataConfig,
    TranslationDataModule,
    TranslationTransformer,
    WMT16TranslationDataModule,
)


@pytest.mark.skipif(sys.platform == "win32", reason="Currently Windows is not supported")
def test_smoke_train(hf_cache_path):
    tokenizer = AutoTokenizer.from_pretrained(pretrained_model_name_or_path="patrickvonplaten/t5-tiny-random")
    model = TranslationTransformer(pretrained_model_name_or_path="patrickvonplaten/t5-tiny-random")
    dm = WMT16TranslationDataModule(
        cfg=TranslationDataConfig(
            batch_size=1,
            dataset_name="wmt16",
            dataset_config_name="ro-en",
            source_language="en",
            target_language="ro",
            cache_dir=hf_cache_path,
            limit_train_samples=16,
            limit_val_samples=16,
            limit_test_samples=16,
            max_source_length=32,
            max_target_length=32,
        ),
        tokenizer=tokenizer,
    )
    trainer = pl.Trainer(fast_dev_run=True)

    trainer.fit(model, dm)


@pytest.mark.skipif(sys.platform == "win32", reason="Currently Windows is not supported")
def test_smoke_predict():
    model = TranslationTransformer(
        pretrained_model_name_or_path="patrickvonplaten/t5-tiny-random",
        tokenizer=AutoTokenizer.from_pretrained(pretrained_model_name_or_path="patrickvonplaten/t5-tiny-random"),
    )
    y = model.hf_predict("¡Hola Sean!")
    assert len(y) == 1
    assert isinstance(y[0]["translation_text"], str)


def test_model_has_correct_cfg():
    model = TranslationTransformer(pretrained_model_name_or_path="patrickvonplaten/t5-tiny-random")
    assert model.hparams.downstream_model_type == "transformers.AutoModelForSeq2SeqLM"
    assert type(model.cfg) is TranslationConfig


def test_datamodule_has_correct_cfg():
    tokenizer = MagicMock()
    dm = TranslationDataModule(tokenizer)
    assert isinstance(dm.cfg, TranslationDataConfig)
    assert dm.tokenizer is tokenizer

"""Translation stage using local IndicTrans2."""

from pathlib import Path

import torch
from IndicTransToolkit import IndicProcessor
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer


MODEL_NAME = "ai4bharat/indictrans2-indic-indic-1B"
SRC_LANG = "kan_Knda"
TGT_LANG = "hin_Deva"

_TOKENIZER = None
_MODEL = None
_PROCESSOR = None
_DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


def _load_components():
    global _TOKENIZER, _MODEL, _PROCESSOR

    if _TOKENIZER is None:
        _TOKENIZER = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    if _MODEL is None:
        _MODEL = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME, trust_remote_code=True).to(_DEVICE)
    if _PROCESSOR is None:
        _PROCESSOR = IndicProcessor(inference=True)

    return _TOKENIZER, _MODEL, _PROCESSOR


def translate_kn_hi(in_txt_path, out_txt_path):
    """Translate Kannada text file to Hindi and write outputs/<run_id>/hindi.txt."""
    text = Path(str(in_txt_path)).read_text(encoding="utf-8").strip()
    if not text:
        translated = ""
    else:
        tokenizer, model, processor = _load_components()
        preprocessed = processor.preprocess_batch([text], src_lang=SRC_LANG, tgt_lang=TGT_LANG)
        inputs = tokenizer(
            preprocessed,
            padding=True,
            truncation=True,
            max_length=1024,
            return_tensors="pt",
        ).to(_DEVICE)
        with torch.no_grad():
            generated = model.generate(**inputs, max_length=1024)
        decoded = tokenizer.batch_decode(generated, skip_special_tokens=True)
        translated = processor.postprocess_batch(decoded, lang=TGT_LANG)[0].strip()

    run_id = Path(str(out_txt_path)).parent.name
    hindi_path = Path("outputs") / run_id / "hindi.txt"
    hindi_path.parent.mkdir(parents=True, exist_ok=True)
    hindi_path.write_text(translated, encoding="utf-8")
    return hindi_path

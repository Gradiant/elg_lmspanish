from transformers import (
    AutoTokenizer,
    pipeline,
    AutoConfig,
    FillMaskPipeline,
    AutoModelForQuestionAnswering,
)


class Initializer:
    def __init__(self):

        tokenizer = AutoTokenizer.from_pretrained("PlanTL-GOB-ES/roberta-base-bne-sqac")
        model = AutoModelForQuestionAnswering.from_pretrained(
            "PlanTL-GOB-ES/roberta-base-bne-sqac"
        )
        config = AutoConfig.from_pretrained("PlanTL-GOB-ES/roberta-base-bne-sqac")
        pipeline_obj = pipeline("question-answering", model=model, tokenizer=tokenizer)

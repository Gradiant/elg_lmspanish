from flask import Flask, request
from flask_json import FlaskJSON, JsonError, as_json
from transformers import (
    AutoTokenizer,
    pipeline,
    AutoConfig,
    FillMaskPipeline,
    AutoModelForQuestionAnswering,
)

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
APP_ROOT = "./"
app.config["APPLICATION_ROOT"] = APP_ROOT
app.config["UPLOAD_FOLDER"] = "files/"

json_app = FlaskJSON(app)

# Downloading model from huggingface
tokenizer = AutoTokenizer.from_pretrained("PlanTL-GOB-ES/roberta-base-bne-sqac")
model = AutoModelForQuestionAnswering.from_pretrained(
    "PlanTL-GOB-ES/roberta-base-bne-sqac"
)
config = AutoConfig.from_pretrained("PlanTL-GOB-ES/roberta-base-bne-sqac")

pipeline = pipeline("question-answering", model=model, tokenizer=tokenizer)


def prepare_output_format(answer):
    response = {
        "type": "annotations",
        "annotations": {
            "answers": [
                {
                    "start": answer["start"],
                    "end": answer["end"],
                    "features": {"answer": answer["answer"], "score": answer["score"]},
                }
            ]
        },
    }

    return {"response": response}


@as_json
@app.route("/process", methods=["POST"])
def run_lmspanish():
    data = request.get_json()
    if (
        (data.get("type") != "structuredText")
        or (data is None)
        or ("texts" not in data)
    ):
        output = invalid_request_error(None)
        return output
    context = data.get("texts")[0].get("content")
    question = data.get("texts")[1].get("content")
    if question.find("?") == -1:
        return generate_failure_response(
            status=404,
            code="elg.service.internalError",
            text=None,
            params=None,
            detail="No question on input or incorrect order",
        )

    try:
        output = pipeline(question=question, context=context)  # json with the response
    except Exception as e:
        return generate_failure_response(
            status=404,
            code="elg.service.internalError",
            text=None,
            params=None,
            detail=str(e),
        )
    return prepare_output_format(output)


@json_app.invalid_json_error
def invalid_request_error(e):
    """Generates a valid ELG "failure" response if the request cannot be parsed"""
    raise JsonError(
        status_=400,
        failure={
            "errors": [
                {"code": "elg.request.invalid", "text": "Invalid request message"}
            ]
        },
    )


@json_app.invalid_json_error
def generate_failure_response(status, code, text, params, detail):
    """Generate a wrong response indicating the failure

    :param status: api error code
    :param code: ELG error type
    :param text: not used
    :param params: not used
    :param detail: detail of the exception

    """

    error = {}
    if code:
        error["code"] = code
    if text:
        error["text"] = text
    if params:
        error["params"] = params
    if detail:
        error["detail"] = {"message": detail}

    raise JsonError(status_=status, failure={"errors": [error]})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8866)

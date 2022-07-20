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
app.config["JSON_ADD_STATUS"] = False
app.config["JSON_SORT_KEYS"] = False

json_app = FlaskJSON(app)

# Downloading model from huggingface
tokenizer = AutoTokenizer.from_pretrained("PlanTL-GOB-ES/roberta-base-bne-sqac")
model = AutoModelForQuestionAnswering.from_pretrained(
    "PlanTL-GOB-ES/roberta-base-bne-sqac"
)
config = AutoConfig.from_pretrained("PlanTL-GOB-ES/roberta-base-bne-sqac")

pipeline = pipeline("question-answering", model=model, tokenizer=tokenizer)

def generate_successful_text_response(answer):
    response = {"type": "texts", "texts": [{"content": answer}]}
    output = {"response": response}
    return output

@as_json
@app.route("/process", methods=["POST"])
def run_lmspanish():
    data = request.get_json()
    if data["type"] != "text":
        # Standard message code for unsupported response type
        return generate_failure_response(
            status=400,
            code="elg.request.type.unsupported",
            text="Request type {0} not supported by this service",
            params=[data["type"]],
            detail=None,
        )

    if "content" not in data:
        return invalid_request_error(
            None,
        )

    content = data.get("content")
    params = data.get("params", {})
    if "question" not in params:
    # Standard message code for missing parameter
        return generate_failure_response(
            status=400,
            code="elg.request.parameter.missing",
            text="Required parameter {0} missing from request",
            params=["question"],
            detail=None,
        )

    context = content
    question = params["question"]

    try:
        answer = pipeline(question=question, context=context)  # json with the response
        print(answer)
        output = generate_successful_text_response(answer["answer"])
        return output
    except Exception as e:
        text = (
            "Unexpected error. If your input text is too long, this may be the cause."
        )
        # Standard message for internal error - the real error message goes in params
        return generate_failure_response(
            status=500,
            code="elg.service.internalError",
            text="Internal error during processing: {0}",
            params=[text],
            detail=e.__str__(),
        )


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

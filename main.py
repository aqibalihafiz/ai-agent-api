
from fastapi import FastAPI
from pydantic import BaseModel
import anthropic
import os

app = FastAPI()

client = anthropic.Anthropic(
    api_key=os.environ["ANTHROPIC_API_KEY"]
)


# -------------------------
# Request model
# -------------------------

class Question(BaseModel):
    question: str


# -------------------------
# Tools
# -------------------------

def add(a, b):
    return a + b


def multiply(a, b):
    return a * b


def get_name():
    return "Aaqib"


available_tools = {
    "add": add,
    "multiply": multiply,
    "get_name": get_name
}


# -------------------------
# Tool schemas
# -------------------------

tools = [
    {
        "name": "add",
        "description": "Add two numbers together.",
        "input_schema": {
            "type": "object",
            "properties": {
                "a": {"type": "number"},
                "b": {"type": "number"}
            },
            "required": ["a", "b"]
        }
    },
    {
        "name": "multiply",
        "description": "Multiply two numbers together.",
        "input_schema": {
            "type": "object",
            "properties": {
                "a": {"type": "number"},
                "b": {"type": "number"}
            },
            "required": ["a", "b"]
        }
    },
    {
        "name": "get_name",
        "description": "Get the user's name.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
]


# -------------------------
# Home
# -------------------------

@app.get("/")
def home():
    return {
        "message": "AI Agent API is working!"
    }


# -------------------------
# Normal AI endpoint
# -------------------------

@app.post("/ask")
def ask_question(data: Question):

    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=200,
        messages=[
            {
                "role": "user",
                "content": data.question
            }
        ]
    )

    return {
        "answer": response.content[0].text
    }


# -------------------------
# AI Agent endpoint
# -------------------------

@app.post("/agent")
def agent(data: Question):

    messages = [
        {
            "role": "user",
            "content": data.question
        }
    ]

    while True:

        response = client.messages.create(
            model="claude-sonnet-5",
            max_tokens=300,
            tools=tools,
            messages=messages
        )

        messages.append({
            "role": "assistant",
            "content": response.content
        })

        tool_results = []

        for block in response.content:

            if block.type == "tool_use":

                tool_function = available_tools[block.name]

                result = tool_function(**block.input)

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": str(result)
                })

        if not tool_results:
            break

        messages.append({
            "role": "user",
            "content": tool_results
        })

    final_text = ""

    for block in response.content:

        if block.type == "text":
            final_text += block.text

    return {
        "answer": final_text
    }

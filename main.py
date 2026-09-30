
from fastapi import FastApi
from pydantic import BaseModel
import anthropic
import os

app = FastApi()

client = anthropic.Anthropic(
  api_key = os.environ["ANTHROPIC_API_KEY"])

class Question(BaseModel):
  question:str

@app.get("/")
def home():
  return {"message":"AI API IS WORKING"}

@app.post("/ask")
def ask_question(data : Question):

  response = client.message.create(
      model = "claude-sonnet-5",
      max_tokens = 200,
      messages[
      {"role":"user","content":data.question}
      ])
  return{
      "answer":response.content[0].text
      }    
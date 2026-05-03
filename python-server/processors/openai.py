# processors/openai.py
# import os
# from openai import OpenAI
# from pydantic import BaseModel
# from typing import Dict, List, Literal

# # 1. Initialize with OpenRouter details
# client = OpenAI(
#     base_url="https://openrouter.ai/api/v1",
# )

# class QuestionOutput(BaseModel):
#     questionNumber: int
#     type: Literal["MCQ", "MSQ", "NAT"]
#     questionText: str
#     options: Dict[str, str]
#     answer: str
#     marks: int
#     difficulty: Literal["easy", "medium", "hard"]
#     subject: str
#     topic: str
#     tags: List[str]
#     explanation: str

# async def change_parse_text_to_JSON(parseText):
#     system_prompt = (
#         "You are an expert data cleaner. Extract exam questions from the provided OCR text. "
#         "1. Ignore headers, footers, and brand info. "
#         "2. Identify the 'type' (MCQ, MSQ, or NAT). "
#         "3. Map the 'subject' and 'topic' strictly to the official GATE syllabus. "
#         "4. Generate relevant tags. "
#         "5. Rewrite the explanation to be clear and instructional. "
#         "6. Return ONLY valid structured JSON."
#     )

#     # 2. Use the OpenRouter model string
#     # For Gemma 4, use the specific OpenRouter path
#     response = client.beta.chat.completions.parse(
#         model="nvidia/nemotron-3-super-120b-a12b:free", 
#         messages=[
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": parseText}
#         ],
#         response_format=QuestionOutput, # Forces the model to follow your Pydantic schema
#         extra_headers={
#             "HTTP-Referer": "http://localhost:3000", # Required by some OpenRouter models
#             "X-Title": "GATE Question Parser",
#         },
#         temperature=0
#     )

#     # 3. Access the parsed object directly
#     structured_data = response.choices[0].message.parsed
#     print(structured_data.model_dump_json(indent=2))
    
#     return structured_data




from openai import OpenAI
from pydantic import BaseModel
from typing import Dict, List, Literal
import json
import asyncio

# Connect OpenAI SDK to Ollama local server
client = OpenAI(
    base_url="http://192.168.1.41:11434/v1",
    api_key="not-needed"
)

class QuestionOutput(BaseModel):
    questionNumber: int
    type: Literal["MCQ", "MSQ", "NAT"]
    questionText: str
    options: Dict[str, str]
    answer: str
    marks: int
    difficulty: Literal["easy", "medium", "hard"]
    subject: str
    topic: str
    tags: List[str]
    explanation: str


async def change_parse_text_to_JSON(parseText):
    system_prompt = """
You are an expert data cleaner.

Extract exam questions from the provided OCR text.

Rules:
1. Ignore headers, footers, logos, addresses, emails, institute names.
2.only top 10 questions
3. Identify type as MCQ, MSQ, or NAT.

4. Map subject/topic to official GATE syllabus.
5. Generate useful tags.
6. Rewrite explanation clearly.
7. Return ONLY valid JSON matching this schema:

output:${QuestionOutput}
"""

    response = client.beta.chat.completions.parse(
        model="gemma4:e2b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": parseText}
        ],
        temperature=0,
        response_format=QuestionOutput # The SDK converts the Pydantic model to JSON Schema
    )
    try:
        # Access the parsed object directly
        validated = response.choices[0].message.parsed
        
        if response.choices[0].message.refusal:
            # Handle safety refusals
            print(f"Model refused: {response.choices[0].message.refusal}")
            return None

        print(validated.model_dump_json(indent=2))
        return validated
   
       

    except Exception as e:
        print("Invalid JSON from model:")
        print(raw)
        print("Error:", e)


    print(response.choices[0].message.content)
    return response.choices[0].message.content


import PyPDF2
import openai
import json
import logging
import asyncio
from typing import Dict, List, Any
from datetime import datetime
from transformers import pipeline

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extracts text from a PDF file."""
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    return text

# Extract syllabus text from PDF
syllabus_text = extract_text_from_pdf("CS182_syllabus.pdf")
print("Syllabus Text Preview:", syllabus_text[:200])  # print first 200 characters
async def extract_syllabus_info(syllabus_text: str) -> dict:
    """
    Uses OpenAI's ChatCompletion API to extract the following information:
      - Homework: total points (assumed 100) and its weight
      - Quizzes: total points (assumed 100) and its weight
      - Midterm: total points (assumed 100) and its weight
      - Final Exam: total points (assumed 100) and its weight
    
    The output is formatted as a JSON object with keys:
      {
        "homework": {"points": 100, "weight": "<extracted weight>"},
        "quizzes": {"points": 100, "weight": "<extracted weight>"},
        "midterm": {"points": 100, "weight": "<extracted weight>"},
        "final_exam": {"points": 100, "weight": "<extracted weight>"}
      }
    """
    prompt = f"""
Extract the following information from the syllabus text:
1. Extract total homework points (assume 100 if not specified) and its weight.
2. Extract total quizzes points (assume 100 if not specified) and its weight.
3. For Exams, extract both Midterm and Final Exam:
   - Each is assumed to be out of 100 points (if not specified).
   - Extract the weight for each exam.
Format the output as a JSON object with these keys:
{{
  "homework": {{"points": 100, "weight": "<extracted weight>"}},
  "quizzes": {{"points": 100, "weight": "<extracted weight>"}},
  "midterm": {{"points": 100, "weight": "<extracted weight>"}},
  "final_exam": {{"points": 100, "weight": "<extracted weight>"}}
}}
Only include the requested information.

Syllabus text:
{syllabus_text}
"""

    response = await openai.ChatCompletion.acreate(
        model="gpt-4o",  # Replace with your preferred model, e.g., "gpt-3.5-turbo"
        messages=[
            {"role": "system", "content": "You are a precise syllabus analyzer. Extract and structure information exactly as requested."},
            {"role": "user", "content": prompt}
        ],
        temperature=0,
        max_tokens=1000
    )
    
    result = response.choices[0].message.content
    try:
        data = json.loads(result)
    except Exception as e:
        print("Error parsing JSON:", e)
        print("Raw output:", result)
        data = None
    return data

async def main():
    # Extract text from the PDF file
    syllabus_text = extract_text_from_pdf("CS182_syllabus.pdf")
    # Extract the required syllabus information using OpenAI
    extracted_info = await extract_syllabus_info(syllabus_text)
    print("Extracted Syllabus Information:")
    print(json.dumps(extracted_info, indent=2))

if __name__ == "__main__":
    openai.api_key = "-"  # Replace with your actual API key
    asyncio.run(main())
    
    # make an assitant
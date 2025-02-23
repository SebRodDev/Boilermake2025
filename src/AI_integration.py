import PyPDF2
import openai
from openai import OpenAI
import json
import logging
from datetime import datetime
import time

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extracts text from a PDF file."""
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    return text

def extract_syllabus_info(client, assistant_id: str, syllabus_text: str) -> dict:
    """Uses existing OpenAI Assistant to extract syllabus information."""
    try:
        # Create a thread
        thread = client.beta.threads.create()

        # Add a message to the thread
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=f"""Please analyze this syllabus and extract the following information:

            1. For Homework:
               - Find the total possible points for homework assignments
               - Extract the weight of homework in the final grade
            
            2. For Quizzes:
               - Find the total possible points for quizzes
               - Extract the weight of quizzes in the final grade
            
            3. For the Midterm Exam:
               - Find the total possible points for the midterm
               - Extract the weight of the midterm in the final grade
            
            4. For the Final Exam:
               - Find the total possible points for the final exam
               - Extract the weight of the final exam in the final grade

            Please extract the actual points and weights mentioned in the syllabus. Do not make any assumptions about points being out of 100.
            Format the output as a JSON object with this structure:
            {{
                "homework": {{"points": <actual points>, "weight": <actual weight>}},
                "quizzes": {{"points": <actual points>, "weight": <actual weight>}},
                "midterm": {{"points": <actual points>, "weight": <actual weight>}},
                "final_exam": {{"points": <actual points>, "weight": <actual weight>}}
            }}

            If any information is not found in the syllabus, use null for that value.

            Syllabus text:
            {syllabus_text}"""
        )

        # Run the assistant
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_id
        )

        # Wait for the run to complete
        while True:
            run_status = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            if run_status.status == 'completed':
                break
            elif run_status.status in ['failed', 'cancelled', 'expired']:
                raise Exception(f"Run failed with status: {run_status.status}")
            time.sleep(1)

        # Get the assistant's response
        messages = client.beta.threads.messages.list(
            thread_id=thread.id
        )
        
        # Parse the JSON response
        for msg in messages.data:
            if msg.role == "assistant":
                try:
                    return json.loads(msg.content[0].text.value)
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON: {e}")
                    print(f"Raw response: {msg.content[0].text.value}")
                    return None

    except Exception as e:
        logging.error(f"Error in extract_syllabus_info: {str(e)}")
        return None

def main():
    # Initialize OpenAI client
    client = openai.OpenAI(
        api_key="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"
    )

    try:
        # Use your existing assistant ID here
        assistant_id = "asst_A3u9Hy5W1IFUC7p5SeSU782h"  # Replace with your actual assistant ID //CHANGE THE ASSISTANT TOKEN
        
        # Extract text from the PDF file
        syllabus_text = extract_text_from_pdf("CS182_syllabus.pdf")
        print("Syllabus Text Preview:", syllabus_text[:200])
        
        # Extract the required syllabus information using OpenAI Assistant
        extracted_info = extract_syllabus_info(client, assistant_id, syllabus_text)
        
        if extracted_info:
            print("\nExtracted Syllabus Information:")
            print(json.dumps(extracted_info, indent=2))
            
            # Print any missing information
            for category in ['homework', 'quizzes', 'midterm', 'final_exam']:
                if category in extracted_info:
                    for metric in ['points', 'weight']:
                        if extracted_info[category][metric] is None:
                            print(f"\nWarning: Could not find {metric} for {category} in the syllabus")
        else:
            print("Failed to extract syllabus information.")

    except Exception as e:
        logging.error(f"Error in main: {str(e)}")

if __name__ == "__main__":
    main()
    
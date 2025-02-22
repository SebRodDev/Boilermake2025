import PyPDF2
import openai
import json
import logging
import asyncio
from typing import Dict, List, Any
from datetime import datetime

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file."""
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    return text

syllabus_text = extract_text_from_pdf("CS182_syllabus.pdf")
print(syllabus_text[:500])  # Print first 500 characters

class SyllabusGPTAnalyzer:
    def __init__(self, api_key: str):
        """Initialize the analyzer with OpenAI API key."""
        self.api_key = api_key
        openai.api_key = api_key
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Predefined prompts for different extraction tasks
        self.prompts = {
            'grading': """
            Extract the following information from the syllabus text:
            1. All grading components and their weights
            2. Number of assignments for each component
            3. Drop policies for assignments
            4. Late submission policies
            
            Format the response as a JSON object with these keys:
            {
                "components": [{"name": "string", "weight": float}],
                "assignment_counts": {"component": int},
                "drop_policies": {"component": "policy"},
                "late_policies": "string"
            }
            """,
            'schedule': """
            Extract all important dates and deadlines from the syllabus including:
            1. Exam dates
            2. Assignment due dates/times
            3. Quiz schedules
            
            Format the response as a JSON object with dates in ISO format:
            {
                "exams": [{"name": "string", "date": "ISO-date", "time": "string"}],
                "assignments": {"due_day": "string", "due_time": "string"},
                "quizzes": {"schedule": "string"}
            }
            """
        }

    async def analyze_text(self, text: str, analysis_type: str) -> Dict[str, Any]:
        """
        Analyze syllabus text using GPT-4 for a specific type of analysis.
        
        Args:
            text: The syllabus text to analyze
            analysis_type: Type of analysis ('grading', 'schedule', etc.)
            
        Returns:
            Dictionary containing the extracted information
        """
        try:
            prompt = self.prompts.get(analysis_type)
            if not prompt:
                raise ValueError(f"Unknown analysis type: {analysis_type}")

            full_prompt = f"""
            {prompt}
            
            Syllabus text:
            {text}
            """

            response = await openai.ChatCompletion.acreate(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a precise syllabus analyzer. Extract and structure information exactly as requested."},
                    {"role": "user", "content": full_prompt}
                ],
                temperature=0,
                max_tokens=1000
            )

            try:
                result = json.loads(response.choices[0].message.content)
                return self.validate_and_clean_response(result, analysis_type)
            except json.JSONDecodeError:
                self.logger.error("Failed to parse GPT response as JSON")
                raise

        except Exception as e:
            self.logger.error(f"Error during analysis: {str(e)}")
            raise

    def validate_and_clean_response(self, response: Dict[str, Any], analysis_type: str) -> Dict[str, Any]:
        """Validate and clean the GPT response based on analysis type."""
        if analysis_type == 'grading':
            total_weight = sum(comp['weight'] for comp in response.get('components', []))
            if not 0.99 <= total_weight <= 1.01:
                self.logger.warning(f"Grading weights sum to {total_weight*100}%, expected 100%")
            for comp in response.get('components', []):
                if comp['weight'] > 1:
                    comp['weight'] /= 100
        elif analysis_type == 'schedule':
            current_year = datetime.now().year
            for exam in response.get('exams', []):
                try:
                    date = datetime.fromisoformat(exam['date'])
                    if date.year < current_year:
                        exam['date'] = exam['date'].replace(str(date.year), str(current_year))
                except ValueError:
                    self.logger.warning(f"Invalid date format in exam schedule: {exam['date']}")
        return response

    async def extract_complete_information(self, text: str) -> Dict[str, Any]:
        """Extract all relevant information from the syllabus asynchronously."""
        all_info = {}
        for analysis_type in self.prompts.keys():
            try:
                info = await self.analyze_text(text, analysis_type)
                all_info[analysis_type] = info
            except Exception as e:
                self.logger.error(f"Failed to extract {analysis_type} information: {str(e)}")
                all_info[analysis_type] = None
        return all_info

    async def calculate_grade_distribution(self, text: str, grades: Dict[str, List[float]]) -> Dict[str, float]:
        """
        Calculate final grade based on extracted weights and provided grades.
        
        Args:
            text: The syllabus text to analyze
            grades: Dictionary of component names and lists of grades
            
        Returns:
            Dictionary containing final grade calculation and component breakdowns
        """
        info = await self.analyze_text(text, 'grading')
        weights = {comp['name']: comp['weight'] for comp in info['components']}
        final_grade = 0
        breakdown = {}
        for component, grade_list in grades.items():
            if component in weights:
                if component in info.get('drop_policies', {}):
                    grade_list = sorted(grade_list)[1:]  # Drop lowest
                avg = sum(grade_list) / len(grade_list)
                weighted = avg * weights[component]
                final_grade += weighted
                breakdown[component] = {'average': avg, 'weighted': weighted}
        return {'final_grade': final_grade, 'breakdown': breakdown}

# Main execution
if __name__ == "__main__":
    analyzer = SyllabusGPTAnalyzer("apaiapiapiapapaia")
    grades = {
        "Individual Homework": [95, 87, 92, 88, 90],
        "Individual Quizzes": [88, 92, 85, 90],
        "Midterm": [89],
        "Final Exam": [91]
    }
    
    async def main():
        # Extract complete information if needed
        all_info = await analyzer.extract_complete_information(syllabus_text)
        # Calculate grade distribution
        grade_distribution = await analyzer.calculate_grade_distribution(syllabus_text, grades)
        print(json.dumps(grade_distribution, indent=2))
    
    asyncio.run(main())

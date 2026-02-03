import os
import json
import openai
import google.generativeai as genai
from typing import Dict, List, Any
from config import Config

class AISummarizer:
    def __init__(self):
        self.config = Config()
        
        if self.config.AI_PROVIDER == 'openai' and self.config.OPENAI_API_KEY:
            openai.api_key = self.config.OPENAI_API_KEY
            self.provider = 'openai'
        elif self.config.AI_PROVIDER == 'gemini' and self.config.GEMINI_API_KEY:
            genai.configure(api_key=self.config.GEMINI_API_KEY)
            self.provider = 'gemini'
        else:
            self.provider = 'mock'  # Fallback to mock data for testing
    
    def generate_summary(self, transcript: str, meeting_type: str) -> Dict[str, Any]:
        """Generate structured meeting summary using AI"""
        
        if self.provider == 'openai':
            return self._openai_summary(transcript, meeting_type)
        elif self.provider == 'gemini':
            return self._gemini_summary(transcript, meeting_type)
        else:
            return self._mock_summary(transcript, meeting_type)
    
    def _openai_summary(self, transcript: str, meeting_type: str) -> Dict[str, Any]:
        """Generate summary using OpenAI"""
        prompt = f"""
        Analyze this {meeting_type} meeting transcript and provide a structured summary in JSON format.
        
        Transcript: {transcript[:4000]}  # Limit token usage
        
        Provide output in this exact JSON structure:
        {{
            "summary": "brief overall summary",
            "key_points": ["point1", "point2", ...],
            "decisions": ["decision1", "decision2", ...],
            "action_items": [
                {{"task": "task description", "owner": "person name", "due_date": "date if mentioned"}}
            ],
            "agenda": [
                {{"topic": "topic name", "summary": "brief discussion summary"}}
            ]
        }}
        
        Extract owners from transcript if mentioned (look for phrases like 'John will handle', 'assigned to Sarah').
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a meeting summarizer. Extract key information and structure it."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            # Extract JSON from response
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            json_str = content[json_start:json_end]
            
            return json.loads(json_str)
            
        except Exception as e:
            print(f"OpenAI error: {e}")
            return self._mock_summary(transcript, meeting_type)
    
    def _gemini_summary(self, transcript: str, meeting_type: str) -> Dict[str, Any]:
        """Generate summary using Google Gemini"""
        try:
            model = genai.GenerativeModel('gemini-pro')
            prompt = f"""
            Analyze this {meeting_type} meeting transcript and provide a structured summary in JSON format.
            
            Transcript: {transcript[:4000]}
            
            Output only valid JSON with this structure:
            {{
                "summary": "brief overall summary",
                "key_points": ["point1", "point2", ...],
                "decisions": ["decision1", "decision2", ...],
                "action_items": [
                    {{"task": "task description", "owner": "person name", "due_date": "date if mentioned"}}
                ],
                "agenda": [
                    {{"topic": "topic name", "summary": "brief discussion summary"}}
                ]
            }}
            """
            
            response = model.generate_content(prompt)
            json_str = response.text.strip()
            
            # Clean response
            if json_str.startswith('```json'):
                json_str = json_str[7:-3]
            elif json_str.startswith('```'):
                json_str = json_str[3:-3]
            
            return json.loads(json_str)
            
        except Exception as e:
            print(f"Gemini error: {e}")
            return self._mock_summary(transcript, meeting_type)
    
    def _mock_summary(self, transcript: str, meeting_type: str) -> Dict[str, Any]:
        """Generate mock summary for testing"""
        return {
            "summary": f"This was a {meeting_type} discussing various topics from the transcript.",
            "key_points": [
                "Project timeline was discussed",
                "Budget constraints were highlighted",
                "Team assignments were made"
            ],
            "decisions": [
                "Approved the Q2 roadmap",
                "Decided to hire two new developers"
            ],
            "action_items": [
                {"task": "Prepare project proposal", "owner": "John Doe", "due_date": "2024-12-15"},
                {"task": "Schedule client meeting", "owner": "Jane Smith", "due_date": "2024-12-10"}
            ],
            "agenda": [
                {"topic": "Project Update", "summary": "Discussed current project status and blockers"},
                {"topic": "Budget Review", "summary": "Reviewed Q3 budget and allocations"}
            ]
        }
#!/usr/bin/env python3
"""
🤖 AI Planning Agent - Uses Ollama for intelligent task breakdown
Integrates with your existing LLaMA setup for AI-powered planning
"""

import json
import sys
import os
import requests
import subprocess
from datetime import datetime

class AIPlanningAgent:
    def __init__(self):
        self.name = "ai_planner"
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model = "llama3"
        
    def check_ollama_available(self) -> bool:
        """Check if Ollama is running and accessible"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def query_ollama(self, prompt: str) -> str:
        """Query Ollama for AI-powered analysis"""
        try:
            response = requests.post(
                self.ollama_url,
                json={"model": self.model, "prompt": prompt},
                stream=True,
                timeout=30
            )
            
            full_response = ""
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        full_response += data.get("response", "")
                    except json.JSONDecodeError:
                        continue
            
            return full_response.strip()
        except Exception as e:
            return f"Error querying Ollama: {str(e)}"
    
    def analyze_codebase_context(self, workspace: str) -> dict:
        """Analyze codebase to provide context for AI planning"""
        
        context = {
            "files": [],
            "technologies": set(),
            "patterns": [],
            "complexity": "unknown"
        }
        
        for root, dirs, files in os.walk(workspace):
            if 'venv' in root or '__pycache__' in root:
                continue
                
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    context["files"].append(os.path.relpath(file_path, workspace))
                    
                    # Detect technologies/frameworks
                    try:
                        with open(file_path, 'r') as f:
                            content = f.read().lower()
                            
                        if 'streamlit' in content:
                            context["technologies"].add("Streamlit")
                        if 'fastapi' in content:
                            context["technologies"].add("FastAPI")
                        if 'flask' in content:
                            context["technologies"].add("Flask")
                        if 'sqlite' in content:
                            context["technologies"].add("SQLite")
                        if 'requests' in content:
                            context["technologies"].add("HTTP/API")
                        if 'concurrent.futures' in content:
                            context["technologies"].add("Parallel Processing")
                        if 'subprocess' in content:
                            context["technologies"].add("System Integration")
                            
                    except:
                        continue
        
        # Determine complexity
        file_count = len(context["files"])
        if file_count > 20:
            context["complexity"] = "high"
        elif file_count > 10:
            context["complexity"] = "medium"
        else:
            context["complexity"] = "low"
        
        context["technologies"] = list(context["technologies"])
        return context
    
    def generate_ai_plan(self, request: str, context: dict) -> dict:
        """Generate AI-powered implementation plan"""
        
        # Create detailed prompt for Ollama
        prompt = f"""
You are an expert software architect and project planner. Analyze this feature request and create a detailed implementation plan.

FEATURE REQUEST: {request}

CURRENT CODEBASE CONTEXT:
- Files: {len(context['files'])} Python files
- Technologies: {', '.join(context['technologies'])}
- Complexity: {context['complexity']}
- Key files: {', '.join(context['files'][:5])}

Please provide a structured implementation plan with:
1. Technical approach and architecture decisions
2. Step-by-step implementation phases
3. Risk assessment and mitigation strategies
4. Time estimates for each phase
5. Dependencies and prerequisites
6. Testing strategy

Format your response as a clear, actionable plan.
"""
        
        if self.check_ollama_available():
            ai_response = self.query_ollama(prompt)
            
            # Parse AI response into structured plan
            plan = {
                "ai_analysis": ai_response,
                "approach": "ai_generated",
                "confidence": "high" if len(ai_response) > 200 else "medium",
                "implementation_strategy": self._extract_strategy(ai_response),
                "risk_factors": self._extract_risks(ai_response),
                "time_estimate": self._extract_time_estimate(ai_response)
            }
        else:
            # Fallback to rule-based planning
            plan = self._fallback_planning(request, context)
        
        return plan
    
    def _extract_strategy(self, ai_response: str) -> list:
        """Extract implementation strategy from AI response"""
        strategies = []
        
        # Look for numbered lists or bullet points
        lines = ai_response.split('\n')
        for line in lines:
            line = line.strip()
            if any(line.startswith(prefix) for prefix in ['1.', '2.', '3.', '•', '-', '*']):
                if len(line) > 10:  # Filter out short lines
                    strategies.append(line)
        
        return strategies[:6]  # Limit to 6 key strategies
    
    def _extract_risks(self, ai_response: str) -> list:
        """Extract risk factors from AI response"""
        risks = []
        
        # Look for risk-related keywords
        risk_keywords = ['risk', 'challenge', 'difficulty', 'problem', 'issue', 'concern']
        lines = ai_response.lower().split('\n')
        
        for line in lines:
            if any(keyword in line for keyword in risk_keywords):
                if len(line.strip()) > 15:
                    risks.append(line.strip())
        
        return risks[:3]  # Limit to top 3 risks
    
    def _extract_time_estimate(self, ai_response: str) -> str:
        """Extract time estimate from AI response"""
        time_keywords = ['hour', 'day', 'week', 'minute', 'time']
        lines = ai_response.lower().split('\n')
        
        for line in lines:
            if any(keyword in line for keyword in time_keywords):
                if any(char.isdigit() for char in line):
                    return line.strip()
        
        return "Time estimate not specified"
    
    def _fallback_planning(self, request: str, context: dict) -> dict:
        """Fallback planning when Ollama is not available"""
        
        return {
            "ai_analysis": f"Fallback analysis for: {request}",
            "approach": "rule_based",
            "confidence": "medium",
            "implementation_strategy": [
                f"1. Analyze existing {', '.join(context['technologies'])} integration points",
                f"2. Design solution architecture for: {request}",
                "3. Implement core functionality with proper error handling",
                "4. Add comprehensive testing coverage",
                "5. Update documentation and examples",
                "6. Perform integration testing and validation"
            ],
            "risk_factors": [
                f"Integration complexity with existing {context['complexity']} codebase",
                "Potential breaking changes to current functionality",
                "Performance impact on existing systems"
            ],
            "time_estimate": f"Estimated 2-4 hours for {context['complexity']} complexity project"
        }

def main():
    if len(sys.argv) < 2:
        print("❌ No task data provided")
        sys.exit(1)
    
    try:
        task_data = json.loads(sys.argv[1])
        agent = AIPlanningAgent()
        
        print(f"🤖 AI Planning Agent: Analyzing request with AI assistance...")
        
        request = task_data.get('request', '')
        workspace = task_data.get('workspace', '.')
        
        # Analyze codebase context
        context = agent.analyze_codebase_context(workspace)
        
        # Generate AI-powered plan
        ai_plan = agent.generate_ai_plan(request, context)
        
        # Check Ollama status
        ollama_status = "available" if agent.check_ollama_available() else "unavailable"
        
        result = {
            "request": request,
            "codebase_context": context,
            "ai_plan": ai_plan,
            "ollama_status": ollama_status,
            "planning_approach": ai_plan["approach"],
            "confidence_level": ai_plan["confidence"],
            "timestamp": datetime.now().isoformat(),
            "status": "completed"
        }
        
        print(f"✅ AI planning completed")
        print(f"   🧠 Approach: {ai_plan['approach']}")
        print(f"   📊 Confidence: {ai_plan['confidence']}")
        print(f"   🔌 Ollama: {ollama_status}")
        print(f"   ⚙️ Technologies: {len(context['technologies'])}")
        
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"❌ AI planning failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

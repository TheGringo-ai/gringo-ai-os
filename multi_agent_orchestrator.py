#!/usr/bin/env python3
"""
Multi-Agent Orchestrator
Spawns and coordinates specialized agents in parallel
"""

import os
import json
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import List, Dict, Any

class AgentResult:
    def __init__(self, agent_name: str, success: bool, output: str, artifacts: List[str] = None):
        self.agent_name = agent_name
        self.success = success
        self.output = output
        self.artifacts = artifacts or []
        self.timestamp = datetime.now().isoformat()

class MultiAgentOrchestrator:
    def __init__(self, workspace_path: str = "."):
        self.workspace_path = workspace_path
        self.agents = {}
        self.results = []
        
    def register_agent(self, name: str, script_path: str, description: str):
        """Register a specialized agent"""
        self.agents[name] = {
            "script": script_path,
            "description": description,
            "active": os.path.exists(script_path)
        }
        
    def spawn_agent(self, agent_name: str, task_data: Dict[str, Any]) -> AgentResult:
        """Spawn a single agent with task data"""
        if agent_name not in self.agents:
            return AgentResult(agent_name, False, f"Agent {agent_name} not registered")
            
        agent_info = self.agents[agent_name]
        if not agent_info["active"]:
            return AgentResult(agent_name, False, f"Agent script {agent_info['script']} not found")
            
        print(f"🤖 Spawning {agent_name}: {agent_info['description']}")
        
        try:
            # Pass task data as JSON to the agent
            task_json = json.dumps(task_data)
            
            result = subprocess.run([
                "python3", agent_info["script"], task_json
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print(f"✅ {agent_name} completed successfully")
                return AgentResult(agent_name, True, result.stdout)
            else:
                print(f"❌ {agent_name} failed: {result.stderr}")
                return AgentResult(agent_name, False, result.stderr)
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {agent_name} timed out")
            return AgentResult(agent_name, False, "Agent execution timeout")
        except Exception as e:
            print(f"⚠️ {agent_name} error: {e}")
            return AgentResult(agent_name, False, str(e))
    
    def orchestrate_parallel(self, tasks: List[Dict[str, Any]]) -> List[AgentResult]:
        """Run multiple agents in parallel"""
        print(f"🎼 Orchestrating {len(tasks)} agents in parallel...")
        
        results = []
        with ThreadPoolExecutor(max_workers=min(len(tasks), 4)) as executor:
            futures = {
                executor.submit(self.spawn_agent, task["agent"], task["data"]): task 
                for task in tasks
            }
            
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                self.results.append(result)
        
        return results
    
    def run_feature_pipeline(self, feature_request: str) -> bool:
        """Complete pipeline: Plan -> Code -> Test -> Doc -> Review"""
        print(f"🚀 Starting feature pipeline: {feature_request}")
        
        # Phase 1: Planning
        planning_tasks = [{
            "agent": "planner",
            "data": {"request": feature_request, "workspace": self.workspace_path}
        }]
        
        planning_results = self.orchestrate_parallel(planning_tasks)
        if not all(r.success for r in planning_results):
            print("❌ Planning phase failed")
            return False
            
        # Phase 2: Parallel Implementation
        implementation_tasks = [
            {"agent": "refactor", "data": {"target": "code_quality"}},
            {"agent": "test_gen", "data": {"coverage_target": 80}},
            {"agent": "doc_gen", "data": {"format": "markdown"}}
        ]
        
        impl_results = self.orchestrate_parallel(implementation_tasks)
        
        # Phase 3: Review
        review_tasks = [{
            "agent": "reviewer", 
            "data": {"artifacts": [r.artifacts for r in impl_results]}
        }]
        
        review_results = self.orchestrate_parallel(review_tasks)
        
        all_success = all(r.success for r in impl_results + review_results)
        
        if all_success:
            print("🎉 Feature pipeline completed successfully!")
        else:
            print("⚠️ Pipeline issues detected - check agent outputs")
            
        return all_success
    
    def get_summary(self) -> Dict[str, Any]:
        """Get execution summary"""
        total = len(self.results)
        successful = sum(1 for r in self.results if r.success)
        
        return {
            "total_agents": total,
            "successful": successful,
            "failed": total - successful,
            "success_rate": (successful / total * 100) if total > 0 else 0,
            "results": [
                {
                    "agent": r.agent_name,
                    "success": r.success,
                    "timestamp": r.timestamp
                } for r in self.results
            ]
        }

def main():
    """Demo the orchestrator"""
    orchestrator = MultiAgentOrchestrator()
    
    # Register available agents
    orchestrator.register_agent("planner", "agents/planner_agent.py", "Task planning and breakdown")
    orchestrator.register_agent("refactor", "agents/refactor_agent.py", "Code refactoring and optimization")
    orchestrator.register_agent("test_gen", "agents/test_generator_agent.py", "Automated test generation")
    orchestrator.register_agent("doc_gen", "agents/doc_generator_agent.py", "Documentation generation")
    orchestrator.register_agent("reviewer", "agents/review_agent.py", "Code review and quality check")
    
    # Demo parallel task execution
    demo_tasks = [
        {"agent": "refactor", "data": {"target": "performance"}},
        {"agent": "test_gen", "data": {"focus": "edge_cases"}},
        {"agent": "doc_gen", "data": {"style": "comprehensive"}}
    ]
    
    results = orchestrator.orchestrate_parallel(demo_tasks)
    summary = orchestrator.get_summary()
    
    print("\n📊 Orchestration Summary:")
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()

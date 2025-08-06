#!/usr/bin/env python3
"""
🔥 Agent Registration Demo
Shows how to register and manage custom agents
"""

import multi_agent_orchestrator
import json

def main():
    print("🤖 GRINGO'S AGENT REGISTRATION SYSTEM")
    print("=" * 50)
    
    # Create orchestrator
    orchestrator = multi_agent_orchestrator.MultiAgentOrchestrator()
    
    # Register all available agents
    agents_to_register = [
        ("planner", "agents/planner_agent.py", "🧠 Task planning and breakdown"),
        ("refactor", "agents/refactor_agent.py", "⚙️ Code refactoring and optimization"),
        ("test_gen", "agents/test_generator_agent.py", "🧪 Automated test generation"),
        ("doc_gen", "agents/doc_generator_agent.py", "📚 Documentation generation"),
        ("reviewer", "agents/review_agent.py", "🔍 Code review and quality check"),
        ("performance", "agents/performance_agent.py", "⚡ Performance monitoring")
    ]
    
    print("📋 Registering Agents...")
    for name, script, description in agents_to_register:
        orchestrator.register_agent(name, script, description)
        status = "✅ Active" if orchestrator.agents[name]["active"] else "❌ Inactive"
        print(f"   {name:12} {status:12} {description}")
    
    print()
    print("🚀 Agent Registry Status:")
    print("-" * 50)
    
    active_agents = []
    inactive_agents = []
    
    for name, info in orchestrator.agents.items():
        if info["active"]:
            active_agents.append(name)
        else:
            inactive_agents.append(name)
    
    print(f"🟢 Active Agents ({len(active_agents)}): {', '.join(active_agents)}")
    print(f"🔴 Inactive Agents ({len(inactive_agents)}): {', '.join(inactive_agents) if inactive_agents else 'None'}")
    
    print()
    print("🎯 Example: Running Parallel Agents")
    print("-" * 50)
    
    # Demo parallel execution
    if len(active_agents) >= 3:
        demo_tasks = [
            {"agent": "refactor", "data": {"target": "demo", "workspace": "."}},
            {"agent": "test_gen", "data": {"coverage_target": 75, "workspace": "."}},
            {"agent": "performance", "data": {"type": "quick", "workspace": "."}}
        ]
        
        print("Executing 3 agents in parallel...")
        results = orchestrator.orchestrate_parallel(demo_tasks)
        
        print()
        print("📊 Execution Results:")
        for result in results:
            status = "✅" if result.success else "❌"
            print(f"   {status} {result.agent_name:12} - {result.timestamp}")
        
        summary = orchestrator.get_summary()
        print(f"Total Executed: {summary['total_agents']}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
    
    else:
        print("⚠️ Need at least 3 active agents for parallel demo")
    
    print()
    print("🔥 Registration Complete! Use orchestrator.register_agent() to add more agents.")

if __name__ == "__main__":
    main()

# API Documentation

*Auto-generated on 2025-08-06 13:07:01*

## cockpit.py

---

## multi_agent_orchestrator.py

Multi-Agent Orchestrator
Spawns and coordinates specialized agents in parallel

### Classes

#### `AgentResult`

**Methods:** __init__

#### `MultiAgentOrchestrator`

**Methods:** __init__, register_agent, spawn_agent, orchestrate_parallel, run_feature_pipeline, get_summary

### Functions

---

## call_llama.py

---

## agent_command_center.py

🔥 Gringo's AI Agent Command Center 🔥
Multi-Agent Orchestration with Ollama Integration

---

## agent_registry_demo.py

🔥 Agent Registration Demo
Shows how to register and manage custom agents

### Functions

---

## fredfix_agent.py

### Functions

#### `create_followup_task(task_description)`

Log follow-up tasks to tasks.json

#### `run_runtime_check(entry_file)`

Attempt to run all detected entry points (in parallel if multiple) or the specified file, capturing runtime errors.

#### `run_parallel_tests(test_pattern)`

Run all test files in parallel for faster validation

#### `run_full_validation(entry_pattern, test_pattern)`

Run both runtime checks and tests in parallel for complete validation

---

## app.py

Simple entry point to demonstrate parallel execution

### Functions

---

## ollama_chat_ui.py

---

## main.py

Gringo's Parallel Agent Runner
Demonstrates parallel runtime + test execution

### Functions

---

## death_server.py

### Functions

#### `chat(prompt)`

#### `search_memory(keyword)`

#### `list_files()`

#### `read_file(path)`

#### `write_file(path, content)`

---

## agents/planner_agent.py

Planning Agent - Breaks down complex tasks into actionable steps

### Classes

#### `PlannerAgent`

**Methods:** __init__, analyze_request, create_task_breakdown

### Functions

---

## agents/performance_agent.py

Custom Performance Agent - System performance monitoring and optimization

### Classes

#### `PerformanceAgent`

**Methods:** __init__, monitor_system, analyze_performance, _generate_performance_recommendations

### Functions

---

## agents/review_agent.py

Review Agent - Code quality assessment and final validation

### Classes

#### `ReviewAgent`

**Methods:** __init__, assess_code_quality, run_static_analysis, generate_quality_report

### Functions

---

## agents/refactor_agent.py

Refactor Agent - Code optimization, cleanup, and restructuring

### Classes

#### `RefactorAgent`

**Methods:** __init__, analyze_code_quality, _categorize_issues, apply_basic_fixes, generate_recommendations

### Functions

---

## agents/doc_generator_agent.py

Documentation Generator Agent - Auto-generates docs and README files

### Classes

#### `DocGeneratorAgent`

**Methods:** __init__, scan_project_structure, extract_module_info, generate_api_docs, generate_readme

### Functions

---


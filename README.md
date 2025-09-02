# AI Agent Demonstration Project

This project demonstrates the fundamental concepts of AI Agents through practical examples. It's designed to help students understand how AI agents work, their components, and real-world applications.

## 🧠 What are AI Agents?

AI Agents are autonomous systems that can:

- **Perceive** their environment
- **Reason** about what actions to take
- **Act** to achieve goals
- **Learn** from experience

### Core Components

1. **LLM/Reasoning Engine**: Makes decisions and processes information
2. **Tools/Actions**: Functions the agent can call to interact with the world
3. **Memory**: Stores state for multi-step reasoning and context
4. **Planner**: Breaks complex tasks into smaller, manageable steps

## 🚀 Why AI Agents Matter for Developers

- **Automate repetitive workflows** - Reduce manual tasks
- **Enable multi-step problem solving** - Handle complex, multi-stage processes
- **Integrate intelligence into existing tools** - Enhance current codebases with AI capabilities

## 📁 Project Structure

```
beetroot/
├── README.md                           # This file
├── requirements.txt                    # Python dependencies
├── examples/
│   ├── 01_basic_agent.py             # Basic agent loop with Ollama
│   ├── 02_tool_using_agent.py        # Agent using internal APIs
│   ├── 03_planning_agent.py          # Agent with memory and planning
│   ├── 04_code_review_agent.py       # Code review helper
│   ├── 05_data_query_agent.py        # Data query assistant
│   └── 06_knowledge_search_agent.py  # Knowledge base search
├── tools/
│   ├── __init__.py
│   ├── code_tools.py                  # Code analysis tools
│   ├── data_tools.py                  # Data manipulation tools
│   └── search_tools.py                # Search and retrieval tools
├── agents/
│   ├── __init__.py
│   ├── base_agent.py                  # Base agent class
│   ├── memory.py                      # Memory management
│   └── planner.py                     # Task planning
└── config/
    └── settings.py                    # Configuration settings
```

## 🛠️ Prerequisites

### 1. Python Environment

- Python 3.8+ (recommended: Python 3.9+)
- pip package manager

### 2. Ollama (Local LLM)

Install Ollama from [https://ollama.ai](https://ollama.ai)

**macOS/Linux:**

```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
Download from [https://ollama.ai/download](https://ollama.ai/download)

### 3. Pull a Model

```bash
# Pull Mistral (recommended for this demo)
ollama pull mistral

# Or try other models
ollama pull llama2
ollama pull codellama
```

### 4. Install Python Dependencies

```bash
# Create and activate a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
# venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

## 🏃‍♂️ Running the Examples

### Example 1: Basic Agent Loop

```bash
# Make sure virtual environment is activated
source venv/bin/activate  # On macOS/Linux
# or
# venv\Scripts\activate  # On Windows

python examples/01_basic_agent.py
```

**What it demonstrates:** Basic agent interaction loop, simple reasoning, and response generation.

### Example 2: Tool-Using Agent

```bash
# Make sure virtual environment is activated
source venv/bin/activate  # On macOS/Linux
# or
# venv\Scripts\activate  # On Windows

python examples/02_tool_using_agent.py
```

**What it demonstrates:** How agents can use tools/functions to accomplish tasks.

### Example 3: Planning Agent with Memory

```bash
# Make sure virtual environment is activated
source venv/bin/activate  # On macOS/Linux
# or
# venv\Scripts/activate  # On Windows

python examples/03_planning_agent.py
```

**What it demonstrates:** Multi-step planning, memory management, and complex task breakdown.

### Example 4: Code Review Agent

```bash
# Make sure virtual environment is activated
source venv/bin/activate  # On macOS/Linux
# or
# venv\Scripts\activate  # On Windows

python examples/04_code_review_agent.py
```

**What it demonstrates:** Real-world application for code analysis and review.

### Example 5: Data Query Agent

```bash
# Make sure virtual environment is activated
source venv/bin/activate  # On macOS/Linux
# or
# venv\Scripts\activate  # On Windows

python examples/05_data_query_agent.py
```

**What it demonstrates:** Data analysis and manipulation through natural language.

### Example 6: Knowledge Search Agent

```bash
# Make sure virtual environment is activated
source venv/bin/activate  # On macOS/Linux
# or
# venv\Scripts\activate  # On Windows

python examples/06_knowledge_search_agent.py
```

**What it demonstrates:** Information retrieval and knowledge base search.

## 🔧 Configuration

Edit `config/settings.py` to customize:

- Model selection
- API endpoints
- Memory settings
- Planning parameters

## 📚 Learning Path

1. **Start with Example 1** - Understand basic agent concepts
2. **Move to Example 2** - Learn about tool usage
3. **Try Example 3** - Explore planning and memory
4. **Experiment with Examples 4-6** - See real-world applications

## 🎯 Key Concepts to Understand

- **Agent Loop**: Perceive → Think → Act → Learn
- **Tool Integration**: How agents use external functions
- **Memory Management**: Storing and retrieving context
- **Planning**: Breaking complex tasks into steps
- **Error Handling**: Graceful failure and recovery

## 🐛 Troubleshooting

### Common Issues

1. **Ollama not running**

   ```bash
      which ollama
   ```

   ```bash
   ollama serve
   ```

2. **Model not found**

   ```bash
   ollama list
   ollama pull mistral
   ```

3. **Python dependencies**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

## 📖 Additional Resources

- [Ollama Documentation](https://ollama.ai/docs)
- [LangChain Framework](https://python.langchain.com/)
- [AI Agent Patterns](https://github.com/microsoft/AI-For-Beginners)

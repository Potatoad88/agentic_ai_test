# Agentic AI Testing

Experimenting and testing agentic AI created using Google ADK.

## Installation

1. Clone this repository and navigate to the `actual` directory:
    ```bash
    cd actual
    ```

2. (Recommended) Create and activate a virtual environment:
    ```bash
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Running the Program

Edit and modify the agents as you wish inside `agent.py`, then run:

```bash
python agent.py
```

## Features / Agents / Tools

- **Weaviate**: Used as a vector database for semantic document storage and retrieval.
- **MCPToolbox**: Provides tools for connecting and interacting with PostgreSQL databases.
- **agentmail**: Enables email sending capabilities via an agentic interface.
- **CrewAI NL2SQL Tool**: Allows natural language to SQL conversion for querying databases using plain English.

## Miscellaneous

- The `parent_folder` was used for tutorials and experimentation.  
  They are not required for running the main agent code.

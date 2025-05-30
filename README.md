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
- **Xero**: Integrates with the Xero MCP server ([github.com/XeroAPI/xero-mcp-server](https://github.com/XeroAPI/xero-mcp-server)) to enable agent access to Xero accounting tools.
- **Opentelemetry**: Enables tracing and monitoring, with support for exporting traces to Langfuse.

## Known Issues

### agentmail-mcp / Email Agent Tool Incompatibility

If you attempt to use the email agent (agentmail-mcp) with Google ADK and Gemini/Vertex AI function calling, you may encounter an error like:

Unable to submit request because list_inboxes functionDeclaration parameters.last_key schema specified other fields alongside any_of. When using any_of, it must be the only field set. Learn more: https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/function-calling

**Explanation:**  
This is due to an incompatibility between the OpenAPI/function schema used by `agentmail-mcp` and Google Vertex AI's function calling requirements. Specifically, the schema for some tool parameters (such as `last_key` in `list_inboxes`) uses `anyOf` alongside other fields, which is not allowed by Vertex AI.

**Workaround:**  
- There is currently no workaround from the agent/user side.  
- You can check for updates to `agentmail-mcp` and `google-adk` that may resolve this issue.
- If the issue persists, report it to the maintainers of `agentmail-mcp` or Google ADK.

**Reference:**  
[Vertex AI Function Calling Schema Requirements](https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/function-calling)

## Miscellaneous

- The `parent_folder` was used for tutorials and experimentation.  
  They are not required for running the main agent code.

# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# @title Import necessary libraries
import asyncio
import os
import weaviate
import json
import base64
import logging
from dotenv import load_dotenv
from google.adk.agents import Agent, LlmAgent
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService
from google.adk.runners import Runner
from google.genai import types # For creating message Content/Parts
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters, SseServerParams
from google.adk.tools.agent_tool import AgentTool
from crewai_tools import NL2SQLTool
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.context import _RUNTIME_CONTEXT
from contextvars import Token
from typing import Optional
from datetime import date

# Use one of the model constants defined earlier
MODEL_GEMINI_2_0_FLASH = "gemini-2.0-flash"
AGENT_MODEL = MODEL_GEMINI_2_0_FLASH # Starting with Gemini

load_dotenv()

langfuse_public_key = os.environ.get("LANGFUSE_PUBLIC_KEY")
langfuse_secret_key = os.environ.get("LANGFUSE_SECRET_KEY")
LANGFUSE_AUTH=base64.b64encode(f"{langfuse_public_key}:{langfuse_secret_key}".encode()).decode()

os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = "https://cloud.langfuse.com/api/public/otel" # EU data region
os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"Authorization=Basic {LANGFUSE_AUTH}"

original_detach = _RUNTIME_CONTEXT.detach

def safe_detach(token: Token):
    try:
        original_detach(token)
    except ValueError as e:
        logging.warning(f"[OpenTelemetry Patch] Ignored context detach error: {e}")

_RUNTIME_CONTEXT.detach = safe_detach

provider = trace.get_tracer_provider()
if hasattr(provider, "add_span_processor"):  # Only works if it’s the SDK provider
    exporter = OTLPSpanExporter()
    provider.add_span_processor(BatchSpanProcessor(exporter))

# @title Define Xero Agent

xero_client_id = os.environ.get("XERO_CLIENT_ID")
xero_client_secret = os.environ.get("XERO_CLIENT_SECRET")

xero_agent = LlmAgent(
    model=AGENT_MODEL,
    name='xero_agent',
    instruction='Assist the user with financial tasks using Xero tools.',
    tools=[
        MCPToolset(
            connection_params=StdioServerParameters(
                command = "node",
                args = ["temp-xero\\dist\\index.js"],
                # Pass the Xero API credentials as environment variables to the npx process
                env={
                    "XERO_CLIENT_ID": xero_client_id,
                    "XERO_CLIENT_SECRET": xero_client_secret
                }
            ),
        )
    ],
)

# @title Define the Search Agent

def list_files(limit: Optional[int] = 10) -> dict:
    """List all documents in the Weaviate collection."""
    print(f"--- Tool: list_files called with limit={limit} ---")
    try:
        client = weaviate.connect_to_local()
        documents = client.collections.get("Document")
        response = documents.query.fetch_objects(limit=limit)
        found_docs = {}
        for idx, obj in enumerate(response.objects, start=1):
            properties = obj.properties
            title = properties.get("title", f"Untitled Document {idx}")
            found_docs[title] = {
                "content": properties.get("content", "[No content provided]")
            }
        client.close()
        if found_docs:
            result = {"status": "success", "documents": found_docs}
            print(f"--- Tool: Listed documents. Result: {json.dumps(result, indent=2)} ---")
            return result
        else:
            print(f"--- Tool: No documents found in Weaviate. ---")
            return {"status": "error", "error_message": "No documents found."}
    except Exception as e:
        print(f"--- Tool: Exception occurred - {str(e)} ---")
        return {"status": "error", "error_message": f"An error occurred while listing documents: {str(e)}"}

def get_file(query: Optional[str] = None, limit: Optional[int] = None) -> dict:
    """Semantic search for documents using Weaviate near_text query."""
    print(f"--- Tool: get_file called with query='{query}' ---")

    if not query:
        return {"status": "error", "error_message": "Please provide a search query."}

    try:
        # Connect to local Weaviate instance
        client = weaviate.connect_to_local()
        documents = client.collections.get("Document")

        # Perform semantic search
        response = documents.query.near_text(
            query=query,
            limit=limit
        )

        # Extract results
        found_docs = {}
        for idx, obj in enumerate(response.objects, start=1):
            properties = obj.properties
            title = properties.get("title", f"Untitled Document {idx}")
            found_docs[title] = {
                "content": properties.get("content", "[No content provided]")
            }

        client.close()

        if found_docs:
            result = {"status": "success", "documents": found_docs}
            print(f"--- Tool: Found matching documents. Result: {json.dumps(result, indent=2)} ---")
            return result
        
        # Fallback: keyword search if semantic search fails
        print("--- Tool: No semantic matches, trying keyword fallback ---")
        client = weaviate.connect_to_local()
        documents = client.collections.get("Document")
        response = documents.query.fetch_objects(limit=100)
        keyword_docs = {}
        for idx, obj in enumerate(response.objects, start=1):
            properties = obj.properties
            content = properties.get("content", "")
            title = properties.get("title", f"Untitled Document {idx}")
            if query.lower() in content.lower():
                keyword_docs[title] = {"content": content}
        client.close()

        if keyword_docs:
            result = {"status": "success", "documents": keyword_docs, "note": "Matched by keyword fallback."}
            print(f"--- Tool: Found keyword matches. Result: {json.dumps(result, indent=2)} ---")
            return result
        else:
            print(f"--- Tool: No matching documents found in Weaviate. ---")
            return {"status": "error", "error_message": "Sorry, no documents matched your query."}

    except Exception as e:
        print(f"--- Tool: Exception occurred - {str(e)} ---")
        return {"status": "error", "error_message": f"An error occurred while searching: {str(e)}"}

search_agent = Agent(
    name="search_agent",
    model=AGENT_MODEL, # Can be a string for Gemini or a LiteLlm object
    description="Search agent that searches for specific files based on user's requirements or simply list out all files.",
    instruction="You are a helpful assistant that helps to search for files. "
                "The files are being stored in weaviate database and you can do semantic search on them based on the vector embeddings. "
                "If there are no files that match the user's requirements, inform them that you can't find any files. "
                "If there are multiple files that matches the user's requirement return all files found. "
                "You can also list all files available in the weaviate database. ",
    tools=[get_file, list_files], # List of tools that this agent can use
)

# @title Define the Email Agent

email_agent = LlmAgent(
    name="email_agent",
    model=AGENT_MODEL, # Can be a string for Gemini or a LiteLlm object
    description="Email agent that sends emails based on user's requirements.",
    instruction="You are a helpful assistant that helps to send emails. "
                "You can send emails based on the user's requirements. "
                "You can make use of the toolset from agentmail to send emails. ",
    # tools=[send_email], # List of tools that this agent can use
    tools=[
        MCPToolset(
            connection_params=StdioServerParameters(
                command="agentmail-mcp",
                args=[f"--api-key={os.environ['AGENTMAIL_API_KEY']}"]
            )
        )
    ]
)

# @title Define postgres agent
postgres_agent = LlmAgent(
    name="postgres_agent",
    model=AGENT_MODEL, # Can be a string for Gemini or a LiteLlm object
    description="Postgres agent that interacts with a PostgreSQL database.",
    instruction="You are a data assistant for a PostgreSQL database about the K-pop group NewJeans."
                "You must use the tools available to answer all user questions."
                "You are not allowed to answer questions from your own knowledge or assumptions. "
                "Use tools like 'list-members' or 'find-member-by-name' when a user mentions a member's name.",
    tools=[
        MCPToolset(
            connection_params=SseServerParams(
                url="http://127.0.0.1:5000/mcp/sse"
            )
        )
    ],
)

# @title Define the NL2SQL Tool

SCHEMA_HINT = """
You are querying a PostgreSQL database with the following schema:

Table: members
- member_id (int): primary key
- name (varchar): member's full name
- birth_date (date): member's birthdate
- position (varchar): member's role in the group
- debut_date (date): when the member debuted

Table: songs
- song_id (int): primary key
- title (varchar): title of the song
- release_date (date): when the song was released
- duration (int): duration of the song in seconds
- genre (varchar): genre of the song

This database contains information about NewJeans members and their songs.
Always return relevant records in your answer.
"""

db_uri = (
    f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
    f"@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
)

nl2sql = NL2SQLTool(db_uri=db_uri, schema_hint=SCHEMA_HINT)

def serialize_dates(obj):
    if isinstance(obj, dict):
        return {k: serialize_dates(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize_dates(i) for i in obj]
    elif isinstance(obj, date):
        return obj.isoformat()
    else:
        return obj

def query_postgres_nl2sql(query: str) -> dict:
    try:
        result = nl2sql.execute_sql(query)
        # serialize dates in the result
        serialized_result = serialize_dates(result)

        return {
            "status": "success",
            "query": query,
            "result": serialized_result
        }

    except Exception as e:
        return {
            "status": "error",
            "query": query,
            "error_message": str(e)
        }
    
def search_nj_db(query: Optional[str] = None) -> dict:
    if not query:
        return {"status": "error", "error_message": "Query is required"}
    return query_postgres_nl2sql(query)

nl2sql_agent = LlmAgent(
    name="nl2sql_agent",
    model=AGENT_MODEL,
    description="Agent that answers questions about the NewJeans music database by converting natural language queries into SQL and returning the results. The database contains tables for members and songs.",
    instruction=(
        "You are an expert at translating natural language questions into SQL queries for a PostgreSQL database. "
        "Always use the provided schema to generate your queries. "
        "The database has two tables: 'members' (with columns member_id, name, birth_date, position, debut_date) and 'songs' (with columns song_id, title, release_date, duration, genre). "
        "When a user asks a question, generate a SQL query that answers it, execute the query, and return the result. "
        "If the question is ambiguous, ask the user for clarification. "
        "Example: For 'What is Minji's birthdate?', generate: SELECT birth_date FROM members WHERE name = 'Minji';"
    ),
    tools=[search_nj_db]
)

# @title Define the Main Agent

def reason(user_input: str) -> dict:
    """Reason about the user's input before taking any action."""
    print(f"--- Tool: reason called with user_input='{user_input}' ---")
    
    # Simulate reasoning by inspecting the input
    reasoning = ""
    if any(word in user_input.lower() for word in ["find", "search", "file", "document", "report"]):
        reasoning = "It seems like the user wants to find a file. I should probably delegate this to the search agent."
    elif any(word in user_input.lower() for word in ["email", "send", "mail", "message"]):
        reasoning = "It seems the user wants to send an email. I should probably delegate this to the email agent."
    else:
        reasoning = "I'm not sure what the user wants. I should ask them to clarify their request."

    result = {
        "status": "success",
        "reasoning": reasoning
    }
    print(f"--- Tool: Reasoning complete. Result: {result} ---")
    return result


root_agent = Agent(
    name="main_agent",
    model=AGENT_MODEL, # Can be a string for Gemini or a LiteLlm object
    description="Main agent that is the first point of contact for users which can delegate tasks to other agents and handle basic conversations.",
    instruction="You are a helpful assistant that engages in friendly conversations. "
                "You follow the reAct framework where you should always reason before you act."
                "You have access to a reasoning tool that helps you to reason about the user's input. "
                "You can use the reasoning from the reasoning tool in additional to your own reasoning to decide what to do next. "
                "You are aware of all other agents in your team and can delegate tasks to them if the user wants to do something that the agents in your team can do. "
                "The agents in your team are passed in as tools. "
                "This is to ensure that the user can only interact with you and not with the other agents directly. "
                "You can transfer to another agent as you wish when you see that there is an agent who can handle the task better than you, you don't have to seek explicit confirmation from the user. "
                "If the user requests for something that none of the agents in your team can do, just inform them that you can't do it. ",
    tools=[
        reason, # Reasoning tool
        AgentTool(search_agent), # Wrap search_agent as a tool
        AgentTool(email_agent),  # Wrap email_agent as a tool
    ], # List of tools that this agent can use
)

async def call_agent_async(query: str, runner, user_id, session_id):
    print(f"\n>>> User Query: {query}")
    content = types.Content(role='user', parts=[types.Part(text=query)])
    final_response_text = "Agent did not produce a final response."
    gen = runner.run_async(user_id=user_id, session_id=session_id, new_message=content)
    try:
        async for event in gen:
            if event.is_final_response():
                if event.content and event.content.parts:
                    final_response_text = event.content.parts[0].text
                elif event.actions and event.actions.escalate:
                    final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
                break
    finally:
        await gen.aclose()
    print(f"<<< Agent Response: {final_response_text}")

async def main():
    APP_NAME = "cli_agent"
    USER_ID = "user_1"
    SESSION_ID = "session_1"

    session_service = InMemorySessionService() 

    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )

    # import weaviate
    # weaviate_client = weaviate.connect_to_local()
    # memory_service = WeaviateMemoryService(
    #     weaviate_client=weaviate_client,
    #     collection_name="adk_chat_history",
    #     embedding_model="text-embedding-004"
    # )

    memory_service = InMemoryMemoryService() 

    runner = Runner(
        agent=xero_agent,
        app_name=APP_NAME,
        session_service=session_service,
        memory_service=memory_service, 
    )

    print("\n--- Starting Interactive Agent Chat (Detailed Output) ---")
    print("Type your message and press Enter. Type 'exit' to quit.\n")

    while True:
        try:
            user_input_text = input("You: ")
            if user_input_text.lower() == 'exit':
                print("--- Ending Chat ---")
                break

            await call_agent_async(
                query=user_input_text,
                runner=runner,
                user_id=USER_ID,
                session_id=SESSION_ID
            )

        except Exception as e:
            print(f"An error occurred during conversation: {e}")
            print("Please try again or type 'exit' to quit.")

if __name__ == "__main__":
    asyncio.run(main())
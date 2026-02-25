# https://developers.openai.com/api/docs/guides/tools-connectors-mcp/?quickstart-panels=remote-mcp

from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
        base_url=os.getenv("OPENAI_BASE_URL"),
    api_key=os.getenv("OPENAI_API_KEY"),
)

chat_model = os.getenv("CHAT_MODEL")

resp = client.responses.create(
    model=chat_model,
    # tools=[
    #     {
    #         "type": "mcp",
    #         "server_label": "dmcp",
    #         "server_description": "A Dungeons and Dragons MCP server to assist with dice rolling.",
    #         "server_url": "https://dmcp-server.deno.dev/sse",
    #         # 'server_url': "https://developers.openai.com/mcp",
    #         "require_approval": "never",
    #     },
    # ],
    input="Roll 2d4+1",
)

print(resp.output_text)
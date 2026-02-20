import logging
from config import CONFIG
# from llm import call_llm
from internal_commands import process as internal_command_process
from solid_rag_query_crud_function_calling_retrieve import call_llm as solid_call_llm

logger = logging.getLogger(__name__)

def run_chat_loop(user_input):
    logger.debug(f"Received input: {user_input}")

    if not user_input:
        logger.error("No input provided")
        return "No input provided"

    messages = []
    messages.append({"role": "user", "content": user_input})

    tool_calls = 0
    done = False

    while done is not True and tool_calls < CONFIG['tool_calls_limit']:
        result = solid_call_llm(messages=messages, tool_calls=tool_calls)
        logger.debug(f"CALL_LLM_RESULT with done boolean, tool_calls counter and assistant reply: {result}")
        done, tool_calls, message = result
        logger.debug(f"DONE: {done}")
        logger.debug(f"TOOL_CALLS_AFTER: {tool_calls}")
        assistant_reply = message.content
        messages.append({"role": "assistant", "content": assistant_reply})
        logger.debug(f"{CONFIG['assistant_name']}: {assistant_reply}")

    return assistant_reply
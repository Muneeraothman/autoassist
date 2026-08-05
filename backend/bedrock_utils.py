import os

import boto3
from dotenv import load_dotenv

from tools import TOOL_SPECS, ToolError, execute_tool

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# Claude Sonnet 4.5 has no in-region (on-demand) inference profile in
# us-east-1 - only the "us." geo cross-region profile does. Calling with the
# bare model ID from this region throws ValidationException: on-demand
# throughput isn't supported for this model.
BEDROCK_MODEL_ID = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"

MAX_TOOL_ITERATIONS = 5

SYSTEM_PROMPT_TEMPLATE = """You are AutoAssist's vehicle maintenance assistant. You help the user understand their own vehicles' maintenance status, service history, and spending - nothing else.

Always use the provided tools to look up real data; never guess or estimate a number yourself. The user's vehicles:
{vehicle_list}

If asked about anything outside this user's own vehicle data (general car advice, other topics, anything you'd have to guess at), politely say that's outside what you can help with here."""

bedrock_client = boto3.client("bedrock-runtime", region_name=AWS_REGION)


def _build_system_prompt(vehicles):
    if not vehicles:
        vehicle_list = "(no vehicles on file yet)"
    else:
        vehicle_list = "\n".join(
            f"- id={v.id}: {v.year} {v.make} {v.model}" for v in vehicles
        )
    return [{"text": SYSTEM_PROMPT_TEMPLATE.format(vehicle_list=vehicle_list)}]


def _extract_text(message) -> str:
    return "".join(block["text"] for block in message["content"] if "text" in block)


def _run_tools(output_message, db, current_user):
    tool_results = []
    for block in output_message["content"]:
        if "toolUse" not in block:
            continue
        tool_use = block["toolUse"]
        try:
            result = execute_tool(tool_use["name"], tool_use["input"], db, current_user)
            # Converse's toolResult "json" field rejects a bare JSON array at
            # the top level ("Provide a json object for the field") - several
            # tools return a list, so it has to be wrapped in an object.
            if isinstance(result, list):
                result = {"items": result}
            tool_results.append(
                {
                    "toolResult": {
                        "toolUseId": tool_use["toolUseId"],
                        "content": [{"json": result}],
                    }
                }
            )
        except ToolError as e:
            tool_results.append(
                {
                    "toolResult": {
                        "toolUseId": tool_use["toolUseId"],
                        "content": [{"text": str(e)}],
                        "status": "error",
                    }
                }
            )
    return tool_results


def run_chat(messages, db, current_user, vehicles) -> str:
    converse_messages = [{"role": m.role, "content": [{"text": m.content}]} for m in messages]
    system = _build_system_prompt(vehicles)

    for _ in range(MAX_TOOL_ITERATIONS):
        response = bedrock_client.converse(
            modelId=BEDROCK_MODEL_ID,
            system=system,
            messages=converse_messages,
            toolConfig={"tools": TOOL_SPECS},
        )
        output_message = response["output"]["message"]
        converse_messages.append(output_message)

        if response["stopReason"] != "tool_use":
            return _extract_text(output_message)

        tool_results = _run_tools(output_message, db, current_user)
        converse_messages.append({"role": "user", "content": tool_results})

    return "I wasn't able to finish looking that up in a reasonable number of steps - try rephrasing your question."

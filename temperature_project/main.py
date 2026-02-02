from configs.model_config import ModelSettings
from pydantic_models.temperature_response import TemperateResponse
from tools.temperature_tools import fetch_temperature, fetch_temperature_tool_def
from groq import Groq
import json

model_settings = ModelSettings()


def execute_tool(tool_name, tool_args):
    mapping_tool_function = {
        "fetch_temperature": fetch_temperature,
    }
    result = mapping_tool_function[tool_name](**tool_args)

    if result is None:
        result = "The operation completed but didn't return any results."

    elif isinstance(result, list):
        result = ", ".join(result)

    elif isinstance(result, dict):
        # Convert dictionaries to formatted JSON strings
        result = json.dumps(result, indent=2)

    else:
        # For any other type, convert using str()
        result = str(result)
    return result


def main(city: str) -> dict:
    model_name = model_settings.model_name
    client = Groq()

    tools = [fetch_temperature_tool_def]

    messages = [
        {
            "role": "system",
            "content": " You are a helpful assistance. Use tool to retrive relevant information.",
        },
        {"role": "user", "content": f"Find the temperature for the city = {city}"},
    ]

    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        tools=tools,
        tool_choice="auto",
        max_completion_tokens=4096,
        temperature=0.5,
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    messages.append(response_message)

    if tool_calls:
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            tool_result = execute_tool(tool_name=function_name, tool_args=function_args)
            messages.append(
                {
                    "role": "tool",
                    "content": f"Tool call with the id : {tool_call.id} is completed with the function {function_name} and the result is : {json.dumps(tool_result)}.  Use this result for futher decision making",
                    "tool_call_id": tool_call.id,
                }
            )

    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        max_completion_tokens=4096,
        temperature=0.5,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "api_response_validation",
                "schema": TemperateResponse.model_json_schema(),
            },
        },
    )

    tempResp: TemperateResponse = TemperateResponse.model_validate(
        json.loads(response.choices[0].message.content)
    )

    print(f"\nOutput:\n{'~' * 7}\n{tempResp.model_dump_json(indent=2)}\n")


info_msg = 'To close  the chat, type "quit"'
while True:
    input_msg = str(input(f"({info_msg}) Enter your City :")).strip()
    if input_msg is None:
        print("Empty input received, Retry\n")
    elif input_msg == "":
        print("Empty input received, Retry\n")
    elif "QUIT" in input_msg.upper():
        print("Thanks you !!!\n")
        break
    else:
        main(input_msg)
        continue

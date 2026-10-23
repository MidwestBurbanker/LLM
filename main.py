import argparse
import os
import sys

from dotenv import load_dotenv
from openai import OpenAI
from config import MAX_AGENT_ITERATIONS

from call_function import available_functions, call_function
from prompts import system_prompt

load_dotenv()

def generate_content(client, messages, verbose):
    response = client.chat.completions.create(
        model="openrouter/free",
        messages=messages,
        temperature=0,
        tools=available_functions,
    )
    if not response.usage:
        raise RuntimeError("API response appears to be malformed")

    if verbose:
        print(f"Prompt tokens: {response.usage.prompt_tokens}")
        print(f"Response tokens: {response.usage.completion_tokens}")

    message = response.choices[0].message

    if message.tool_calls:
        messages.append(message)
        for tool_call in message.tool_calls:
            result_message = call_function(tool_call, verbose)
            messages.append(result_message)
            if not result_message.get("content"):
                raise RuntimeError(f"{tool_call.function.name} returned empty content")
            if verbose:
                print(f"-> {result_message['content']}")
    else:
        return message.content


def main() -> None:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("No environment variable found. Please check .env for OPENROUTER_API_KEY")

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": args.user_prompt},
    ]
    if args.verbose:
        print(f"User prompt: {args.user_prompt}")

    for _ in range(MAX_AGENT_ITERATIONS):
        final_response = generate_content(client, messages, args.verbose)
        if final_response is not None:
            print(final_response)
            break

    if final_response is None:
        print(f"Maximum number of iterations, {MAX_AGENT_ITERATIONS}, reached without a final response ")
        sys.exit(1)


if __name__ == "__main__":
    main()

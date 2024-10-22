from openai import OpenAI
client = OpenAI()

def callLLM(system_prompt, user_prompt):
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": user_prompt
            }
        ]
    )

    return completion.choices[0].message.content

def text_to_eval(text,case="lst"):
    if case == "lst":
        # Ensure that the list is in JSON format. I expect it to start and end with square brackets []
        start_index = text.find("[")
        end_index = text.rfind("]") + 1  # +1 to include the "}" character
    elif case == "dict":
        start_index = text.find("{")
        end_index = text.rfind("}") + 1  # +1 to include the "}" character
    else:
        start_index = 0
        end_index = len(text)-1

    return eval(text[start_index:end_index])

# Example usage
if __name__ == "__main__":
    system_message = "You are a helpful assistant."
    user_prompt = "What is the capital of France?"
    
    response = callLLM(user_prompt, system=system_message)
    if response:
        print("AI response:", response)
    else:
        print("Failed to get a response from the AI.")

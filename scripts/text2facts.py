from call_llm import callLLM,text_to_eval

def text2facts(text):
    system = "Extract every piece of exposition from the given text. Return the set of information in a list format: [\"{fact}\", \"{fact}\"]"
    prompt = f"Extract the exposition from the following text:\n\n{text}"
    
    response = callLLM(system,prompt)
    facts = text_to_eval(response,case="lst")
    return facts

# ... existing code ...

if __name__ == "__main__":
    text = "The capital of France is Paris. The capital of Germany is Berlin. The capital of Italy is Rome."
    facts = text2facts(text)
    print(facts)
"""
Customer Support Ticket Processor
Task 1: Foundation Patterns (Prompt Chaining, Routing, Parallelization, Reflection)
"""

import requests
import asyncio
import json
import re

# ============================================================================
# CONFIGURATION
# ============================================================================
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2:1b"

def call_llm(prompt):
    """Helper function to call Ollama API."""
    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": MODEL, "prompt": prompt, "stream": False},
            timeout=130
        )
        return response.json()["response"].strip()
    except Exception as e:
        return f"[Error: {e}]"

# ============================================================================
# PATTERN 1: PROMPT CHAINING
# ============================================================================
def preprocess(message):
    prompt = f"Fix typos and expand abbreviations. Return only the cleaned message: {message}"
    return call_llm(prompt)

def classify(cleaned_message):
    prompt = f"""From this message: '{cleaned_message}'
Return ONLY valid JSON with keys: category, product, urgency.
Category: technical, billing, general, or complaint.
Urgency: high, medium, or low.
Example: {{"category": "technical", "product": "phone", "urgency": "high"}}"""
    raw = call_llm(prompt)
    # Extract JSON part
    try:
        start = raw.find('{')
        end = raw.rfind('}') + 1
        if start != -1 and end != 0:
            raw = raw[start:end]
    except:
        pass
    return raw

def generate_response(classification_json, original_message):
    prompt = f"Based on {classification_json}, write a helpful 2-sentence reply to the customer: {original_message}"
    return call_llm(prompt)

# ============================================================================
# PATTERN 2: ROUTING
# ============================================================================
def route(category, original_message):
    category = category.lower()
    if category == "technical":
        prompt = f"You are a tech support agent. The customer says: '{original_message}'. Write ONE helpful troubleshooting step for their device."
        branch_name = "TECHNICAL SUPPORT"
    elif category == "billing":
        prompt = f"You are a billing agent. The customer says: '{original_message}'. Write ONE sentence about our refund policy."
        branch_name = "BILLING DEPARTMENT"
    elif category == "complaint":
        prompt = f"You are a customer success manager. The customer says: '{original_message}'. Write ONE empathetic apology and escalation promise."
        branch_name = "COMPLAINT ESCALATION"
    else:
        prompt = f"You are a general support agent. The customer asks: '{original_message}'. Write ONE helpful sentence answering their question."
        branch_name = "GENERAL SUPPORT"
    response = call_llm(prompt)
    return branch_name, response

# ============================================================================
# PATTERN 3: PARALLELIZATION
# ============================================================================
async def parallel_tasks(message):
    task1 = asyncio.to_thread(call_llm, f"Output one word only (positive, negative, or neutral) for: {message}")
    task2 = asyncio.to_thread(call_llm, f"Reply with only a single digit from 1 to 10. No other text. Urgency of: {message}")
    sentiment, priority_raw = await asyncio.gather(task1, task2)
    digits = re.findall(r'\d+', priority_raw)
    priority = digits[0] if digits else "5"
    return sentiment, priority

def run_parallel(message):
    return asyncio.run(parallel_tasks(message))

# ============================================================================
# PATTERN 4: REFLECTION
# ============================================================================
def reflect(draft_response):
    print("  [Reflection]")
    critique1 = call_llm(f"Give one specific criticism of this response (tone or completeness) in one sentence: {draft_response}")
    print(f"    Critique 1: {critique1}")
    improved = call_llm(f"Improve this response based on criticism: '{critique1}'. Original: {draft_response}")
    print(f"    Improved: {improved}")
    critique2 = call_llm(f"Give one more criticism in one sentence: {improved}")
    print(f"    Critique 2: {critique2}")
    final = call_llm(f"Final improve based on: '{critique2}'. Current: {improved}")
    print(f"    Final: {final}")
    return final

# ============================================================================
# MAIN PIPELINE
# ============================================================================
def process_ticket(raw_message):
    print(f"\n{'='*60}")
    print(f"TICKET: {raw_message}")
    print(f"{'='*60}")

    print("\n[1] PROMPT CHAINING")
    cleaned = preprocess(raw_message)
    print(f"  Cleaned: {cleaned}")
    classification = classify(cleaned)
    print(f"  Classification: {classification}")
    draft_reply = generate_response(classification, raw_message)
    print(f"  Draft reply: {draft_reply}")

    print("\n[2] ROUTING")
    try:
        cat_dict = json.loads(classification)
        category = cat_dict.get("category", "general").lower()
    except:
        category = "general"
    branch_name, branch_response = route(category, raw_message)
    print(f"  Category: {category}")
    print(f"  Routed to: {branch_name}")
    print(f"  Branch response: {branch_response}")

    print("\n[3] PARALLELIZATION")
    sentiment, priority = run_parallel(raw_message)
    print(f"  Sentiment: {sentiment}")
    print(f"  Priority score: {priority}/10")

    print("\n[4] REFLECTION")
    final_response = reflect(draft_reply)
    print(f"\n  Final response after reflection: {final_response}")

    return final_response

# ============================================================================
# RUN WITH 10 TEST MESSAGES
# ============================================================================
if __name__ == "__main__":
    test_messages = [
        "my phone won't turn on",
        "my screen is cracked and touch isn't working",
        "the battery drains in 2 hours",
        "apps keep crashing randomly",
        "you charged me for a warranty I didn't buy",
        "I returned the phone but no refund yet",
        "the price dropped 2 days after I bought it",
        "how do I transfer data from my old phone?",
        "when will the new model be released?",
        "this is the 3rd time I'm contacting you. Your support is useless"
    ]

    for msg in test_messages:
        process_ticket(msg)
        print("\n" + "="*60)
        print("NEXT TICKET")
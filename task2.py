"""
Simple Deep Research System
Task 2: Routing, Parallelization, Reflection
"""

import requests
import asyncio
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2:1b"

def call_llm(prompt):
    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": MODEL, "prompt": prompt, "stream": False},
            timeout=130
        )
        return response.json()["response"].strip()
    except Exception as error:
        return f"[Error: {error}]"


# --- STEP 1: ROUTING ---
# look at the query and decide what type of research it needs,
# then break it into 3 subtopics to research

def route_query(query):
    prompt = f"""Look at this research question: '{query}'

Return ONLY a JSON object with these keys:
- research_type: one of 'factual', 'comparison', 'technical', 'historical'
- subtopics: list of exactly 3 sub-questions to research
- strategy: one sentence on how to approach this

Example:
{{
  "research_type": "technical",
  "subtopics": ["What is quantum computing?", "How do quantum computers work?", "What are its current limitations?"],
  "strategy": "Break down the concept technically, covering how it works and where it stands today."
}}

Only return the JSON, nothing else."""

    raw = call_llm(prompt)

    try:
        start = raw.find('{')
        end = raw.rfind('}') + 1
        if start != -1 and end != 0:
            raw = raw[start:end]
        return json.loads(raw)
    except Exception:
        return {
            "research_type": "factual",
            "subtopics": [
                f"What is {query}?",
                f"What are the main uses of {query}?",
                f"What challenges exist around {query}?"
            ],
            "strategy": "General research covering definition, uses, and challenges."
        }


def get_researcher_prompt(research_type, subtopic):
    # assign a specialist role depending on the research type
    if research_type == "factual":
        return f"You are a research analyst. Answer this clearly and accurately: {subtopic}"
    elif research_type == "comparison":
        return f"You are a comparison analyst. Cover pros, cons, and key differences for: {subtopic}"
    elif research_type == "technical":
        return f"You are a technical writer. Give a detailed technical explanation for: {subtopic}"
    elif research_type == "historical":
        return f"You are a historian. Give historical context and key events related to: {subtopic}"
    else:
        return f"Research this question and give a clear, informative answer: {subtopic}"


# --- STEP 2: PARALLELIZATION ---
# instead of researching subtopics one by one, run them all at the same time

async def research_one(research_type, subtopic):
    prompt = get_researcher_prompt(research_type, subtopic)
    prompt += "\n\nWrite 3-4 sentences. Be specific."
    result = await asyncio.to_thread(call_llm, prompt)
    return subtopic, result

async def research_all(research_type, subtopics):
    tasks = [research_one(research_type, subtopic) for subtopic in subtopics]
    results = await asyncio.gather(*tasks)
    return results

def run_research(research_type, subtopics):
    return asyncio.run(research_all(research_type, subtopics))

def combine_results(query, results):
    findings = ""
    for subtopic, content in results:
        findings += f"\nSubtopic: {subtopic}\nFindings: {content}\n"

    prompt = f"""You are a research editor. Take these findings about '{query}' and write them as one clear, flowing report.
4-5 sentences, paragraph form only, no bullet points.

Findings:
{findings}

Report:"""

    return call_llm(prompt)


# --- STEP 3: REFLECTION ---
# review the draft report, find problems, improve it twice

def reflect(query, draft):
    print("  running reflection...")

    critique1 = call_llm(
        f"You are reviewing a research report about '{query}'. "
        f"Give one specific criticism about its depth or clarity in one sentence:\n\n{draft}"
    )
    print(f"  critique 1: {critique1}")

    improved = call_llm(
        f"Improve this research report about '{query}' based on this feedback: '{critique1}'\n\n"
        f"Original:\n{draft}\n\n"
        f"Write an improved version, 4-5 sentences, paragraph form."
    )
    print(f"  improved: {improved}")

    critique2 = call_llm(
        f"Give one more criticism of this report about '{query}' in one sentence:\n\n{improved}"
    )
    print(f"  critique 2: {critique2}")

    final = call_llm(
        f"Make a final improvement to this report about '{query}' based on: '{critique2}'\n\n"
        f"Current:\n{improved}\n\n"
        f"Write the final version, 4-5 sentences, paragraph form."
    )
    print(f"  final: {final}")

    return final


# --- MAIN ---

def research(query):
    print("\n--- new query ---")
    print(f"topic: {query}\n")

    # routing
    print("[1] routing the query...")
    route = route_query(query)
    research_type = route.get("research_type", "factual")
    subtopics = route.get("subtopics", [])
    strategy = route.get("strategy", "")
    print(f"  type: {research_type}")
    print(f"  strategy: {strategy}")
    print(f"  subtopics:")
    for i, subtopic in enumerate(subtopics, 1):
        print(f"    {i}. {subtopic}")

    # parallelization
    print("\n[2] researching subtopics in parallel...")
    results = run_research(research_type, subtopics)
    for subtopic, content in results:
        print(f"\n  Q: {subtopic}")
        print(f"  A: {content}")

    print("\n  combining into draft report...")
    draft = combine_results(query, results)
    print(f"\n  draft: {draft}")

    # reflection
    print("\n[3] reflecting on the draft...")
    final = reflect(query, draft)

    print("\n--- final report ---")
    print(f"topic: {query}")
    print(final)
    print()

    return final


if __name__ == "__main__":
    test_queries = [
        "What is machine learning?",
        "How does blockchain technology work?",
        "What are the effects of climate change on agriculture?",
        "Compare SQL and NoSQL databases",
        "What is the history of the internet?"
    ]

    for query in test_queries:
        research(query)

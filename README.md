# Customer Support Ticket Processor

This project implements an automated customer support ticket processor using four foundational agentic patterns: **Prompt Chaining**, **Routing**, **Parallelization**, and **Reflection**. It uses a local LLM (`llama3.2:1b`) via Ollama.

## Requirements

- Python 3.8 or higher
- [Ollama](https://ollama.com) installed on your machine
- At least 4 GB of free RAM (8 GB recommended)

## Setup Instructions

1. **Install Ollama**  
   Download from [ollama.com](https://ollama.com) and install.

2. **Pull the required model**  
   Open a terminal (Command Prompt) and run:
   ```bash
   ollama pull llama3.2:1b

   Start Ollama (keep it running)
3.
Open another terminal window and run:
" ollama run llama3.2:1b "

Leave this window open (you will see >>>).


4.
In a third terminal, run:
pip install requests


5.Run the script
Navigate to the folder containing final_assignment.py and execute:
python final_assignment.py



How It Works
How It Works
The script processes 10 sample customer messages. For each message it demonstrates:

Prompt Chaining - clean  -classify - generate reply

Routing – route to technical, billing, complaint, or general branch

Parallelization – sentiment analysis + priority scoring run concurrently

Reflection – the AI critiques and improves its own response (2 iterations)

Output
The console output (also saved in output.txt) shows each step clearly.

Files
final_assignment.py – main script

output.txt – sample run output

README.md – this file

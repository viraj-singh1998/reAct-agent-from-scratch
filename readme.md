**** ARCoT: Agentic Retrieval Chain of Thought ****

Instructions to run:

1. create a new virtual environment:

python3 -m venv ~/.virutalenvs/reasoning_agent
source ~/.virutalenvs/reasoning_agent/bin/activate

2. install requirements

pip3 install -r requirements.txt

3. set up the following environment variables in the .env file
OPENAI_API_KEY=...
GOOGLE_API_KEY=...
GOOGLE_CSE_ID=...

4. run reasoning.py as a module, specifying the following command line arguments

python3 -m reasoning --knowledge_base_dir /path/to/your/knowledge/base/directory --knowledge_base_desc "Some text describing your knowledge base, to help the language model understand its utility" --verbose false --query "Your query goes here"

5. the conversations are written to date and time stamped text files in the conversations/ folder.

notes:
>all arguments are optional EXCEPT query, of course.
>use --verbose true for transparency in the reasoning and tool-calling
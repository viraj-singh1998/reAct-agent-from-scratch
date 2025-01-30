
# Instructions to Run

### 1. Create a New Virtual Environment
```bash
python3 -m venv ~/.virutalenvs/reasoning_agent
source ~/.virutalenvs/reasoning_agent/bin/activate
```

### 2. Install Requirements
```bash
pip3 install -r requirements.txt
```

### 3. Set Up the Following Environment Variables in the `.env` File
```env
OPENAI_API_KEY=...
GOOGLE_API_KEY=...
GOOGLE_CSE_ID=...
```

### 4. Run `reasoning.py` as a Module, Specifying the Following Command Line Arguments
```bash
python3 -m reasoning --knowledge_base_dir /path/to/your/knowledge/base/directory --knowledge_base_desc "Some text describing your knowledge base, to help the language model understand its utility" --verbose false --query "Your query goes here"
```

### 5. Conversations are Written to Date and Time Stamped Text Files in the `conversations/` Folder.

---

### Notes:
- **All arguments are optional EXCEPT `query`, of course.**
- Use `--verbose true` for transparency in the reasoning and tool-calling.

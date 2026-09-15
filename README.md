## Run

Run package modules from the project root so Python resolves `agent` as a package:

```powershell
uv run python -m agent.llm
```

Running `src\agent\llm.py` directly places `src\agent` first on Python's import path, where the sibling `agent.py` shadows the `agent` package.

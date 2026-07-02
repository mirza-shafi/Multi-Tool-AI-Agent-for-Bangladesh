# Multi-Tool AI Agent for Bangladesh

A LangChain agent that answers questions about Bangladeshi institutions, hospitals,
and restaurants using SQLite-backed tools, and falls back to web search for general
knowledge questions.

## Architecture

- `data/download_datasets.py` — downloads the 3 HuggingFace datasets into `data/raw/*.csv`.
- `db/build_databases.py` — converts those CSVs into `db/institutions.db`, `db/hospitals.db`,
  `db/restaurants.db` with meaningful column names and correct types.
- `tools/db_tools.py` — `InstitutionsDBTool`, `HospitalsDBTool`, `RestaurantsDBTool`. Each is a
  text-to-SQL pipeline: your question -> LLM writes a SELECT against the known schema ->
  runs it -> LLM turns the result into a natural-language answer.
- `tools/web_search_tool.py` — `WebSearchTool`, backed by Tavily, for general knowledge.
- `agent/main_agent.py` — builds a `create_tool_calling_agent` + `AgentExecutor` with all 4
  tools and a system prompt that routes data questions to the right DB tool and general
  knowledge questions to web search.
- `main.py` — interactive CLI chat loop.

## Setup

1. Create a virtualenv and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and fill in your API keys (Gemini or Groq, plus Tavily).
   You need a free key from at least one LLM provider:
   - Gemini: https://aistudio.google.com/apikey (set `LLM_PROVIDER=gemini`, the default)
   - Groq: https://console.groq.com/keys (set `LLM_PROVIDER=groq`)
   - Tavily (required either way): https://app.tavily.com/
3. Run the agent:
   ```bash
   python main.py
   ```
   `db/*.db` are already built and committed to this repo, so no extra setup is needed.
   Only rerun the pipeline below if you want to refresh the data from HuggingFace:
   ```bash
   python data/download_datasets.py
   python db/build_databases.py
   ```

## Datasets

| Source dataset | Local DB | Table | Notable columns |
|---|---|---|---|
| [Institutional-Information-of-Bangladesh](https://huggingface.co/datasets/Mahadih534/Institutional-Information-of-Bangladesh) | `db/institutions.db` | `institutions` | institute_name, institute_type, division, district, management_type, education_level |
| [all-bangladeshi-hospitals](https://huggingface.co/datasets/Mahadih534/all-bangladeshi-hospitals) | `db/hospitals.db` | `hospitals` | name, facility_type, division, district, city_corporation, is_private |
| [Bangladeshi-Restaurant-Data](https://huggingface.co/datasets/Mahadih534/Bangladeshi-Restaurant-Data) | `db/restaurants.db` | `restaurants` | name, address, rating, number_of_reviews |

**Note:** the hospitals dataset is a DGHS facility directory and does not contain bed or
doctor counts, and the restaurants dataset has no explicit cuisine/city column (location
and cuisine questions are matched against the address/name text). The agent answers using
what's actually in the data rather than inventing fields.

## Example queries

| Query | Tool used |
|---|---|
| "How many hospitals are in Dhaka?" | HospitalsDBTool |
| "How many government institutions are in Rajshahi?" | InstitutionsDBTool |
| "Find restaurants in Chattogram serving biryani." | RestaurantsDBTool |
| "What is the healthcare policy of Bangladesh?" | WebSearchTool |
| "What is the role of DGHS in Bangladesh?" | WebSearchTool |

## Switching LLM provider

Set `LLM_PROVIDER=gemini` (default) or `LLM_PROVIDER=groq` in `.env`. Both have free tiers.
Note: some Gemini API keys return `429 ResourceExhausted` with a `limit: 0` free-tier quota
even though the key is valid — this is a Google Cloud project/billing eligibility issue, not
a bug here. If you hit it, switch to `LLM_PROVIDER=groq`, which has no such restriction.

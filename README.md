# UPSC-LLM
Answering UPSC current affairs questions using RAG LLM.

# Run
- Get an OpenAI Key, and set it inside the `demo-question-answering/.env` as **OPENAI_API_KEY**
- Install Docker and Docker Compose
- `docker compose up` and wait for the containers to spin up
- To see statistics: `curl -X 'POST' 'http://localhost:8000/v1/statistics'`
- To find documents:
```bash
curl -X 'POST' \
  'http://0.0.0.0:8000/v1/retrieve' \
  -H 'accept: */*' \
  -H 'Content-Type: application/json' \
  -d '{
  "query": "Which areas are affected by Cyclone Remal?",
  "k": 4
}'
```
- To ask questions: 
```bash
curl -X 'POST' \
  'http://0.0.0.0:8000/v1/pw_ai_answer' \
  -H 'accept: */*' \
  -H 'Content-Type: application/json' \
  -d '{
  "prompt": "Which areas are affected by Cyclone Remal?"
}'
```

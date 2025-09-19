# analytique-ai-slack-agent

rag-slack-agent/                  # root of project
├── .github/
│   ├── workflows/
│   │   └── ci.yml               # CI for linting, tests
│   └── CODEOWNERS
├── aws/                        # AWS deployment infrastructure (optional)
│   ├── ecs/                   # ECS / Fargate configs
│   └── ec2/                   # EC2 setup scripts
├── docs/                       # Documentation
│   ├── architecture.md
│   ├── flow_diagrams/
│   └── internal_policies.md
├── rag_pipeline/               # core RAG pipeline
│   ├── retrieval/
│   │   ├── vector_search.py
│   │   └── bm25_retriever.py
│   ├── document_processing/
│   │   ├── loaders/            # loaders for PDF, HTML, JSON, etc.
│   │   ├── chunking.py
│   │   └── enrichment.py       # e.g. keywords, summaries, metadata
│   ├── agents/                 # e.g. query optimizer, source identifier, etc.
│   │   ├── pre_agents.py
│   │   └── post_agents.py
│   └── generation/
│       ├── llm_interface.py     # wrapper around the LLM (OpenAI, etc.)
│       └── prompt_templates.py
├── slack_listener/             # your Slack bot and file handling
│   ├── listener.py             # the SlackListener class
│   ├── file_handlers.py        # logic for handling file metadata / downloads
│   └── slack_config.py         # loading tokens, Slack-specific utilities
├── tests/
│   ├── unit/
│   │   ├── test_retrieval.py
│   │   └── test_listener.py
│   └── integration/
│       └── test_full_rag_flow.py
├── scripts/
│   ├── data_ingest.py          # one-off loading of docs
│   └── evaluate.py             # scripts to evaluate with golden sets
├── requirements.txt
├── Dockerfile
├── .env.example
└── README.md

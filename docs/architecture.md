# dobby-ai-slack-agent

dobby-ai-slack-agent/            
├── .github/
│   ├── workflows/
│   │   └── ci.yml                  # CI for linting, tests, docker build
│   └── CODEOWNERS
├── aws/                           
│   ├── ecs/                        # ECS / Fargate configs
│   ├── eks/                        # EKS manifests (deployment.yaml, service.yaml)
│   └── ecr/                        # ECR push scripts
├── docs/                          
│   ├── architecture.md
│   ├── flow_diagrams/
│   └── internal_policies.md
├── rag_pipeline/                   
│   ├── retrieval/
│   │   ├── vector_search.py
│   │   └── bm25_retriever.py
│   ├── document_processing/
│   │   ├── loaders/                
│   │   ├── chunking.py
│   │   └── enrichment.py           
│   ├── agents/                     
│   │   ├── pre_agents.py
│   │   ├── post_agents.py
│   │   └── classifier_agent.py     # LangGraph classify node + Jira/update/summarize
│   └── generation/
│       ├── llm_interface.py        
│       └── prompt_templates.py
├── slack_listener/                 
│   ├── listener.py                  # SlackListener class (msg + file handlers)
│   ├── file_handlers.py             # File metadata capture
│   └── slack_config.py              # loads env tokens, helpers
├── tests/
│   ├── unit/
│   │   ├── test_retrieval.py
│   │   ├── test_listener.py
│   │   └── test_classifier.py       # tests for classifier agent intents
│   └── integration/
│       └── test_full_rag_flow.py
├── scripts/
│   ├── data_ingest.py               
│   ├── evaluate.py                  
│   └── debug_local.py               # run SlackListener + echo_query_processor locally
├── requirements.txt                 # slack-bolt, dotenv, requests, langgraph, typing-extensions
├── Dockerfile
├── deployment.yaml                  # Kubernetes deployment spec
├── service.yaml                     # Kubernetes service spec (ClusterIP / LoadBalancer)
├── .env.example                     # sample Slack tokens + bot id
├── main.py                          # entrypoint, wraps SlackListener, debug logging, echo processor
└── README.md

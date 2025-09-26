# CoffeeMate——Your Companion in the Café

## 🌟 Project Overview

**CoffeeMate** is an AI-powered conversational web app designed for café environments. It offers customers an engaging, interactive experience while they enjoy their coffee. Through natural conversation, users can:

- 📚 Learn about coffee origins, brewing methods, culture, and trivia
- 💬 Submit feedback or suggestions directly to café staff
- 🍽️ Get personalized dinner or local food recommendations
- 🎨 Just chat casually for fun — the perfect blend of tech and relaxation

Built with modern web technologies (**Vue**, **Fastapi**) and enhanced by **MCP** and **RAG**, CoffeeAI delivers accurate, context-aware, and delightful conversations.

## 🛠️ Tech Stack

| COMPONENT | TECHNOLOGY                  |
| --------- | --------------------------- |
| Frontend  | Vue 3 + Vite                |
| Backend   | FastAPI (Python)            |
| Database  | MongoDB                     |
| AI Engine | QWEN, MCP Architecture, RAG |

## 🚀 Quick Start

### Prerequisites

- Node.js >= 16
- Python >= 3.10

### Installation & Run

#### 1. Clone the repo & download uv

```bash
git clone https://github.com/Jiansheng-Chen/CoffeeMate.git
pip install uv
```

#### 2. Start the mcp server

```bash
#server 1
cd HowToCook-mcp-master/HowToCook-mcp-master
npm install
npm run build
node build/index.js --transport http --port 8080
#server 2
cd coffee_mcp
uv venv
uv pip install -r requirements.txt
./.venv/Scripts/activate
cat > config.json << 'EOF'
{
    "MCP_NAME": "coffee-mcp",
    "MCP_HOST" : "0.0.0.0",
    "MCP_PORT" : "8001",
    "API_KEY" : "<qwen_embedding_api_key>",
    "BASE_URL" : "<qwen_embedding_base_url, default : https://dashscope.aliyuncs.com/compatible-mode/v1>",
    "EMBEDDING_MODEL" : "<embedding_model, default : text-embedding-v3>"
}
EOF
python main.py
```

#### 3. Start the backend

```bash
cd coffee-fastapi
pip install -r requirements.txt
./venv/Script/activate
cat > ./app/config.json << 'EOF'
{
    "LLM_API_KEY" :  "<your_llm_api_key>",
    "Base_URL" : "<base_url, default : https://dashscope.aliyuncs.com/compatible-mode/v1>",
    "Model" : "<model_name, default : qwen-plus>",
    "MongoDB_URI" : "<your_mongodb_connect_string>",
    "MongoDB_db_name" : "coffee-db",
    "MCP_SERVER" : {
        "howtocook" : "http://localhost:8080/mcp",
        "coffee-mcp" : "http://localhost:8001"
    }
}
uvicorn main:app --host 0.0.0.0 --port 8000
```

#### 4. Start the frontend

```bash
cd coffee-vue
npm install
npm run build
```

## 👀 Website Preview

![image-20250923174156516](https://raw.githubusercontent.com/Jiansheng-Chen/my_picgo/main/image-20250923174156516.png)
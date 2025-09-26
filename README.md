#CoffeeMate——Your Companion in the Café

##🌟 Project Overview

**CoffeeMate** is an AI-powered conversational web app designed for café environments. It offers customers an engaging, interactive experience while they enjoy their coffee. Through natural conversation, users can:

- 📚 Learn about coffee origins, brewing methods, culture, and trivia
- 💬 Submit feedback or suggestions directly to café staff
- 🍽️ Get personalized dinner or local food recommendations
- 🎨 Just chat casually for fun — the perfect blend of tech and relaxation

Built with modern web technologies (**Vue**, **Fastapi**) and enhanced by **MCP** and **RAG**, CoffeeAI delivers accurate, context-aware, and delightful conversations.

##🛠️ Tech Stack

| COMPONENT | TECHNOLOGY                  |
| --------- | --------------------------- |
| Frontend  | Vue 3 + Vite                |
| Backend   | FastAPI (Python)            |
| Database  | MongoDB                     |
| AI Engine | QWEN, MCP Architecture, RAG |

##🚀 Quick Start

###Prerequisites

- Node.js >= 16
- Python >= 3.10

###Installation & Run

####1. Clone the repo & download uv

```bash
git clone https://github.com/your-username/coffee-ai-chat.git
cd coffee-ai-chat
```

####2. Start the mcp server (update later)

```bash
cd HowToCook-mcp-master/HowToCook-mcp-master
npm install
npm run build
node build/index.js --transport http --port 8080
```

####3. Start the backend

```bash
cd coffee-fastapi
pip install -r requirements.txt
./venv/Script/activate
$env:MCP_SERVER="<Mcp server address>"
$env:MongoDB_URI="<MongoDB connect string> please ensure it has a db named 'coffee-db' with collections 'user' and 'dialogue'"
$env:DASHSCOPE_API_KEY="<Your dashscope api key>"
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

####4. Start the frontend

```bash
cd coffee-vue
npm install
npm run dev
```

##👀 Website Preview

![image-20250923174156516](C:\Users\eru\AppData\Roaming\Typora\typora-user-images\image-20250923174156516.png)
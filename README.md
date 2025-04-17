# AI Translator Agent using VideoSDK and OpenAI Realtime API

This project integrates VideoSDK, OpenAI Realtime APIs to create voice assistant. Below are the setup instructions.

### Start with the project

```sh
https://github.com/kashish63/chatbot-using-VideoSDK-and-openai-realtime.git
```

```sh
cd chatbot-using-VideoSDK-and-openai-realtime
```

### Client Setup


   
1. Create a `config.js` file in the `jsclient` folder videoSDK token for creating and joining meeting with:

   ```sh
   TOKEN = your_videosdk_auth_token_here
   ```


Obtain your VideoSDK Auth Token from [app.videosdk.live](https://app.videosdk.live)

### Server Setup (Python FastAPI)

Create Virtual Environment (from project root):

```sh
python -m venv .venv
```

Create a virtual environment:

Install Dependencies:

```sh
pip install -r requirements.txt
```

Create Server Environment File (in project root):

Add these keys to your `.env` file:

```sh
OPENAI_API_KEY=your_openai_key_here
```

🔑 Obtaining API Keys

- **OpenAI**: [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- **VideoSDK Token**: [https://app.videosdk.live](https://app.videosdk.live)

---

### ▶️ Running the Application

Start the Server (From Project Root):

```sh
uvicorn main:app
```

Start the Client (From `/jsclient` Folder):

in jsclient folder click on index.html

---

For more information, check out [docs.videosdk.live](https://docs.videosdk.live).

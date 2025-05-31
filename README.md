# ♟️ Chess Commentary App

An AI-powered real-time chess commentator that observes live chess games, interprets game positions visually, generates expert-level commentary using Azure OpenAI's Vision models, and narrates it through Azure Text-to-Speech.

---

## 🧾 Features

- 🔍 **Visual Game Monitoring** – Uses Selenium to detect chessboard updates via webpage hash comparison.
- 🖼️ **Screenshot Capture** – Captures chessboard state as an image using Selenium and PIL.
- 💬 **Multimodal Commentary** – Sends screenshots to Azure OpenAI Vision model with context-aware prompts.
- 🔊 **Natural Speech Output** – Converts commentary to high-quality audio using Azure Speech Services.
- 🌀 **Asynchronous Pipeline** – Real-time screenshot, inference, and playback using Python's `asyncio`.

---

## 📦 Technical Stack

| Category              | Tech Used                                 |
|----------------------|--------------------------------------------|
| Language              | Python 3.9+                                |
| Environment           | Conda                                      |
| Web Automation        | Selenium                                   |
| Image Processing      | PIL (Pillow)                               |
| Async HTTP            | aiohttp, aiofiles                          |
| Audio Playback        | simpleaudio                                |
| Speech Synthesis      | Azure Cognitive Services (TTS)             |
| Vision Inference      | Azure OpenAI (Vision-enabled deployment)   |

---

## 🚀 Getting Started

### 1. 📁 Clone the Repository

```bash
git clone https://github.com/your-org/chess-commentary-app.git
cd chess-commentary-app
```

### 2. 🐍 Create and Activate Conda Environment

```bash
conda create -n chess-ai python=3.10 -y
conda activate chess-ai
```

### 3. 📦 Install Dependencies

```bash
pip install -r requirements.txt
```

> Make sure you have [ChromeDriver](https://chromedriver.chromium.org/downloads) installed and set the path in your `.env` file.

---

## ⚙️ Configuration

### `.env` File

Create a `.env` file in the root directory with the following keys:

```env
# Azure OpenAI Configuration
OPENAI_API_BASE_URL=https://<your-resource-name>.openai.azure.com
OPENAI_API_KEY=<your-azure-openai-key>
VISION_MODEL_DEPLOYMENT_NAME=your-vision-deployment

# Azure Speech Configuration
AZURE_SPEECH_KEY=<your-speech-key>
AZURE_SPEECH_REGION=<your-region>

# Chess URL & Login (Optional)
CHESS_STREAM_URL=https://www.chess.com/live
CHESS_USERNAME=your-username
CHESS_PASSWORD=your-password

# Chrome Driver
CHROME_DRIVER_PATH=/path/to/chromedriver
```

---

## ☁️ Azure Resource Setup

### 1. 🔑 Provision Azure OpenAI

* Go to [Azure Portal](https://portal.azure.com)
* Search **Azure OpenAI**
* Create a resource with a **vision-capable deployment**
* Deploy `gpt-4o` or similar model under a name (e.g., `vision-commentary`)
* Copy the **API key** and **Endpoint** to `.env`

### 2. 🎙️ Provision Azure Speech Services

* Go to [Azure Portal](https://portal.azure.com)
* Create a **Speech resource**
* Choose a region (e.g., `eastus`, `westeurope`)
* Use the provided **Key** and **Region** in `.env`

---

## ▶️ Running the App

```bash
python main.py
```

> After logging in to Chess.com and pressing Enter, the app will start generating and narrating commentary in real time.

---

## 📁 Directory Structure

```
real-time-chess-commentary-app/
│
├── audio/                     # Output audio files
├── screenshots/               # Captured screenshots
├── .env                       # Environment configuration
├── prompts.py                 # Prompt templates for vision inference
├── main.py                    # Entry point for the app
├── README.md                  # You're here
├── LICENSE                    # Creative Commons Attribution 4.0 License (free to use with required credit)
└── requirements.txt           # Python dependencies
```

---

## 🧠 How It Works

1. Selenium logs into the chess stream URL
2. Screenshots are taken on every board update
3. Image is converted to base64 and sent to Azure OpenAI Vision
4. Commentary is generated using system and user prompts
5. Commentary is converted to speech using Azure Speech
6. Audio is queued and played back using `simpleaudio`

---

## 💡 Future Enhancements

* Add support for FEN/PGN parsing for higher accuracy
* Support multiple voice options and languages
* Stream to Twitch or YouTube with live commentary overlay
* Build a GUI for easy configuration and game monitoring

---

## 📜 License

This project is licensed under the **Creative Commons Attribution 4.0 International (CC BY 4.0)** license.

You are free to:
- **Use** this software and its outputs for any purpose
- **Modify** and **build upon** it
- **Distribute** your own versions

**As long as you:**
- **Give appropriate credit** to the original author(s)
- Link to this license: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- Indicate if changes were made

### 📣 Attribution

If you use this app, its architecture, or commentary outputs in your project, paper, content, or product, please include the following attribution:

> “Chess Commentary App by Sourav Sahu, licensed under CC BY 4.0 – https://github.com/your-repo-url”

We appreciate the citation and recognition. Thank you!

---

## ✨ Credits

Built using:

* [Azure OpenAI](https://azure.microsoft.com/en-us/products/cognitive-services/openai-service)
* [Azure Cognitive Services - Speech](https://learn.microsoft.com/en-us/azure/cognitive-services/speech-service/)
* [Selenium WebDriver](https://www.selenium.dev/)
* [OpenAI Vision Models](https://platform.openai.com/docs/guides/vision)

---

## 🙋‍♂️ Need Help?

Open an issue.

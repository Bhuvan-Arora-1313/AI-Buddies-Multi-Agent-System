# AI Buddies: Multi-Agent System

**AI Buddies** is a multi-agent system that captures real-time user activity from a computer—such as active windows, screenshots, clipboard content, and typed text—and uses a Large Language Model (LLM) to infer what the user is doing (e.g., coding, reading, browsing, idle).  
It was built as part of the **Transactional AI** track at CloudDefense.AI.

---

## 🧠 Features

- 🪟 Detects active window name and running process
- 🖼️ Takes real-time screenshots of the screen
- 📝 Captures visible text via OCR
- 📋 Reads clipboard content and textbox inputs
- 🧠 Uses LLM to interpret user intent (e.g., “user is coding in Python”)
- 📦 Outputs structured JSON logs to the `output/` folder
- 🔒 Local-only, privacy-respecting architecture

---

## 📂 Project Structure

```
ai-buddies-multi-agent-system/
│
├── buddy/                  # Core logic for data capture and context inference
│   ├── capture.py          # Captures system activity
│   ├── analyze.py          # Sends data to the LLM for intent prediction
│   ├── output/             # Stores captured logs and predictions
│   └── ...
│
├── main.py                 # Entry point to run the system
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

---

## 🚀 Getting Started

### 1. Clone the Repo

```bash
git clone https://github.com/Bhuvan-Arora-1313/ai-buddies-multi-agent-system.git
cd ai-buddies-multi-agent-system
```

### 2. Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Make sure you have the following installed on your system:
- `Tesseract OCR` (for extracting text from screenshots)
- `Pillow`, `pyautogui`, `pyperclip`, etc.

On macOS, you can install Tesseract via:
```bash
brew install tesseract
```

---

## 🧪 Running the System

```bash
python main.py
```

This will:
- Continuously monitor user activity
- Store the logs in `buddy/output/activity_log.json`
- Print and optionally speak the interpreted intent

---

## 🧰 Sample Output (JSON)

```json
{
  "timestamp": "2025-07-09T10:13:15",
  "window_title": "Visual Studio Code - main.py",
  "visible_text": "def get_active_window_title()",
  "predicted_intent": "The user is coding in Python using VS Code"
}
```

---

## 🛡️ Privacy Note

This project runs **entirely locally** and does **not upload any data** to external servers. All captured data is stored only in the `output/` folder.

---

## 📌 Future Improvements

- Web-based UI for live intent tracking
- Custom LLM fine-tuning for better context understanding
- Role-based agent actions (e.g., note-taking, auto-saving code, break reminders)

---

## 📜 License

This project is open-source under the [MIT License](LICENSE).

---

## 🙌 Acknowledgements

Built as part of the **CloudDefense.AI Summer Internship 2025**, under the Transactional AI track by the AI Buddies team.

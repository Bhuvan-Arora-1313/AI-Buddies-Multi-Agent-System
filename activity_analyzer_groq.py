import json
import time
import os
from typing import Dict, Any, List
import subprocess
from groq import Groq
from dotenv import load_dotenv
from shared_state import set_paused, is_paused
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

LIVE_PATH = "output/live_output.json"
PREDICT_PATH = "output/prediction_output.json"

def read_latest_user_data() -> Dict[str, Any]:
    try:
        with open(LIVE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def get_all_user_data_files() -> List[str]:
    try:
        return sorted([f for f in os.listdir("output") if f.startswith("user_data_")])
    except:
        return []

def read_user_data_file(filename: str) -> Dict[str, Any]:
    try:
        with open(f"output/{filename}", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}
def delete_all_user_data_files():
    folder = "output"
    for filename in os.listdir(folder):
        if filename.startswith("user_data"):
            filepath = os.path.join(folder, filename)
            try:
                os.remove(filepath)
                print(f"🗑️ Deleted: {filepath}")
            except Exception as e:
                print(f"⚠️ Could not delete {filepath}: {e}")
def analyze_user_activity_from_json(user_data: Dict[str, Any]) -> Dict[str, Any]:
    if not user_data:
        return {
            "activity": "unknown",
            "confidence": 0.0,
            "description": "No user data available",
            "timestamp": time.time()
        }

    active_window = user_data.get("active_window", "")
    focused_text = user_data.get("focused_text", "")
    clipboard_content = user_data.get("clipboard", "")
    ocr_text = user_data.get("ocr_text", "")
    combined_text = f"""
Active Window: {active_window}
Focused Text: {focused_text}
Clipboard: {clipboard_content}
Screen OCR: {ocr_text}
    """.strip()

    system_prompt = """You are an AI assistant that analyzes user activity data to classify the user's current task.

Return only valid JSON with:
- activity
- confidence
- description
- details
- data_sources
- timestamp

Activity categories:
- coding, researching, browsing, emailing, messaging, gaming, watching, writing, designing, working, unknown

Example:
{
  "activity": "researching",
  "confidence": 0.91,
  "description": "User is reading documentation and Wikipedia in Chrome",
  "details": "Tabs include VS Code docs, Wikipedia",
  "data_sources": "Active Window, Screen OCR",
  "timestamp": 1724384851.153
}"""

    user_prompt = f"Here's the user data:\n{combined_text}\n\nClassify the user's activity."

    try:
        response = client.chat.completions.create(
            model="mistral-saba-24b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.4
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```json"):
            content = content.split("```json")[1].split("```")[0].strip()
        elif content.startswith("```"):
            content = content.split("```")[1].split("```")[0].strip()

        parsed = json.loads(content)
        parsed["timestamp"] = time.time()
        return parsed
    except Exception as e:
        return {
            "activity": "unknown",
            "confidence": 0.0,
            "description": f"Error: {e}",
            "details": "",
            "data_sources": "groq API failure",
            "timestamp": time.time()
        }

def analyze_historical_data(n=5):
    files = get_all_user_data_files()[-n:]
    results = []
    for f in files:
        data = read_user_data_file(f)
        result = analyze_user_activity_from_json(data)
        result["source_file"] = f
        results.append(result)
    return results

def main():
    print("🟢 Groq Activity Monitor Running...")
    print("Model: mixtral-8x7b-32768")

    gather_proc = subprocess.Popen(["python", "gatheruserdata.py"])
    print(f"Started gatheruserdata.py [PID {gather_proc.pid}]")

    last_ts = None
    try:
        while True:
            while is_paused():
                print("⏸️ Paused... Skipping prediction.")
                time.sleep(1)


            user_data = read_latest_user_data()
            if user_data.get("timestamp") != last_ts:
                last_ts = user_data.get("timestamp")
                result = analyze_user_activity_from_json(user_data)
                print("🧠 Prediction:", json.dumps(result, indent=2))
                with open(PREDICT_PATH, "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=2)
            time.sleep(10)
            delete_all_user_data_files()
    except KeyboardInterrupt:
        print("Stopping monitor...")
    finally:
        gather_proc.terminate()
        gather_proc.wait(timeout=3)
        print("✅ gatheruserdata.py stopped.")

if __name__ == "__main__":
    main()
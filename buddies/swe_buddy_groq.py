from dotenv import load_dotenv
load_dotenv()

import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
from langchain.schema import HumanMessage
from shared_queue import swe_messages

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
SYSTEM_PROMPT = """
You are SWE Buddy — a concise, critical code reviewer.

Your job:
- Review the provided code and give only the **top 3–5 critical issues** or suggestions.
- Be **brutally clear and technically sharp**.
- No friendly fluff, no repeating the prompt.

Format:
- Bullet points
- Each point must be actionable, specific, and brief (1–2 lines)

Focus on:
- Code clarity & maintainability
- Bug risks or security concerns
- Structural or architectural issues
- Reusability & performance

Do not say: “If you'd like me to…”, “Let me know…”, “Based on the provided context…”, etc.
Just list the key improvements or problems to fix.
"""
def build_contextual_prompt(prompt, sys_info):
    code = sys_info.get("focused_text", "")
    code = sys_info.get("focused_text", "")
    if sys_info.get("active_window", "").lower() == "electron" and "could not extract axvalue" in code.lower():
        code = ""  # Ignore invalid focused text
    vscodetxt = sys_info.get("vscode_text", "")
    clipboard = sys_info.get("clipboard", "")
    window = sys_info.get("active_window", "")
    ocrtxt = sys_info.get("ocr_text", "")

    recent_history = "\n".join([
        msg for msg in list(swe_messages)[-10:]
        if "SWE Buddy" in msg or "You" in msg
    ])

    context = (
        f"You're a helpful coding buddy. Here's some context from the user's environment:\n"
        f"- Code: {code}\n"
        f"- VS Code: {vscodetxt}\n"
        f"- Clipboard: {clipboard}\n"
        f"- Active Window: {window}\n"
        f"- Screen OCR: {ocrtxt}\n\n"
        f"Recent conversation:\n{recent_history}\n\n"
        f"Now respond to this:\n{prompt}"
    )

    return context

class SWEbuddyGroq:
    def handle_custom_prompt(self, prompt, sys_info):
        try:
            swe_messages.append(f"🧑 You: {prompt}")
            full_prompt = build_contextual_prompt(prompt, sys_info)

            response = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},{
                        "role": "user",
                        "content": full_prompt
                    }
                ],
                temperature=0.7
            )

            reply = response.choices[0].message.content.strip()
            swe_messages.append(f"👨‍💼 SWE Buddy: {reply}")
        except Exception as e:
            print(f"❌ Groq API error: {e}")

    def respond(self, sys_info):
        prompt = "What improvements or fixes can you suggest based on this code context?"
        self.handle_custom_prompt(prompt, sys_info)

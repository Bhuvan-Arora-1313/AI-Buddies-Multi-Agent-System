from dotenv import load_dotenv
load_dotenv()

import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
from shared_queue import pa_messages

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
SYSTEM_PROMPT = """
You are PA Buddy, a sharp, no-nonsense assistant. Your job is to help the user by adding value fast.

Guidelines:
- Always respond in **clean, concise bullet points**.
- Focus on **useful, factual, actionable** info — not fluff.
- Adapt based on what the user seems to be doing (writing, reading, coding, researching, etc.).

What to include:
- 🧠 Smart rephrasings (if user is writing something)
- 🔍 Interesting insights or deeper context (if user is reading/watching)
- 🛠 Suggestions or next steps (if user is working/coding)
- 📊 Surprising facts, stats, or historical/cultural links (if relevant)

What to avoid:
- ❌ Don’t say “you seem to be...”
- ❌ No greetings, opinions, or filler
- ✅ Just get to the point with bullet points

Tone:
- Brief, helpful, professional
- No extra commentary
-NEVER EVER IN YOUR LIFE TELL ME WHAT I AM DOING - I KNOW WHAT I AM DOING DARE YOU TELL ME WHAT I AM DOING
"""
def build_pa_prompt(activity, text, window, ocrtxt, clipboard):
    context_parts = []

    # Focused text is always useful
    if text:
        context_parts.append(f"📝 Focused Text:\n{text}")

    # Add context conditionally
    if activity in ["researching", "browsing", "watching"]:
        if window:
            context_parts.append(f"🪟 Active Window:\n{window}")
        if ocrtxt:
            context_parts.append(f"🔍 OCR:\n{ocrtxt}")
        if clipboard:
            context_parts.append(f"📋 Clipboard:\n{clipboard}")
    elif activity in ["messaging", "emailing", "writing"]:
        # Avoid distractions — keep it focused
        pass
    else:
        if window:
            context_parts.append(f"🪟 Active Window:\n{window}")
        if clipboard:
            context_parts.append(f"📋 Clipboard:\n{clipboard}")

    common_context = "\n\n".join(context_parts)

    if activity == "researching":
        task = "Summarize the key historical themes and points you think I'm exploring. Talk to me like a buddy."
    elif activity == "messaging":
        task = "Based on the focused text, give me a better, cleaner version of the message I'm typing — something I can copy-paste. Make it casual and effective."
    elif activity == "emailing":
        task = "Based on the focused text, rewrite my email to make it clearer and more professional. Keep it short and polished — something I can copy and send."
    elif activity == "writing":
        task = "Rewrite or complete what I’m writing in a clearer, more engaging, and friendly tone. Just give the improved text I can copy."
    elif activity == "designing":
        task = "Give creative feedback based on what you see. Be casual and helpful."
    elif activity == "browsing":
        task = "Based on what I’m reading, give me the most important, lesser-known, or high-impact facts related to the topic. Be direct and avoid summaries — just tell me what matters."
    elif activity == "watching":
        task = "Tell me what might be interesting about what I’m watching. Be a chill buddy."
    elif activity == "working":
        task = "Suggest next steps casually, based on what it looks like I’m working on."
    else:
        task = "Summarize what I'm doing based on the screen. Talk to me casually, like a friend helping out."

    prompt = (
        "you are PA , be formal and factual and bullet points only , otherwise you are dead\n\n"
        + common_context +
        "🎯 Task:\n" + task + "\n\n"
        "Just keep it short — 3–5 lines. Be helpful and avoid repeating what’s already visible."
    )

    return prompt

class PersonalAssistantBuddyGroq:
    def handle_custom_prompt(self, prompt, sys_info):
        try:
            pa_messages.append(f"🧑 You: {prompt}")
            history = "\n".join([msg for msg in list(pa_messages)[-10:] if "PA Buddy" in msg or "You" in msg])
            full_prompt = f"Here's our conversation so far:\n{history}\n\nNow help me with this:\n{prompt}"

            chat = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ]
            )

            reply = chat.choices[0].message.content.strip()
            pa_messages.append(f"🤖 PA Buddy: {reply}")

        except Exception as e:
            print("❌ Groq API error:", e)

    def summarize_contextually(self, sys_info, activity):
        text = sys_info.get("focused_text", "")
        window = sys_info.get("active_window", "")
        ocrtxt = sys_info.get("ocr_text", "")
        clipboard = sys_info.get("clipboard", "")

        prompt = build_pa_prompt(activity, text, window, ocrtxt, clipboard)

        try:
            chat = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ]
            )

            reply = chat.choices[0].message.content.strip()
            print("💡 PA Buddy (Groq) Response:\n", reply)
            pa_messages.append(f"🤖 PA Buddy: {reply}")

        except Exception as e:
            print("❌ Groq API error:", e)

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
from shared_queue import pa_messages
load_dotenv()
import os
os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_BUDDY_API_KEY")



llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.7
)



def build_pa_prompt(activity, text, window, ocrtxt, clipboard):
    common_context = (
        f"📝 Main text:\n{text}\n\n"
        f"🪟 Active window:\n{window}\n\n"
        f"🔍 OCR:\n{ocrtxt}\n\n"
        #f"📋 Clipboard:\n{clipboard}\n\n"
    )

    if activity == "researching":
        task = "Read the content and highlight the key points the user is likely reading or focusing on. Speak in first person, like you're talking *to the user*. Avoid saying 'The user'."
    elif activity == "messaging":
        task = "Suggest how the user can rephrase their message better. Speak in a casual tone and talk to the user directly."
    elif activity == "emailing":
        task = "Help the user improve their email's clarity and tone. Speak in first person, addressing the user."
    elif activity == "writing":
        task = "Suggest better ways to express the current content. Be friendly and direct."
    elif activity == "designing":
        task = "Extract creative ideas from the screen and offer suggestions. Keep it casual and creative."
    elif activity == "browsing":
        task = "If any content is meaningful, summarize it. Speak in a buddy tone directly to the user."
    elif activity == "watching":
        task = "Try to figure out what the user is watching and mention anything interesting or relevant."
    elif activity == "working":
        task = "Offer insights into what the user might be doing and suggest the next step casually."
    else:
        task = "Summarize what the user seems to be reading or writing. Be brief and speak in first person to the user."

    prompt = (
        "You're a helpful personal assistant buddy. Based on the following context, respond as if you're directly talking to the user.\n\n"
        + common_context +
        "🎯 Task:\n" + task + "\n\n"
        "Keep your response short — just 3–5 lines. Be clear, casual, and avoid repeating the context."
    )

    return prompt

class PersonalAssistantBuddy:
    def handle_custom_prompt(self, prompt, sys_info):
        try:
            from shared_queue import pa_messages

            # Append user prompt
            pa_messages.append(f"🧑 You: {prompt}")

            # Get message history (last 10)
            history = "\n".join([msg for msg in list(pa_messages)[-10:]])

            # System context
            code = sys_info.get("focused_text", "")
            window = sys_info.get("active_window", "")
            clipboard = sys_info.get("clipboard", "")
            ocrtxt = sys_info.get("ocr_text", "")

            system_context = (
                f"🧠 System Context:\n"
                f"• Focused Text:\n{code}\n\n"
                f"• Active Window:\n{window}\n\n"
                f"• Clipboard:\n{clipboard}\n\n"
                f"• OCR Text:\n{ocrtxt}\n"
            )

            full_prompt = (
                f"{system_context}\n"
                f"💬 Recent Conversation:\n{history}\n\n"
                f"🧑 User's New Prompt:\n{prompt}\n\n"
                f"👉 Please respond helpfully like a chill, friendly assistant buddy. Be short, clear, and relevant."
            )

            response = self.llm.invoke([HumanMessage(content=full_prompt)])
            pa_messages.append(f"🤖 PA Buddy: {response.content.strip()}")

        except Exception as e:
            print(f"❌ Gemini API error (PA Buddy): {e}")

    def summarize_contextually(self, sys_info, activity):
        print(f"🧠 [PA Buddy] summarize_contextually triggered for activity: {activity}")

        prompt = (
            "Hey buddy! Based on what I'm reading right now, can you help me out?\n\n"
            "👉 Just give me a **quick, chill summary** of the key stuff — like the main ideas, historical events, or cool facts.\n"
            "Skip the obvious stuff I can already see on the screen. Talk to me like a friend helping me revise.\n\n"
            f"📚 Here's what's on my screen:\n\n"
            f"🪟 Active Window: {sys_info.get('active_window')}\n\n"
            f"📋 Clipboard: {sys_info.get('clipboard')}\n\n"
            f"🖥 OCR Snapshot: {sys_info.get('ocr_text')}\n\n"
        )

        try:
            response = llm.invoke([HumanMessage(content=prompt)])
            from shared_queue import pa_messages
            if response and response.content:
                print("💬 [PA Buddy] Response generated")
                pa_messages.append(f"🤖 PA Buddy: {response.content.strip()}")
            else:
                print("⚠️ [PA Buddy] No response content.")
        except Exception as e:
            print(f"❌ [PA Buddy] Gemini API error: {e}")



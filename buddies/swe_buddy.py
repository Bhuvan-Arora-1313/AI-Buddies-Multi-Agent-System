
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
from shared_queue import swe_messages
load_dotenv()
import os
os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_BUDDY_API_KEY")




llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.7
)


class SWEbuddy:
    def handle_custom_prompt(self, prompt, sys_info):
        try:
            from shared_queue import swe_messages

            # Append user input
            swe_messages.append(f"🧑 You: {prompt}")

            # Build history (up to 10 latest messages)
            history = "\n".join([msg for msg in list(swe_messages)[-10:]])

            # Add system context (real-time info)
            code = sys_info.get("focused_text", "")
            if sys_info.get("active_window", "").lower() == "electron" and "could not extract axvalue" in code.lower():
                code = ""  # Ignore invalid focused text
            window = sys_info.get("active_window", "")
            clipboard = sys_info.get("clipboard", "")
            vscodetxt = sys_info.get("vscode_text", "")
            ocrtxt = sys_info.get("ocr_text", "")

            # Build system context section
            system_context = (
                f" System Context:\n"
                f" Focused Code:\n{code}\n\n"
                f" VS Code Text:\n{vscodetxt}\n\n"
                f" Active Window:\n{window}\n\n"
                f" Clipboard:\n{clipboard}\n\n"
                f" OCR Text:\n{ocrtxt}\n"
            )

            # Final full prompt
            full_prompt = (
                f"{system_context}\n"
                f"💬 Recent Conversation:\n{history}\n\n"
                f"🧑 User's New Prompt:\n{prompt}\n\n"
                f"👉 Now respond with coding advice like a chill dev buddy. Be concise and developer-friendly."
            )

            response = llm.invoke([HumanMessage(content=full_prompt)])

            # Append assistant response
            swe_messages.append(f"👨‍💻 SWE Buddy: {response.content.strip()}")

        except Exception as e:
            print(f"❌ Gemini API error: {e}")
    def respond(self, sys_info):
        code = sys_info.get("focused_text", "")
        if not code.strip():
            print("👨‍💻 You're coding, but no code was captured yet.")
            return
        window=sys_info.get("active_window","")
        clipboard=sys_info.get("clipboard","")
        vscodetxt=sys_info.get("vscode_text","")
        ocrtxt=sys_info.get("ocr_text","")

        print("🧠 SWE Buddy activated. Sending code to Gemini...")

        # prompt = (
        #     f"You are a helpful coding assistant. "
        #     f"Here is some code the user is writing:\n\n{code}\n\n"
        #     f"if user is using vs code for writing code , the text will be available in variable vscodetxt it contents are : \n\n{vscodetxt}\n\n"
        #     f"the active window that the user is working on is : \n\n{window}\n\n"
        #     f"the ocr of the users screen is as follows :\n\n{ocrtxt}\n\n you can use this ocr to infer context"
        #     f"you can use the clipboard content also if required to infer the context , it is as follows : \n\n{clipboard}\n\n"
        #
        #     f"Please suggest improvements, detect bugs, or add docstrings if missing."
        # )
        prompt = (
            "You're an intelligent but chill coding buddy. Read everything below — the user is coding and debugging.\n"
            "Give 1-2 sharp, useful suggestions. Be concise. Talk like a dev.\n\n"

            f"Code:\n{code}\n\n"
            f"VS Code text:\n{vscodetxt}\n\n"
            f"Clipboard:\n{clipboard}\n\n"
            f"Active Window:\n{window}\n\n"
            f"Screen OCR:\n{ocrtxt}\n\n"

            "Now reply like a buddy — suggest code improvements, flag bugs, or help with what looks confusing."
        )

        try:
            response = llm.invoke([HumanMessage(content=prompt)])
            if response and response.content:
                print("💬 Gemini's response:")
                print(response.content.strip())
                swe_messages.append(response.content.strip())
            else:
                print("⚠️ Gemini returned no content.")
        except Exception as e:
            print(f"❌ Gemini API error: {e}")



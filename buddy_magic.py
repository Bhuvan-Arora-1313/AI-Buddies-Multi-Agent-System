import time
import json
from buddies.personal_assistant import PersonalAssistantBuddy
from buddies.swe_buddy import SWEbuddy
from shared_queue import swe_messages, pa_messages, swe_inputs, pa_inputs


LIVE_OUTPUT_PATH = "output/live_output.json"
PREDICTION_OUTPUT_PATH = "output/prediction_output.json"

def read_prediction():
    try:
        with open(PREDICTION_OUTPUT_PATH, "r") as f:
            data = json.load(f)
            return data.get("activity", "").lower()
    except Exception as e:
        print(f"[Error reading prediction] {e}")
        return None

def read_system_info():
    try:
        with open(LIVE_OUTPUT_PATH, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Error reading system info] {e}")
        return {}

def run_buddy_system():
    pab = PersonalAssistantBuddy()
    swe = SWEbuddy()
    last_prediction = None
    last_trigger_time = 0

    print("🔁 Buddy system is now running...")

    while True:
        prediction = read_prediction()
        sys_info = read_system_info()

        if prediction:
            print(f"\n🧠 Predicted activity: {prediction}")
            print(f"⏱ Time since last trigger: {time.time() - last_trigger_time:.1f} seconds")

        if prediction and (prediction != last_prediction or time.time() - last_trigger_time > 60):
            print(f"⚡ Triggering buddy for activity: {prediction}")
            last_trigger_time = time.time()

            if prediction == "coding":
                swe.respond(sys_info)
            elif prediction == "idle":
                pab.remind_break()
            else:
                pab.summarize_contextually(sys_info, prediction)

            last_prediction = prediction

        if swe_inputs:
            user_prompt = swe_inputs.popleft()
            swe.handle_custom_prompt(user_prompt, sys_info)

        if pa_inputs:
            user_prompt = pa_inputs.popleft()
            pab.handle_custom_prompt(user_prompt, sys_info)

        time.sleep(5)

        if swe_inputs:
            user_prompt = swe_inputs.popleft()
            swe.handle_custom_prompt(user_prompt,sys_info)
            last_prediction = None  # ✅ Reset prediction trigger

        if pa_inputs:
            user_prompt = pa_inputs.popleft()
            pab.handle_custom_prompt(user_prompt,sys_info)
            last_prediction = None  # ✅ Reset prediction trigger


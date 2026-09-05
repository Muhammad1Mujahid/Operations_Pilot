import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def suggest_root_cause(incident_type, severity, server, value):
    prompt = f"""You are an IT operations assistant. An automated monitoring
system just opened this incident:

Type: {incident_type}
Severity: {severity}
Server: {server}
Value: {value}%

Give a short, realistic likely root cause (1-2 sentences), and a short
suggested fix (1-2 sentences). Be specific and practical, not generic.
Respond in exactly this format:

CAUSE: <your answer>
FIX: <your answer>
"""

    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt
        )
        text = response.text

        cause = ""
        fix = ""
        for line in text.splitlines():
            if line.startswith("CAUSE:"):
                cause = line.replace("CAUSE:", "").strip()
            elif line.startswith("FIX:"):
                fix = line.replace("FIX:", "").strip()

        return cause, fix

    except Exception as e:
        print(f"AI suggestion failed: {e}")
        return "", ""
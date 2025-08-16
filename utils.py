import tempfile
from datetime import datetime
from fpdf import FPDF
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
from prompts import SYSTEM_PROMPT, VARIATION_PROMPTS

MODEL_ID = "google/flan-t5-base"

print(f"Loading model {MODEL_ID}...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_ID)

def call_model(prompt: str, max_new_tokens: int = 150):
    """Run local inference with transformers instead of API."""
    try:
        inputs = tokenizer(prompt, return_tensors="pt")
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            num_beams=4,
            early_stopping=True
        )
        text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return text, None
    except Exception as e:
        return None, f"Local inference error: {str(e)}"

# utils.py

FIELDS = ["Habit", "Why", "Measure", "Schedule", "Start date", "Success criteria"]

def build_prompt(user_goal: str, variant_key: str) -> str:
    """
    Few-shot + strict format. Short by design so small models follow it.
    Ending with 'Habit:' nudges the model into the right structure.
    """
    variation = VARIATION_PROMPTS[variant_key]
    return (
        "Rewrite a vague goal into ONE SMART habit plan.\n"
        "Output all fields exactly once and do NOT copy the user's sentence.\n\n"
        "Example 1\n"
        "Goal: be healthier\n"
        "Habit: Walk 8,000 steps daily and add 2 servings of vegetables to lunch.\n"
        "Why: Daily movement and better diet improve health.\n"
        "Measure: Steps from a phone/app; servings logged.\n"
        "Schedule: Every day at lunch and evening.\n"
        "Start date: Next Monday.\n"
        "Success criteria: 80% compliance for 8 weeks.\n\n"
        "Example 2\n"
        "Goal: study more\n"
        "Habit: Study 25 minutes with 5-minute breaks, 4 sessions per weekday.\n"
        "Why: Short focused blocks improve retention.\n"
        "Measure: Sessions per day in a tracker.\n"
        "Schedule: Mon–Fri, 18:00–20:00.\n"
        "Start date: Tomorrow.\n"
        "Success criteria: 80 sessions in 1 month.\n\n"
        f"Style: {variation}\n"
        f"Goal: {user_goal}\n"
        "Habit: "
    )
import re
from typing import Tuple

MAX_GOAL_CHARS = 280  # keep prompts compact for small/medium models
MIN_GOAL_TOKENS = 2   # reject single-word inputs like "weight"

CTRL_CHARS = ''.join(map(chr, list(range(0,9))+[11,12]+list(range(14,32))+[127]))
CTRL_RE = re.compile(f"[{re.escape(CTRL_CHARS)}]")

def preprocess_goal(raw: str) -> Tuple[bool, str]:
    """
    Clean and validate the user's goal text.
    Returns (ok, cleaned_or_error_message).
    """
    if raw is None:
        return False, "Please enter a goal."

    # Remove control characters, normalize spaces, trim
    text = CTRL_RE.sub("", raw)
    text = re.sub(r"\s+", " ", text).strip()

    if not text:
        return False, "Please enter a goal."

    # Very short / ambiguous goals — still allow, but ensure at least two tokens
    if len(text.split()) < MIN_GOAL_TOKENS:
        return False, "Please add a few more words so I understand your goal."

    # Cap length to avoid huge prompts
    if len(text) > MAX_GOAL_CHARS:
        text = text[:MAX_GOAL_CHARS].rstrip() + "…"

    return True, text


def clean_output(text: str) -> str:
    """
    Keep only SMART fields; tolerate partial/odd formatting from the model.
    """
    # Keep only from first "Habit:" to cut prompt echo
    i = text.lower().find("habit:")
    if i != -1:
        text = text[i:]
    text = text.strip()

    # Extract each field until next field or end (case-insensitive, multiline)
    normalized = {k: "" for k in FIELDS}
    field_union = "|".join(re.escape(k) for k in FIELDS)
    for k in FIELDS:
        pattern = rf"{k}:\s*(.*?)(?=\n(?:{field_union}):|\Z)"
        m = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
        if m:
            normalized[k] = re.sub(r"\s+\n", "\n", m.group(1).strip())

    # If everything came back empty, return a skeleton so the UI isn't blank
    if not any(normalized.values()):
        return "\n".join(f"{k}:" for k in FIELDS)

    # Reassemble in canonical order
    return "\n".join(f"{k}: {normalized[k]}" for k in FIELDS).strip()
def generate_variations(user_goal: str):
    """
    Returns a list [v1, v2, v3] of SMART habit variants.
    """
    ok, goal_or_msg = preprocess_goal(user_goal)
    if not ok:
        return [goal_or_msg] * 3

    versions = []
    for key in ("v1", "v2", "v3"):
        prompt = build_prompt(goal_or_msg, key)
        text, err = call_model(prompt)
        versions.append(clean_output(text) if text else f"Error generating {key}: {err}")
    return versions

def export_pdf(text: str):
    """
    Create a simple PDF from the current editable output.
    Returns a temp file path for Gradio to serve as a download.
    """
    if not text or not text.strip():
        text = "No content to export"

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "SMART Habit Plan", ln=True)

    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 8, f"Exported {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
    pdf.ln(4)

    pdf.set_font("Arial", "", 12)
    for line in text.splitlines():
        pdf.multi_cell(0, 8, line)

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(tmp.name)
    return tmp.name
import tempfile
from datetime import datetime
from fpdf import FPDF
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

MODEL_ID = "google/flan-t5-large"

print(f"Loading model {MODEL_ID}...")
try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_ID)
    print("DEBUG: Model loaded successfully")
except Exception as e:
    print(f"DEBUG: Error loading model: {e}")
    tokenizer = None
    model = None

def call_model(prompt: str, max_new_tokens: int = 150):
    """Run local inference with transformers instead of API."""
    print(f"DEBUG: call_model called with prompt length: {len(prompt)}")
    
    if tokenizer is None or model is None:
        print("DEBUG: Model not loaded, returning error")
        return None, "Model not loaded properly"
    
    try:
        inputs = tokenizer(prompt, return_tensors="pt")
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            num_beams=4,
            early_stopping=True
        )
        text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"DEBUG: Model returned: '{text}'")
        return text, None
    except Exception as e:
        print(f"DEBUG: Model error: {str(e)}")
        return None, f"Local inference error: {str(e)}"

# utils.py

FIELDS = ["Habit", "Why", "Measure", "Schedule", "Start date", "Success criteria"]

def build_prompt(user_goal: str, variant_key: str) -> str:
    """
    Simple, direct prompt for FLAN-T5-Base model.
    """
    return f"Create a specific habit for {user_goal}. What should I do?"
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
    print(f"DEBUG: clean_output called with: '{text}'")
    
    # Keep only from first "Habit:" to cut prompt echo
    i = text.lower().find("habit:")
    if i != -1:
        text = text[i:]
    text = text.strip()
    print(f"DEBUG: After finding 'habit:': '{text}'")

    # Extract each field until next field or end (case-insensitive, multiline)
    normalized = {k: "" for k in FIELDS}
    field_union = "|".join(re.escape(k) for k in FIELDS)
    for k in FIELDS:
        pattern = rf"{k}:\s*(.*?)(?=\n(?:{field_union}):|\Z)"
        m = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
        if m:
            normalized[k] = re.sub(r"\s+\n", "\n", m.group(1).strip())
    
    print(f"DEBUG: Normalized fields: {normalized}")

    # If everything came back empty, return a skeleton so the UI isn't blank
    if not any(normalized.values()):
        print("DEBUG: No fields found, returning skeleton")
        return "\n".join(f"{k}:" for k in FIELDS)

    # Reassemble in canonical order
    result = "\n".join(f"{k}: {normalized[k]}" for k in FIELDS).strip()
    print(f"DEBUG: Final result: '{result}'")
    return result


def generate_variations(user_goal: str):
    """
    Returns a list [v1, v2, v3] of SMART habit variants.
    """
    print(f"DEBUG: generate_variations called with: '{user_goal}'")
    ok, goal_or_msg = preprocess_goal(user_goal)
    print(f"DEBUG: preprocess_goal result: ok={ok}, goal='{goal_or_msg}'")
    if not ok:
        return [goal_or_msg] * 3

    versions = []
    for key in ("v1", "v2", "v3"):
        print(f"DEBUG: Generating {key}...")
        version = generate_complete_smart_habit(goal_or_msg, key)
        versions.append(version)
    return versions

def generate_complete_smart_habit(goal: str, variant: str) -> str:
    """
    Generate a complete SMART habit using a single, comprehensive prompt.
    """
    print(f"DEBUG: Generating complete SMART habit for variant {variant}")
    
    # Create a single, comprehensive prompt for the entire SMART habit
    if variant == "v1":
        prompt = f"""Create a SMART habit plan for: {goal}

Generate a simple, straightforward approach. Be specific and actionable.

Habit: [specific action to take]
Why: [explain why this helps]
Measure: [how to track progress]
Schedule: [when to do it]
Start date: [when to start]
Success criteria: [how to know you're succeeding]

Fill in each field with specific, actionable content:"""
    
    elif variant == "v2":
        prompt = f"""Create an alternative SMART habit plan for: {goal}

Generate a different approach from the usual. Think outside the box.

Habit: [alternative action to take]
Why: [explain why this alternative works]
Measure: [how to track progress differently]
Schedule: [alternative timing]
Start date: [when to start]
Success criteria: [alternative success metrics]

Fill in each field with specific, actionable content:"""
    
    elif variant == "v3":
        prompt = f"""Create a creative SMART habit plan for: {goal}

Generate a fun, flexible, and enjoyable approach.

Habit: [creative action to take]
Why: [explain why this is enjoyable and effective]
Measure: [how to track progress in a fun way]
Schedule: [flexible timing]
Start date: [when to start]
Success criteria: [enjoyable success metrics]

Fill in each field with specific, actionable content:"""
    
    # Generate the complete SMART habit
    text, err = call_model(prompt, max_new_tokens=400)
    
    if text and not err:
        # Clean and format the response
        formatted_habit = format_smart_response(text, goal, variant)
        print(f"DEBUG: Generated SMART habit for {variant}: {formatted_habit}")
        return formatted_habit
    else:
        # Fallback to a simple approach
        return generate_simple_fallback(goal, variant)

def format_smart_response(text: str, goal: str, variant: str) -> str:
    """Format the AI response into proper SMART structure."""
    text = text.strip()
    
    # If the response has some structure, try to extract it
    if "habit:" in text.lower():
        # Try to extract structured content
        lines = text.split('\n')
        smart_fields = {
            'habit': '',
            'why': '',
            'measure': '',
            'schedule': '',
            'start date': '',
            'success criteria': ''
        }
        
        current_field = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if this line starts a new field
            for field in smart_fields.keys():
                if line.lower().startswith(field + ':'):
                    current_field = field
                    content = line.split(':', 1)[1].strip() if ':' in line else ''
                    smart_fields[field] = content
                    break
            else:
                # If no new field, append to current field
                if current_field and smart_fields[current_field]:
                    smart_fields[current_field] += ' ' + line
                elif current_field:
                    smart_fields[current_field] = line
        
        # Build the formatted response
        result = []
        for field, content in smart_fields.items():
            if content:
                result.append(f"{field.title()}: {content}")
            else:
                # If field is empty, use fallback
                fallback = get_field_fallback(field, goal, variant)
                result.append(f"{field.title()}: {fallback}")
        
        return '\n'.join(result)
    else:
        # If no structure, use fallback
        return generate_simple_fallback(goal, variant)

def get_field_fallback(field: str, goal: str, variant: str) -> str:
    """Get fallback content for empty fields."""
    if field == 'habit':
        if "weight" in goal.lower() or "lose" in goal.lower():
            if variant == "v1":
                return "Walk 10,000 steps daily and eat 3 servings of vegetables"
            elif variant == "v2":
                return "Replace sugary drinks with water and do strength training 3 times per week"
            elif variant == "v3":
                return "Join a dance class twice per week and cook healthy meals at home"
        elif "read" in goal.lower():
            if variant == "v1":
                return "Read 30 pages every day"
            elif variant == "v2":
                return "Listen to audiobooks during daily commute"
            elif variant == "v3":
                return "Join a book club and read one book per month"
        else:
            return f"Practice {goal} for 30 minutes daily"
    
    elif field == 'why':
        return f"This habit helps achieve {goal} through consistent action"
    
    elif field == 'measure':
        return "Track daily progress and record results"
    
    elif field == 'schedule':
        if variant == "v1":
            return "Every morning at 7 AM"
        elif variant == "v2":
            return "Every evening at 6 PM"
        elif variant == "v3":
            return "3 times per week with flexible timing"
    
    elif field == 'start date':
        return "Tomorrow"
    
    elif field == 'success criteria':
        if variant == "v1":
            return "Maintain this habit for 30 consecutive days"
        elif variant == "v2":
            return "Maintain this habit for 21 days with 80% consistency"
        elif variant == "v3":
            return "Maintain this habit for 6 weeks with flexible scheduling"
    
    return "Track progress regularly"

def generate_simple_fallback(goal: str, variant: str) -> str:
    """Generate a simple fallback when AI fails completely."""
    habit = get_field_fallback('habit', goal, variant)
    why = get_field_fallback('why', goal, variant)
    measure = get_field_fallback('measure', goal, variant)
    schedule = get_field_fallback('schedule', goal, variant)
    start_date = get_field_fallback('start date', goal, variant)
    success_criteria = get_field_fallback('success criteria', goal, variant)
    
    return f"""Habit: {habit}
Why: {why}
Measure: {measure}
Schedule: {schedule}
Start date: {start_date}
Success criteria: {success_criteria}"""




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
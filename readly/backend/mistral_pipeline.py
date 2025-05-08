from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch

model_name = "tiiuae/falcon-rw-1b"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, max_new_tokens=300, temperature=0.5)

def basic_prompt(prompt):
    output = pipe(prompt)[0]["generated_text"]
    return output.strip()

# ---- Step 1: Extract Learning Objectives ----
def extract_objectives(text):
    prompt = f"""
    Extract key learning objectives and break them into smaller teachable units:

    Curriculum:
    {text}

    Return as JSON: [{{"unit": "Unit Title", "objectives": ["Objective 1", "Objective 2"]}}]
    """
    raw = mistral_prompt(prompt)
    try:
        return json.loads(raw)
    except:
        return [{"unit": "Default Unit", "objectives": [text]}]  # fallback if parsing fails

# ---- Step 2: Suggest Activity for Objective ----
def suggest_activities_for_objective(objective):
    prompt = f"""
    Suggest a gamified activity for the learning objective: "{objective}".
    Format as JSON: {{"activity_type": "drag_and_drop", "reason": "why it fits"}}
    """
    raw = mistral_prompt(prompt)
    try:
        return json.loads(raw)
    except:
        return {"activity_type": "quiz", "reason": "default fallback"}

# ---- Step 3: Generate Summary and Questions ----
def generate_content_and_questions(objective):
    prompt = f"""
    Generate a simplified explanation and 3 quiz questions for this learning objective:

    Objective: {objective}

    Format as JSON:
    {{
      "summary": "...",
      "questions": [
        {{"type": "multiple_choice", "question": "...", "options": [...], "answer": "..."}},
        ...
      ]
    }}
    """
    raw = mistral_prompt(prompt)
    try:
        return json.loads(raw)
    except:
        return {"summary": objective, "questions": []}

# ---- Pipeline ----
def generate_lesson_from_curriculum(c_text):
    units = extract_objectives(c_text)
    for unit in units:
        for i, obj in enumerate(unit['objectives']):
            unit['objectives'][i] = {
                "text": obj,
                "activity": suggest_activities_for_objective(obj),
                "content": generate_content_and_questions(obj)
            }
    return units

# Example Run
curriculum_text = """
Students will understand how ecosystems function, including food chains, producers and consumers, and energy flow.
"""

result = generate_lesson_from_curriculum(curriculum_text)
print(json.dumps(result, indent=2))

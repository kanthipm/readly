from flask import Flask, request, jsonify
from mistral_pipeline import generate_lesson_from_curriculum

from flask_cors import CORS

app = Flask(__name__)
CORS(app)   

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    curriculum = data.get("curriculum", "")
    result = generate_lesson_from_curriculum(curriculum)
    return jsonify(result)

if __name__ == "__main__":
    app.run(port=5000, debug=True)

import pickle
import os
import numpy as np
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

# Initialize Flask app with explicit template/static paths so it runs from any CWD
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
)
CORS(app)

# Load the trained model (path relative to this file)
model_path = os.path.join(BASE_DIR, "MMGSY_best_model.pkl")
with open(model_path, "rb") as f:
    model = pickle.load(f)

""" 
Model feature list and CSV input ordering.

- The UI will collect 19 inputs in the exact order of the CSV (excluding
  the unnamed index column and excluding "Actual PCI" which is a label).
- The model, however, only uses 12 features, including an implicit
  "Unnamed: 0" which is always set to 0 for inference.
"""

# 19 input fields in the same order as the CSV header (excluding the initial unnamed index and "Actual PCI")
csv_inputs_order = [
    "Part_length",
    "Carriageway width in m.",
    "Year of construction /upgradation",
    "Study Stretch Chainage",
    "Avg Rain fall",
    "Age of Pavement during Evalution Years ",
    "MDD",
    "OMC",
    "LL",
    "PL",
    "PI",
    "CBR",
    "SCI",
    "SN",
    "MSN",
    "CVPD",
    "evalution_year",
    "evalution_month",
    "evalution_quarter",
]

# Feature order expected by the model (first entry is the implicit index)
model_features = [
    "Unnamed: 0",  # always 0 for inference
    "Carriageway width in m.",
    "Year of construction /upgradation",
    "Study Stretch Chainage",
    "Avg Rain fall",
    "Age of Pavement during Evalution Years ",
    "MDD",
    "PI",
    "SCI",
    "MSN",
    "CVPD",
    "evalution_quarter",
]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json() or {}

        # Validate required 19 inputs exist (in any order; UI sends them all)
        missing_inputs = [name for name in csv_inputs_order if name not in data]
        if missing_inputs:
            return jsonify({"error": f"Missing inputs: {', '.join(missing_inputs)}"}), 400

        # Build model input vector
        input_data = [0.0]  # Unnamed: 0 defaulted to 0
        for feature in model_features[1:]:  # skip the unnamed index already added
            try:
                input_data.append(float(data[feature]))
            except Exception:
                return jsonify({"error": f"Invalid value for '{feature}'"}), 400

        # Reshape for model
        input_array = np.array(input_data).reshape(1, -1)

        # Prediction
        prediction = model.predict(input_array)
        predicted_value = float(prediction[0])

        # Echo back submitted inputs in the CSV order (display-only)
        submitted_inputs = [{"name": name, "value": data.get(name)} for name in csv_inputs_order]

        return jsonify({
            "prediction": predicted_value,
            "inputs": submitted_inputs
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

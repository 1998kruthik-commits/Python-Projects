from flask import Flask, render_template, request
import joblib

app = Flask(__name__)

# Load trained model and imputer
model = joblib.load("models/arrhythmia_model.pkl")
imputer = joblib.load("models/imputer.pkl")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    try:
        values = request.form["features"]

        # Convert comma-separated string to list of floats
        data = [float(x.strip()) for x in values.split(",")]

        # Validate feature count
        if len(data) != 279:
            return render_template(
                "index.html",
                prediction=f"Error: Expected 279 values but got {len(data)}"
            )

        # Apply same preprocessing used during training
        data = imputer.transform([data])

        # Predict
        pred = model.predict(data)[0]

        return render_template(
            "index.html",
            prediction=f"Predicted Arrhythmia Class : {pred}"
        )

    except Exception as e:
        return render_template(
            "index.html",
            prediction=f"Error: {str(e)}"
        )


@app.route("/health")
def health():
    return "OK", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5010)

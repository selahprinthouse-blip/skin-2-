from flask import Flask, render_template_string, request
import pandas as pd
import os

app = Flask(__name__)

# Load Excel
EXCEL_FILE = "skin_clinic_services.xlsx"
df = pd.read_excel(EXCEL_FILE)

# Normalize some data
df['Gender'] = df['Gender'].str.lower()
df['Skin Type'] = df['Skin Type'].str.lower()
df['Skin Problem'] = df['Skin Problem'].str.lower()

# HTML Template (form + results)
HTML_TEMPLATE = """
<!doctype html>
<html>
<head>
    <title>Skin Clinic Service Recommender</title>
</head>
<body>
    <h1>Skin Clinic Service Recommender</h1>
    {% if not results %}
    <form method="POST">
        Age: <input type="number" name="age" required><br><br>
        Gender:
        <select name="gender">
            <option value="male">Male</option>
            <option value="female">Female</option>
        </select><br><br>
        Skin Type:
        <select name="skin_type">
            <option value="normal">Normal</option>
            <option value="dry">Dry</option>
            <option value="oily">Oily</option>
            <option value="combination">Combination</option>
        </select><br><br>
        Skin Problem (comma separated): <input type="text" name="skin_problem"><br><br>
        Budget (PHP): <input type="number" name="budget" required><br><br>
        Location: <input type="text" name="location"><br><br>
        <input type="submit" value="Get Recommendations">
    </form>
    {% else %}
        <h2>Recommended Services:</h2>
        {% if results|length == 0 %}
            <p>No services match your criteria within budget.</p>
        {% else %}
            <ul>
            {% for r in results %}
                <li>{{ r['Service Name'] }} - {{ r['Price (PHP)'] }} PHP</li>
            {% endfor %}
            </ul>
        {% endif %}
        <a href="/">Try Again</a>
    {% endif %}
</body>
</html>
"""

def split_values(cell):
    return [x.strip().lower() for x in str(cell).split(",")]

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        age = int(request.form.get("age", 0))
        gender = request.form.get("gender", "").lower()
        skin_type = request.form.get("skin_type", "").lower()
        skin_problem = request.form.get("skin_problem", "").lower()
        budget = float(request.form.get("budget", 0))
        location = request.form.get("location", "")

        user_problems = [x.strip() for x in skin_problem.split(",") if x.strip()]

        # Scoring
        recommendations = []
        for idx, row in df.iterrows():
            score = 0
            # Gender
            if row['Gender'] == "any" or row['Gender'] == gender:
                score += 1
            # Age
            if row['Min Age'] <= age <= row['Max Age']:
                score += 1
            # Skin Type
            if gender in row['Skin Type'].lower() or skin_type in row['Skin Type'].lower():
                score += 1
            # Skin Problems
            service_problems = split_values(row['Skin Problem'])
            if all(p in service_problems for p in user_problems):
                score += 1
            # Budget
            if row['Price (PHP)'] <= budget:
                score += 1

            if score >= 3:  # Adjust threshold as needed
                recommendations.append(row)

        return render_template_string(HTML_TEMPLATE, results=recommendations)
    return render_template_string(HTML_TEMPLATE, results=None)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd

# -----------------------------
# Load Excel File
# -----------------------------
FILE_PATH = "skin_clinic_services.xlsx"

try:
    df = pd.read_excel(FILE_PATH)
except:
    messagebox.showerror("Error", "Excel file not found")
    exit()

# Normalize text
for col in ["Skin Type", "Skin Problems", "Gender"]:
    df[col] = df[col].str.lower()

# -----------------------------
# Scoring Function
# -----------------------------
def calculate_score(service, gender, age, skin_type, problems, budget):
    score = service["Base Score"]

    # Gender
    if service["Gender"] == "any" or service["Gender"] == gender:
        score += 2

    # Age
    if service["Min Age"] <= age <= service["Max Age"]:
        score += 3
    else:
        return 0

    # Skin Type
    if skin_type in service["Skin Type"]:
        score += 3

    # Skin Problems
    for p in problems:
        if p in service["Skin Problems"]:
            score += 2

    # Budget
    if service["Price_PHP"] > budget:
        return 0

    return score

# -----------------------------
# Recommendation Logic
# -----------------------------
def recommend():
    try:
        age = int(age_entry.get())
        budget = int(budget_entry.get())
    except:
        messagebox.showerror("Input Error", "Age and Budget must be numbers")
        return

    gender = gender_var.get().lower()
    skin_type = skin_var.get().lower()
    problems = [p.lower() for p in problems_listbox.get(0, tk.END) if problems_listbox.selection_includes(problems_listbox.get(0, tk.END).index(p))]
    location = location_var.get()

    results = []

    for _, service in df.iterrows():
        score = calculate_score(service, gender, age, skin_type, problems, budget)
        if score > 0:
            results.append((service["Service Name"], service["Price_PHP"], score))

    results.sort(key=lambda x: x[2], reverse=True)

    result_box.delete(0, tk.END)

    if not results:
        result_box.insert(tk.END, "❌ No suitable services found.")
        return

    result_box.insert(tk.END, f"📍 Nearest Branch: {location}")
    result_box.insert(tk.END, "-" * 40)

    for r in results[:5]:
        result_box.insert(tk.END, f"✔ {r[0]} | {r[1]} PHP | Score: {r[2]}")

# -----------------------------
# GUI
# -----------------------------
root = tk.Tk()
root.title("Skin Clinic Service Recommender")
root.geometry("650x600")

# Gender
tk.Label(root, text="Gender").pack()
gender_var = ttk.Combobox(root, values=["Male", "Female"], state="readonly")
gender_var.pack()

# Age
tk.Label(root, text="Age").pack()
age_entry = tk.Entry(root)
age_entry.pack()

# Skin Type
tk.Label(root, text="Skin Type").pack()
skin_var = ttk.Combobox(root, values=["Normal", "Oily", "Dry", "Combination", "Sensitive"], state="readonly")
skin_var.pack()

# Skin Problems
tk.Label(root, text="Skin Problems (select multiple)").pack()
problems_listbox = tk.Listbox(root, selectmode="multiple", height=6)
for p in ["Acne", "Pigmentation", "Wrinkles", "Dullness", "Redness", "Dehydration"]:
    problems_listbox.insert(tk.END, p)
problems_listbox.pack()

# Budget
tk.Label(root, text="Budget (PHP)").pack()
budget_entry = tk.Entry(root)
budget_entry.pack()

# Location
tk.Label(root, text="Location / City").pack()
location_var = ttk.Combobox(root, values=[
    "Manila Branch",
    "Quezon City Branch",
    "Cavite Branch",
    "Tagaytay Branch"
], state="readonly")
location_var.pack()

# Button
tk.Button(root, text="Recommend Service", command=recommend, bg="#4CAF50", fg="white").pack(pady=10)

# Results
result_box = tk.Listbox(root, width=80, height=12)
result_box.pack()

root.mainloop()

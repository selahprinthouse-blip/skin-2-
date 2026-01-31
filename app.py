import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd

# --------- تحميل ملف Excel ---------
FILE_PATH = "skincare_services.xlsx"  # ضع اسم ملفك هنا
try:
    df = pd.read_excel(FILE_PATH)
except Exception as e:
    messagebox.showerror("Error", f"Cannot load Excel file: {e}")
    exit()

# Normalize text
df['Skin Type'] = df['Skin Type'].astype(str)
df['Skin Problem'] = df['Skin Problem'].astype(str)
df['Gender'] = df['Gender'].astype(str)
df['Service Name'] = df['Service Name'].astype(str)
df['Notes'] = df['Notes'].astype(str)

# --------- إعداد الواجهة ---------
root = tk.Tk()
root.title("Skincare Service Finder")
root.geometry("600x550")

# --- اختيار النوع ---
gender_label = tk.Label(root, text="Gender:")
gender_label.pack()
gender_options = ["Any", "Male", "Female"]
gender_var = tk.StringVar(value="Any")
gender_dropdown = ttk.Combobox(root, textvariable=gender_var, values=gender_options, state="readonly")
gender_dropdown.pack()

# --- اختيار العمر ---
age_label = tk.Label(root, text="Age:")
age_label.pack()
age_var = tk.IntVar()
age_entry = tk.Spinbox(root, from_=0, to=100, textvariable=age_var)
age_entry.pack()

# --- اختيار نوع البشرة ---
skin_types_all = sorted(set([s.strip() for types in df['Skin Type'] for s in types.split(",")]))
skin_label = tk.Label(root, text="Skin Type:")
skin_label.pack()
skin_var = tk.StringVar()
skin_dropdown = ttk.Combobox(root, textvariable=skin_var, values=skin_types_all, state="readonly")
skin_dropdown.pack()

# --- اختيار مشاكل البشرة (قائمة متعددة اختيار) ---
problems_all = sorted(set([p.strip() for probs in df['Skin Problem'] for p in probs.split(",")]))
problem_label = tk.Label(root, text="Skin Problems (select multiple with Ctrl):")
problem_label.pack()
problem_listbox = tk.Listbox(root, selectmode="multiple", height=6)
for problem in problems_all:
    problem_listbox.insert(tk.END, problem)
problem_listbox.pack()

# --- اختيار الميزانية ---
budget_label = tk.Label(root, text="Budget (PHP):")
budget_label.pack()
budget_var = tk.IntVar()
budget_entry = tk.Spinbox(root, from_=0, to=10000, increment=100, textvariable=budget_var)
budget_entry.pack()

# --- زر البحث ---
def recommend_services():
    gender = gender_var.get().lower()
    age = age_var.get()
    skin_type = skin_var.get().lower()
    selected_indices = problem_listbox.curselection()
    user_problems = [problem_listbox.get(i).lower() for i in selected_indices]
    budget = budget_var.get()
    
    results = []

    for _, row in df.iterrows():
        score = 0
        
        # Gender check
        if row['Gender'].strip().lower() in [gender, "any"]:
            score += 1
        
        # Age check
        if row['Min Age'] <= age <= row['Max Age']:
            score += 1
        
        # Skin type check
        service_skin_types = [s.strip() for s in row['Skin Type'].lower().split(",")]
        if skin_type in service_skin_types:
            score += 1
        
        # Skin problems check
        service_problems = [s.strip().lower() for s in row['Skin Problem'].split(",")]
        if any(p in service_problems for p in user_problems):
            score += 1
        
        # Budget check
        if row['Price (PHP)'] <= budget:
            score += 1
        
        # إضافة Base Score من Excel
        base_score = row.get('Base Score', 0)
        try:
            score += float(base_score)
        except:
            pass
        
        if score > 0:
            results.append((row['Service Name'], score, row['Price (PHP)'], row['Notes']))

    if not results:
        messagebox.showinfo("No Match", "No services match your criteria.")
        return
    
    # ترتيب حسب أعلى نقاط
    results.sort(key=lambda x: x[1], reverse=True)

    # عرض النتائج
    result_text = "Best Matching Services:\n\n"
    for name, score, price, notes in results:
        result_text += f"{name} - Score: {score} - Price: {price} PHP\nNotes: {notes}\n\n"
    
    messagebox.showinfo("Results", result_text)

search_button = tk.Button(root, text="Find Best Service", command=recommend_services)
search_button.pack(pady=10)

root.mainloop()

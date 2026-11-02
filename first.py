import tkinter as tk
from tkinter import messagebox, filedialog
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import re

# ---------------- COLORS (MEDICAL THEME) ----------------
WHITE_BG = "#ffffff"
BLACK_TEXT = "#000000"
MEDICAL_RED = "#c00000"
LIGHT_GREY_ENTRY = "#f5f5f5"
DARK_GREY_BORDER = "#cccccc"
INVALID_BG = "#ffe6e6"  # Highlight for invalid inputs

# ---------------- CURRENT PAGE ----------------
current_page = "page1"
stored_bmi = stored_category = stored_advice = None
stored_health_result = stored_health_advice = None

# ---------------- UTILITY FUNCTIONS ----------------
def convert_weight(value, unit):
    value = float(value)
    if unit == "lb":
        return round(value * 0.453592, 2)
    return value  # kg

def convert_height(value, unit):
    if unit == "cm":
        return float(value)
    # ft/in format: e.g., 5.11 -> 5 ft 11 in
    match = re.match(r"^(\d+)\.(\d+)$", value)
    if not match:
        raise ValueError("Height in ft/in must be in format ft.in (e.g., 5.11)")
    ft, inch = map(int, match.groups())
    if inch >= 12:
        raise ValueError("Inches must be less than 12")
    return round(ft * 30.48 + inch * 2.54, 2)

def validate_number(input_value):
    if input_value == "":
        return True
    try:
        float(input_value)
        return True
    except ValueError:
        return False

def validate_realistic_values(weight, height_cm, age):
    """Validate realistic ranges for weight, height, and age."""
    errors = []
    if not (20 <= weight <= 300):
        errors.append("Weight is unrealistic (20-300 kg).")
        weight_entry.config(bg=INVALID_BG)
    else:
        weight_entry.config(bg=LIGHT_GREY_ENTRY)

    if not (50 <= height_cm <= 250):
        errors.append("Height is unrealistic (50-250 cm).")
        height_entry.config(bg=INVALID_BG)
    else:
        height_entry.config(bg=LIGHT_GREY_ENTRY)

    if not (1 <= age <= 120):
        errors.append("Age is unrealistic (1-120 years).")
        age_entry.config(bg=INVALID_BG)
    else:
        age_entry.config(bg=LIGHT_GREY_ENTRY)

    if errors:
        messagebox.showerror("Unrealistic Input", "\n".join(errors))
        return False
    return True

def reset_inputs():
    global stored_bmi, stored_category, stored_advice, stored_health_result, stored_health_advice
    for entry in [weight_entry, height_entry, age_entry, fullname_entry]:
        entry.delete(0, tk.END)
        entry.config(bg=LIGHT_GREY_ENTRY)
    # Reset dropdowns
    weight_unit.set("kg")
    height_unit.set("cm")
    stored_bmi = stored_category = stored_advice = stored_health_result = stored_health_advice = None
    for var in [q1_var,q2_var,q3_var,q4_var,q5_var,q6_var,q7_var,q8_var]:
        var.set("No")
    messagebox.showinfo("Reset", "All inputs have been cleared.")

def slide_to_page(current, next_page, direction="left"):
    width = 1000
    step = 25
    start_pos = 0
    end_pos = -width if direction=="left" else width
    next_start = width if direction=="left" else -width
    delta = -step if direction=="left" else step
    next_page.place(x=next_start, y=0)
    def animate():
        nonlocal start_pos, next_start
        if (direction=="left" and start_pos>end_pos) or (direction=="right" and start_pos<end_pos):
            start_pos+=delta
            next_start+=delta
            current.place(x=start_pos,y=0)
            next_page.place(x=next_start,y=0)
            root.after(5, animate)
        else:
            current.place_forget()
            next_page.place(x=0,y=0)
    animate()

def calculate_bmi_values():
    try:
        weight = convert_weight(weight_entry.get(), weight_unit.get())
        height_cm = convert_height(height_entry.get(), height_unit.get())
        if age_entry.get() == "":
            raise ValueError("Age is required")
        age = int(age_entry.get())

        if not validate_realistic_values(weight, height_cm, age):
            return None, None, None

        height_m = height_cm / 100
        bmi = weight / (height_m ** 2)
        if bmi < 18.5:
            return round(bmi, 2), "Underweight", "🥦 You may need to gain weight. Eat nutrient-rich foods."
        elif bmi < 24.9:
            return round(bmi, 2), "Normal", "💪 You have a healthy body weight. Maintain your balanced diet!"
        elif bmi < 29.9:
            return round(bmi, 2), "Overweight", "🚶‍♂️ Try to be more active. Include regular exercise."
        else:
            return round(bmi, 2), "Obese", "🩺 Consider consulting a healthcare provider for guidance."
    except ValueError as ve:
        messagebox.showerror("Invalid Input", str(ve))
        return None, None, None
    except Exception as e:
        messagebox.showerror("Error", f"Unexpected error: {e}")
        return None, None, None

def current_page_widget():
    return {"page1":page1,"page_questions":page_questions,"page_results":page_results}[current_page]

def go_to_results_page():
    global current_page
    bmi_result.set(stored_bmi)
    category_result.set(stored_category)
    advice_result.set(stored_advice)
    health_result.set(stored_health_result)
    health_advice.set(stored_health_advice)
    slide_to_page(current_page_widget(), page_results)
    current_page="page_results"

def go_to_questions_page():
    global current_page
    slide_to_page(current_page_widget(), page_questions)
    current_page="page_questions"

def done_button():
    global stored_bmi, stored_category, stored_advice
    bmi, category, advice = calculate_bmi_values()
    if bmi is None: return
    stored_bmi, stored_category, stored_advice = bmi, category, advice
    if messagebox.askyesno("Continue?", "Continue to health questions?"):
        go_to_questions_page()
    else:
        go_to_results_page()

def assess_health():
    global stored_health_result, stored_health_advice
    responses = [q1_var.get(),q2_var.get(),q3_var.get(),q4_var.get(),
                 q5_var.get(),q6_var.get(),q7_var.get(),q8_var.get()]
    score = responses.count("Yes")
    if score==8:
        stored_health_result="Excellent"; stored_health_advice="Outstanding habits! Keep maintaining them."
    elif score>=6:
        stored_health_result="Good"; stored_health_advice="You maintain good habits. Stay consistent."
    elif score>=4:
        stored_health_result="Fair"; stored_health_advice="Some areas need improvement."
    elif score>=2:
        stored_health_result="Poor"; stored_health_advice="Many habits need improvement."
    else:
        stored_health_result="Very Poor"; stored_health_advice="Major lifestyle improvements are needed."
    go_to_results_page()

def back_to_page1():
    global current_page; slide_to_page(current_page_widget(), page1,direction="right"); current_page="page1"

def back_to_questions():
    global current_page; slide_to_page(current_page_widget(), page_questions,direction="right"); current_page="page_questions"

def back_from_results():
    back_to_page1() if stored_health_result is None else back_to_questions()

def save_user_info():
    if stored_bmi is None or stored_health_result is None:
        messagebox.showerror("Incomplete Data", "Please complete BMI calculation and health assessment first.")
        return
    fullname = fullname_entry.get().strip()
    if not fullname:
        messagebox.showerror("Missing Name", "Please enter your full name before saving.")
        return
    # Automatically use Full Name as file name
    file_path = filedialog.asksaveasfilename(
        title="Save Health Report",
        defaultextension=".pdf",
        initialfile=f"{fullname}.pdf",
        filetypes=[("PDF Files","*.pdf")]
    )
    if not file_path:
        return
    try:
        c = canvas.Canvas(file_path, pagesize=letter)
        width, height = letter
        y = height - 50
        def write_line(text, font="Helvetica", size=12, leading=15):
            nonlocal y
            c.setFont(font, size)
            c.drawString(50, y, text)
            y -= leading

        write_line(f"=== {fullname.upper()} HEALTH REPORT ===", "Helvetica-Bold", 14, 20)
        write_line("="*50, "Helvetica", 12, 20)
        write_line(f"Full Name: {fullname}")
        write_line(f"Weight: {weight_entry.get()} {weight_unit.get()}")
        write_line(f"Height: {height_entry.get()} {height_unit.get()}")
        write_line(f"Age: {age_entry.get()}")
        write_line("")
        write_line("=== BMI RESULTS ===", "Helvetica-Bold", 12, 15)
        write_line(f"BMI: {stored_bmi}")
        write_line(f"Category: {stored_category}")
        write_line(f"Advice: {stored_advice}")
        write_line("")
        write_line("=== HEALTH ASSESSMENT ===", "Helvetica-Bold", 12, 15)
        write_line(f"Assessment: {stored_health_result}")
        write_line(f"Tips: {stored_health_advice}")
        write_line("")
        write_line("=== HEALTH QUESTIONS ===", "Helvetica-Bold", 12, 15)
        questions_list = [
            "Do you exercise regularly?",
            "Do you eat fruits and vegetables daily?",
            "Do you sleep at least 7 hours a night?",
            "Do you drink at least 8 glasses of water daily?",
            "Do you avoid sugary drinks regularly?",
            "Do you limit junk food and processed foods?",
            "Do you perform stretching or light activity?",
            "Do you manage stress well (hobbies, relaxing)?"
        ]
        vars_list = [q1_var,q2_var,q3_var,q4_var,q5_var,q6_var,q7_var,q8_var]
        for q, var in zip(questions_list, vars_list):
            write_line(f"- {q} {var.get()}")
        write_line("")
        write_line("=== END OF REPORT ===", "Helvetica-Bold", 12, 15)
        c.save()
        messagebox.showinfo("Saved", f"User information was successfully saved as {fullname}.pdf!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save PDF.\n{e}")

def style_entry(entry):
    entry.config(bg=LIGHT_GREY_ENTRY, fg=BLACK_TEXT, insertbackground=BLACK_TEXT,
                 highlightthickness=1, highlightbackground=DARK_GREY_BORDER, relief="flat",
                 font=("Segoe UI",12))

def create_styled_dropdown(parent, variable, options, width=4):
    frame = tk.Frame(parent, bg=LIGHT_GREY_ENTRY, bd=1, relief="solid")
    option_menu = tk.OptionMenu(frame, variable, *options)
    option_menu.config(
        bg=LIGHT_GREY_ENTRY,
        fg=BLACK_TEXT,
        activebackground=WHITE_BG,
        activeforeground=BLACK_TEXT,
        width=width,
        font=("Segoe UI", 10),
        highlightthickness=0,
        relief="flat",
        bd=0,
        anchor="w"
    )
    option_menu["menu"].config(bg=WHITE_BG, fg=BLACK_TEXT, font=("Segoe UI", 10))
    option_menu.pack(fill="both", expand=True, padx=1, pady=1)
    return frame

# ---------------- GUI ----------------
root = tk.Tk()
root.title("Smart Health & BMI Checker")
root.geometry("1000x550")
root.resizable(False, False)
root.config(bg=WHITE_BG)
validate_cmd = root.register(validate_number)

# ---------------- PAGE 1 ----------------
page1 = tk.Frame(root, bg=WHITE_BG, width=1000, height=550)
page1.place(x=0,y=0)
container1 = tk.Frame(page1,bg=WHITE_BG)
container1.place(relx=0.5,rely=0.5,anchor="center")

tk.Label(container1,text="Smart Health & BMI Checker",font=("Helvetica",28,"bold"),
         fg=MEDICAL_RED,bg=WHITE_BG).pack(pady=10)
tk.Label(container1,text="Enter your information",font=("Segoe UI",16),
         fg=BLACK_TEXT,bg=WHITE_BG).pack(pady=5)

tk.Label(container1, text="Full Name:", fg=BLACK_TEXT, bg=WHITE_BG, font=("Segoe UI",12)).pack(pady=(10,0))
fullname_entry = tk.Entry(container1, width=30)
style_entry(fullname_entry)
fullname_entry.pack(pady=5)

input_frame = tk.Frame(container1,bg=WHITE_BG)
input_frame.pack(pady=20)

# Weight
weight_frame = tk.Frame(input_frame,bg=WHITE_BG)
weight_frame.grid(row=0,column=0,padx=20)
tk.Label(weight_frame,text="Weight:",fg=BLACK_TEXT,bg=WHITE_BG,font=("Segoe UI",12)).pack()
weight_entry=tk.Entry(weight_frame,width=12,validate="key",validatecommand=(validate_cmd,"%P"))
style_entry(weight_entry)
weight_entry.pack(side="left", pady=5)
weight_unit = tk.StringVar(value="kg")
weight_dropdown = create_styled_dropdown(weight_frame, weight_unit, ["kg", "lb"])
weight_dropdown.pack(side="left", padx=3)

# Height
height_frame = tk.Frame(input_frame,bg=WHITE_BG)
height_frame.grid(row=0,column=1,padx=20)
tk.Label(height_frame,text="Height:",fg=BLACK_TEXT,bg=WHITE_BG,font=("Segoe UI",12)).pack()
height_entry=tk.Entry(height_frame,width=12,validate="key",validatecommand=(validate_cmd,"%P"))
style_entry(height_entry)
height_entry.pack(side="left", pady=5)
height_unit = tk.StringVar(value="cm")
height_dropdown = create_styled_dropdown(height_frame, height_unit, ["cm", "ft/in"])
height_dropdown.pack(side="left", padx=3)

# Age
age_frame = tk.Frame(input_frame,bg=WHITE_BG)
age_frame.grid(row=0,column=2,padx=20)
tk.Label(age_frame,text="Age:",fg=BLACK_TEXT,bg=WHITE_BG,font=("Segoe UI",12)).pack()
age_entry=tk.Entry(age_frame,width=12,validate="key",validatecommand=(validate_cmd,"%P"))
style_entry(age_entry)
age_entry.pack(pady=5)

# Buttons
btn_row = tk.Frame(container1,bg=WHITE_BG)
btn_row.pack(pady=20)
tk.Button(btn_row,text="Calculate",command=done_button,bg=MEDICAL_RED,fg="white",
          width=14,font=("Segoe UI",12,"bold")).grid(row=0,column=0,padx=10)
tk.Button(btn_row,text="Reset",command=reset_inputs,bg=MEDICAL_RED,fg="white",
          width=14,font=("Segoe UI",12,"bold")).grid(row=0,column=1,padx=10)

# ---------------- HEALTH QUESTIONS PAGE ----------------
page_questions = tk.Frame(root,bg=WHITE_BG,width=1000,height=550)
container2 = tk.Frame(page_questions,bg=WHITE_BG)
container2.place(relx=0.5,rely=0.5,anchor="center")
tk.Label(container2,text="Health Habit Check",font=("Helvetica",22,"bold"),
         fg=MEDICAL_RED,bg=WHITE_BG).pack(pady=15)

q1_var = tk.StringVar(value="No"); q2_var = tk.StringVar(value="No")
q3_var = tk.StringVar(value="No"); q4_var = tk.StringVar(value="No")
q5_var = tk.StringVar(value="No"); q6_var = tk.StringVar(value="No")
q7_var = tk.StringVar(value="No"); q8_var = tk.StringVar(value="No")

questions = [
    ("Do you exercise regularly?", q1_var),
    ("Do you eat fruits and vegetables daily?", q2_var),
    ("Do you sleep at least 7 hours a night?", q3_var),
    ("Do you drink at least 8 glasses of water daily?", q4_var),
    ("Do you avoid sugary drinks regularly?", q5_var),
    ("Do you limit junk food and processed foods?", q6_var),
    ("Do you perform stretching or light activity?", q7_var),
    ("Do you manage stress well (hobbies, relaxing)?", q8_var),
]

for qtext,var in questions:
    tk.Checkbutton(container2,text=qtext,variable=var,onvalue="Yes",offvalue="No",
                   fg=BLACK_TEXT,bg=WHITE_BG,font=("Segoe UI",12),selectcolor=WHITE_BG).pack(anchor="w",padx=20,pady=2)

tk.Button(container2,text="Finish Assessment",bg=MEDICAL_RED,fg="white",
          width=18,font=("Segoe UI",12,"bold"),command=assess_health).pack(pady=20)
tk.Button(container2,text="Back",bg=LIGHT_GREY_ENTRY,fg=BLACK_TEXT,
          width=12,font=("Segoe UI",12),command=back_to_page1).pack()

# ---------------- RESULTS PAGE ----------------
page_results = tk.Frame(root,bg=WHITE_BG,width=1000,height=550)
container3 = tk.Frame(page_results,bg=WHITE_BG)
container3.place(relx=0.5,rely=0.5,anchor="center")

bmi_result = tk.StringVar(); category_result = tk.StringVar()
advice_result = tk.StringVar(); health_result = tk.StringVar(); health_advice = tk.StringVar()

tk.Label(container3,text="BMI Results",font=("Helvetica",26,"bold"),
         fg=MEDICAL_RED,bg=WHITE_BG).pack(pady=10)
tk.Label(container3,text="Your BMI:",fg=BLACK_TEXT,bg=WHITE_BG,font=("Segoe UI",14)).pack()
tk.Label(container3,textvariable=bmi_result,font=("Helvetica",28,"bold"),
         fg=BLACK_TEXT,bg=WHITE_BG).pack()

tk.Label(container3,text="Category:",fg=BLACK_TEXT,bg=WHITE_BG,font=("Segoe UI",14)).pack(pady=(10,0))
tk.Label(container3,textvariable=category_result,font=("Helvetica",20),
         fg=BLACK_TEXT,bg=WHITE_BG).pack()

tk.Label(container3,text="\nBMI Advice:",fg=BLACK_TEXT,bg=WHITE_BG,font=("Segoe UI",12)).pack()
tk.Label(container3,textvariable=advice_result,wraplength=650,
         justify="center",fg=BLACK_TEXT,bg=WHITE_BG,font=("Segoe UI",12)).pack()

tk.Label(container3,text="\nHealth Assessment:",fg=BLACK_TEXT,bg=WHITE_BG,font=("Segoe UI",14)).pack()
tk.Label(container3,textvariable=health_result,font=("Helvetica",20),
         fg=BLACK_TEXT,bg=WHITE_BG).pack()

tk.Label(container3,text="\nHealth Tips:",fg=BLACK_TEXT,bg=WHITE_BG,font=("Segoe UI",12)).pack()
tk.Label(container3,textvariable=health_advice,wraplength=650,justify="center",
         fg=BLACK_TEXT,bg=WHITE_BG,font=("Segoe UI",12)).pack()

btn_results = tk.Frame(container3,bg=WHITE_BG)
btn_results.pack(pady=20)
tk.Button(btn_results,text="Back",bg=LIGHT_GREY_ENTRY,fg=BLACK_TEXT,width=12,
          font=("Segoe UI",12),command=back_from_results).grid(row=0,column=0,padx=10)
tk.Button(btn_results,text="Save as PDF",bg=MEDICAL_RED,fg="white",width=12,
          font=("Segoe UI",12,"bold"),command=save_user_info).grid(row=0,column=1,padx=10)

tk.Label(container3,text="\nDeveloped by BSIT-06 Group 4",font=("Segoe UI",10,"italic"),
         fg=BLACK_TEXT,bg=WHITE_BG).pack()

root.mainloop()

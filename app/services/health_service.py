import io
import re
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

class PDFService:
    @staticmethod
    def generate_report(data):
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        _, height = letter
        y = height - 50
        fullname = data.get("fullname", "User").strip() or "User"

        def write_line(text, font="Helvetica", size=12, leading=15):
            nonlocal y
            c.setFont(font, size)
            c.drawString(50, y, text)
            y -= leading

        write_line(f"=== {fullname.upper()} HEALTH REPORT ===", "Helvetica-Bold", 14, 20)
        write_line("=" * 50, "Helvetica", 12, 20)
        write_line(f"Full Name: {fullname}")
        write_line(f"Weight: {data.get('weight')} {data.get('weight_unit')}")
        write_line(f"Height: {data.get('height')} {data.get('height_unit')}")
        write_line(f"Age: {data.get('age')}")
        write_line("")
        write_line("=== BMI RESULTS ===", "Helvetica-Bold", 12, 15)
        write_line(f"BMI: {data.get('bmi')}")
        write_line(f"Category: {data.get('category')}")
        write_line(f"Advice: {data.get('advice')}")
        write_line("")

        if data.get("health_result"):
            write_line("=== HEALTH ASSESSMENT ===", "Helvetica-Bold", 12, 15)
            write_line(f"Assessment: {data.get('health_result')}")
            write_line(f"Tips: {data.get('health_advice')}")
            write_line("")
            write_line("=== HEALTH QUESTIONS ===", "Helvetica-Bold", 12, 15)

            questions = [
                "Do you exercise regularly?",
                "Do you eat fruits and vegetables daily?",
                "Do you sleep at least 7 hours a night?",
                "Do you drink at least 8 glasses of water daily?",
                "Do you avoid sugary drinks regularly?",
                "Do you limit junk food and processed foods?",
                "Do you perform stretching or light activity?",
                "Do you manage stress well (hobbies, relaxing)?"
            ]
            answers = data.get("answers", [])
            for q, ans in zip(questions, answers):
                val = "Yes" if ans else "No"
                write_line(f"- {q} {val}")
            write_line("")

        write_line("=== END OF REPORT ===", "Helvetica-Bold", 12, 15)
        c.save()
        buffer.seek(0)
        
        filename = f"{re.sub(r'[^a-zA-Z0-9_-]', '_', fullname)}.pdf"
        return buffer, filename
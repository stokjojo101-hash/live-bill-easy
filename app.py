from flask import Flask, render_template, request
from datetime import datetime
from cost_engine import calculate_cost
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase import pdfmetrics
from flask import send_file
import io
import os
from werkzeug.utils import secure_filename
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from flask import send_file
import io
import json
from PIL import Image
from openpyxl.drawing.image import Image as XLImage
import base64
from equipment import equipment_bill

app = Flask(__name__)
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/equipment")
def equipment_page():
    return render_template("form_equipment.html")


@app.route("/equipment_bill", methods=["POST"])
def equipment_bill_route():
    return equipment_bill()

@app.route("/form")
def form():
    return render_template("form.html")

@app.route("/generate", methods=["POST"])
def generate():

    from datetime import datetime

    header = request.form.get("header")
    address = request.form.get("address")
    note = request.form.get("note")

    # ✅ แปลงวันที่
    date_input = request.form.get("date")

    if date_input:
        dt = datetime.strptime(date_input, "%Y-%m-%d")
    else:
        dt = datetime.today()

    # ✅ แปลงเป็น พ.ศ.
    thai_year = dt.year + 543
    date = dt.strftime("%d/%m/") + str(thai_year)

    # items
    colors = request.form.getlist("color[]")
    widths = request.form.getlist("width[]")
    heights = request.form.getlist("height[]")
    qtys = request.form.getlist("qty[]")
    notes = request.form.getlist("note[]")

    items = []
    total_cost = 0
    total_fabric_qty = 0

    for i in range(len(colors)):

        color = colors[i]
        width = float(widths[i])
        height = float(heights[i])
        qty = int(qtys[i])
        total_fabric_qty += qty
        note = notes[i] if i < len(notes) else ""

                    # เรียกคำนวณต้นทุน
        cost, is_special, used_width = calculate_cost(color, width, height)

        cost_total = cost * qty
        total_cost += cost_total

                    # สร้างข้อความขนาด
        size_text = f"{width:.1f} x {height:.1f}"

        if is_special:
            size_text += " (แปรรูป)"

        items.append({
            "color": color,
            "size": size_text,
            "qty": qty,
            "cost": cost_total,
            "note": note
        })

# ======================
# ของแถม
# ======================
    gifts = []
    gift_total_cost = 0
    total_gift_qty = 0

    for i in range(1, 4):
        name = request.form.get(f"gift_name_{i}")
        qty = request.form.get(f"gift_qty_{i}")
        price = request.form.get(f"gift_price_{i}")

        if name and qty and price:
            qty = int(qty)
            price = float(price)
            total_gift_qty += qty

            gifts.append({
                "name": name,
                "qty": qty
            })

            gift_total_cost += qty * price


    # 🔥 รวมต้นทุนของแถมเข้ากับต้นทุนหลักตรงนี้เลย
    total_cost += gift_total_cost


    # ======================
            # การชำระเงิน
    # ======================
    pay_types = request.form.getlist("pay_type[]")
    pay_amounts = request.form.getlist("pay_amount[]")

    payments = []
    for i in range(len(pay_types)):
        amount = float(pay_amounts[i]) if pay_amounts[i] else 0
        payments.append({
            "type": pay_types[i],
            "amount": amount
        })

    slip_filename = None
    file = request.files.get("slip_image")

    if file and file.filename != "":
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)
        slip_filename = filename

    # ======================
    # render
    # ======================
    extra_message = request.form.get("extra_message")
    return render_template(
        "bill.html",
        header=header,
        date=date,
        address=address,
        items=items,
        gifts=gifts,
        payments=payments,
        total_cost=total_cost,
        total_fabric_qty=total_fabric_qty,
        total_gift_qty=total_gift_qty,
        fabric_total_cost=total_cost - gift_total_cost,
        gift_total_cost=gift_total_cost,
        note=note,
        extra_message=extra_message,
        slip_filename=slip_filename,
        bill_type="curtain",
    )

@app.route("/export_excel_image", methods=["POST"])
def export_excel_image():

    data = request.get_json()
    image_data = data["image"]

    # ตัด header base64
    image_data = image_data.split(",")[1]

    image_bytes = base64.b64decode(image_data)

    # บันทึกชั่วคราว
    img = Image.open(io.BytesIO(image_bytes))
    img_path = "temp_bill.png"
    img.save(img_path)

    wb = Workbook()
    ws = wb.active
    ws.title = "Bill"

    ws.page_setup.orientation = ws.ORIENTATION_LANDSCAPE

    img_excel = XLImage(img_path)
    img_excel.anchor = "A1"
    ws.add_image(img_excel)

    file_stream = io.BytesIO()
    wb.save(file_stream)
    file_stream.seek(0)

    return send_file(
        file_stream,
        as_attachment=True,
        download_name="bill.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@app.route("/export_pdf")
def export_pdf():

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)

    elements = []

    pdfmetrics.registerFont(UnicodeCIDFont('HYSMyeongJo-Medium'))
    styles = getSampleStyleSheet()
    style = styles["Normal"]
    style.fontName = 'HYSMyeongJo-Medium'

    elements.append(Paragraph("ใบสรุปบิล", style))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("ระบบคำนวณราคาผ้าม่าน", style))

    doc.build(elements)

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="bill.pdf",
        mimetype="application/pdf"
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

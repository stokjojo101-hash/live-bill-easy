from flask import request, render_template
from datetime import datetime
from werkzeug.utils import secure_filename
import os

def equipment_bill():

    header = request.form.get("header")
    address = request.form.get("address")

    items = []
    total_cost = 0

    cost_table = {
        "rod":50,
        "rod_head":12,
        "bracket1":20,
        "bracket2":60,
        "joint":20,
        "tie":30
    }

    name_map = {
        "rod":"ราวม่าน",
        "rod_head":"หัวราว",
        "bracket1":"ขา 1 ชั้น",
        "bracket2":"ขา 2 ชั้น",
        "joint":"ข้อต่อ",
        "tie":"สายรวบพู่"
    }

    item_keys = ["rod_head","bracket1","bracket2","joint","tie"]

    # ⭐ ราวม่าน (รองรับหลายรายการ)

    rod_meters = request.form.getlist("rod_meter[]")
    rod_qtys = request.form.getlist("rod_qty[]")
    rod_colors = request.form.getlist("rod_color[]")

    for meter, qty, color in zip(rod_meters, rod_qtys, rod_colors):

        meter = float(meter or 0)
        qty = int(qty or 0)

        if meter == 0 or qty == 0:
            continue

        cost = meter * qty * cost_table["rod"]

        items.append({
            "color": color,
            "size": f"ราวม่าน {meter} เมตร",
            "qty": qty,
            "note": "",
            "cost": cost
        })

        total_cost += cost

    for key in item_keys:

        color = request.form.get(f"{key}_color")
        qty = int(request.form.get(f"{key}_qty") or 0)

        if qty == 0:
            continue

        cost = qty * cost_table[key]
        size_text = name_map[key]

        items.append({
            "color": color,
            "size": size_text,
            "qty": qty,
            "note": "",
            "cost": cost
        })

        total_cost += cost


    payment_types = request.form.getlist("payment_type[]")
    payment_amounts = request.form.getlist("payment_amount[]")

    payments = []

    for ptype, amount in zip(payment_types, payment_amounts):
        if amount:
            payments.append({
                "type": ptype,
                "amount": float(amount)
            })


    slip = request.files.get("slip")
    slip_filename = None

    if slip and slip.filename != "":
        filename = secure_filename(slip.filename)
        slip_path = os.path.join("static/uploads", filename)
        slip.save(slip_path)
        slip_filename = filename

    return render_template(
        "bill.html",
        header=header,
        date=datetime.now().strftime("%d/%m/%Y"),
        address=address,
        items=items,
        gifts=[],
        payments=payments,
        total_cost=total_cost,
        total_fabric_qty=len(items),
        total_gift_qty=0,
        fabric_total_cost=total_cost,
        gift_total_cost=0,
        slip_filename=slip_filename,
        bill_type="equipment",
    )
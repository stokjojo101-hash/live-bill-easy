import math
from cost_loader import load_cost_tables

COST_TABLE = load_cost_tables()

# ----------------------------
# MAP สี
# ----------------------------

PLAIN_COLORS = [
    "A4","A6","A7","A8","A9","A10","A18",
    "828","828-1","828-3","828-6"
]

PATTERN_COLORS = [
    "702","704","705","716","717","719","722","723","741","742","744","858",
    "860","861","862","863","865","876","877",
    "2021-4","2021-5","2021-6","2021-9"
]

SHEER_COLORS = ["733","734"]  # เพิ่มได้ตามจริง


def get_model_sheet(color):
    if color in PLAIN_COLORS:
        return "ผ้าพื้น"
    if color in PATTERN_COLORS:
        return "ผ้าลาย"
    if color in SHEER_COLORS:
        return "ผ้าโปร่ง"
    return None


def get_lower_sheet(color):
    if color in PLAIN_COLORS:
        return "ผ้าพื้นต่อล่าง"
    if color in PATTERN_COLORS or color in SHEER_COLORS:
        return "ผ้าลายต่อล่าง"
    return None


# =====================================================
# ================= MAIN ENGINE =======================
# =====================================================

def calculate_cost(color, width, height):

    model_sheet = get_model_sheet(color)
    if not model_sheet:
        return 0, False, width

    table = COST_TABLE.get(model_sheet)
    if not table:
        return 0, False, width

    available_widths = sorted(table.keys())
    max_width = available_widths[-1]


    # =================================================
    # 2️⃣ width ต่ำกว่า 1.3 → ใช้ 1.3
    # =================================================
    if width < 1.3:
        width = 1.3

    # =================================================
    # 3️⃣ กรณี width เกินสูงสุด
    # =================================================
    if width > max_width:

        # หา base price จากช่วง height ที่ถูกต้องของ max_width
        base_price = None
        max_h = 0

        for row in table[max_width]:
            if row["min_h"] <= height <= row["max_h"]:
                base_price = row["price"]

            if row["max_h"] > max_h:
                max_h = row["max_h"]

        # 🔥 เกินทั้งคู่ → ไปผ้าต่อ
        if height > max_h:

            lower_sheet = get_lower_sheet(color)
            lower_table = COST_TABLE.get(lower_sheet)

            if lower_table:
                for row in lower_table:
                    if (row["width_min"] <= width <= row["width_max"] and
                        row["min_h"] <= height <= row["max_h"]):
                        return row["price"], False, width

            return 0, False, width

        # 🔥 เกินแค่ width → บวกเพิ่ม
        if base_price is not None:
            extra_cm = round((width - max_width) * 100)
            return base_price + extra_cm, False, max_width

        return 0, False, width

    # =================================================
    # 4️⃣ width ปกติ
    # =================================================

    # หา width ที่ต้องใช้ (ปัดขึ้น)
    price_width = None
    for w in available_widths:
        if width <= w:
            price_width = w
            break

    base_price = None
    max_h = 0

    # 🔥 ตรวจเกินทั้งคู่แบบถูกต้อง
    max_width = available_widths[-1]
    max_h_of_current = max(r["max_h"] for r in table[price_width])

    if height > max_h_of_current and price_width == max_width:

        lower_sheet = get_lower_sheet(color)
        lower_table = COST_TABLE.get(lower_sheet)

        if lower_table:
            for row in lower_table:
                if (row["width_min"] <= width <= row["width_max"] and
                    row["min_h"] <= height <= row["max_h"]):
                    return row["price"], False, width

        return 0, False, width

    for row in table[price_width]:

        if row["min_h"] <= height <= row["max_h"]:
            return row["price"], False, price_width

        if row["max_h"] > max_h:
            max_h = row["max_h"]
            base_price = row["price"]

    # 🔥 เกิน height อย่างเดียว → บวกเพิ่ม
    if height > max_h and base_price is not None:
        extra_cm = round((height - max_h) * 100)
        return base_price + extra_cm, False, price_width

    return 0, False, price_width
import pandas as pd

def load_cost_tables(filepath="cost_tables.xlsx"):

    xls = pd.ExcelFile(filepath)
    cost_tables = {}

    for sheet in xls.sheet_names:

        df = pd.read_excel(xls, sheet)
        df.columns = df.columns.str.strip()
        # ============================
        # 🔥 ตารางแปรรูป
        # ============================
        if sheet == "แปรรูป":

            special_table = {}

            for _, row in df.iterrows():
                width = float(row["width"])
                height = float(row["height"])
                price = float(row["price"])

                special_table[(width, height)] = price

            cost_tables[sheet] = special_table
            continue

        # ============================
        # 🔥 ตารางต่อล่าง (มี width_min)
        # ============================
        if "width_min" in df.columns:

            special_rows = []

            for _, row in df.iterrows():
                special_rows.append({
                    "width_min": float(row["width_min"]),
                    "width_max": float(row["width_max"]),
                    "min_h": float(row["min_h"]),
                    "max_h": float(row["max_h"]),
                    "price": float(row["price"])
                })

            cost_tables[sheet] = special_rows

        # 🔥 sheet ปกติ
        else:

            model_table = {}

            for _, row in df.iterrows():
                width = float(row["width"])

                if width not in model_table:
                    model_table[width] = []

                model_table[width].append({
                    "min_h": float(row["min_h"]),
                    "max_h": float(row["max_h"]),
                    "price": float(row["price"])
                })

            cost_tables[sheet] = model_table

    return cost_tables
import pdfplumber
import re
import pandas as pd

def extract_data(pdf_path):
    advice_no = ""
    date = ""
    payment_made = ""
    rows = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:

            text = page.extract_text() or ""
            lines = [l.strip() for l in text.split("\n")]

            # 🔹 header
            adv_match = re.search(r"Advice\s*No[:\s]+(\S+)", text, re.I)
            if adv_match:
                advice_no = adv_match.group(1)

            date_match = re.search(r"Date[:\s]+([\d./-]+)", text, re.I)
            if date_match:
                date = date_match.group(1)

            pay_match = re.search(r"Payment\s+Made\s+([\d,.\-]+)", text, re.I)
            if pay_match:
                payment_made = pay_match.group(1).replace(",", "")

            # 🔹 find table region
            start, end = None, None
            for i, line in enumerate(lines):
                if line.startswith("Ref. No"):
                    start = i + 2
                if "Payment Made" in line:
                    end = i
                    break

            if start is None or end is None:
                continue

            table_lines = []

            # remove junk
            for line in lines[start:end]:
                if not line or set(line) == {"-"}:
                    continue
                table_lines.append(line)

            # 🔥 process 3-line blocks
            i = 0
            while i < len(table_lines):

                try:
                    line1 = table_lines[i]
                    line2 = table_lines[i+1] if i+1 < len(table_lines) else ""
                    line3 = table_lines[i+2] if i+2 < len(table_lines) else ""

                    # split main row safely
                    parts = re.findall(r'\S+', line1)

                    if len(parts) < 6:
                        i += 1
                        continue

                    ref_no = parts[0]
                    tcode = parts[1]
                    inv_date = parts[2]
                    inv_no = parts[3]
                    amount_text = parts[4]
                    amount = parts[5].replace(",", "")

                    # clean TDS
                    tds = re.sub(r"[^\d.]", "", line2)

                    remarks = line3

                    rows.append({
                        "Advice No": advice_no,
                        "Date": date,
                        "Ref No": ref_no,
                        "TCode": tcode,
                        "Inv Date": inv_date,
                        "Inv No": inv_no,
                        "Amount/Text": amount_text,
                        "Amount": amount,
                        "TDS": tds,
                        "Remarks": remarks
                    })

                    i += 3

                except:
                    i += 1

    # 🔹 add payment row
    if payment_made:
        rows.append({
            "Advice No": advice_no,
            "Date": date,
            "Ref No": "",
            "TCode": "",
            "Inv Date": "",
            "Inv No": "Payment Made",
            "Amount/Text": "",
            "Amount": payment_made,
            "TDS": "",
            "Remarks": ""
        })

    df = pd.DataFrame(rows)

    df = df[
        [
            "Advice No",
            "Date",
            "Ref No",
            "TCode",
            "Inv Date",
            "Inv No",
            "Amount/Text",
            "Amount",
            "TDS",
            "Remarks"
        ]
    ]

    return df
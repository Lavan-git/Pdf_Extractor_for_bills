import pdfplumber
import re
import pandas as pd


def is_dash_line(line: str) -> bool:
    cleaned = line.replace(" ", "")
    return bool(cleaned) and all(c == "-" for c in cleaned)


def extract_data(pdf_path):
    advice_no = ""
    date = ""
    payment_made = ""
    rows = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:

            text = page.extract_text() or ""
            lines = [l.strip() for l in text.split("\n") if l.strip()]

            # 🔹 Header extraction
            adv_match = re.search(r"Advice\s*No[:\s]+(\S+)", text, re.I)
            if adv_match:
                advice_no = adv_match.group(1)

            date_match = re.search(r"Date[:\s]+([\d./-]+)", text, re.I)
            if date_match:
                date = date_match.group(1)

            pay_match = re.search(r"Payment\s+Made\s+([\d,.\-]+)", text, re.I)
            if pay_match:
                payment_made = pay_match.group(1).replace(",", "")

            # 🔹 Find table region
            start, end = None, None
            for i, line in enumerate(lines):
                if line.startswith("Ref. No"):
                    start = i + 2
                if "Payment Made" in line:
                    end = i
                    break

            if start is None or end is None:
                continue

            # 🔹 Clean table lines
            table_lines = []
            for line in lines[start:end]:
                if is_dash_line(line):
                    continue
                table_lines.append(line)

            # 🔥 Dynamic row parsing (FINAL FIX)
            i = 0
            while i < len(table_lines):

                line = table_lines[i]
                parts = re.findall(r'\S+', line)

                # detect new row
                if len(parts) >= 6 and re.match(r"^\d{6,}", parts[0]):

                    ref_no = parts[0]
                    tcode = parts[1]
                    inv_date = parts[2]
                    inv_no = parts[3]
                    amount_text = parts[4]
                    amount = parts[5].replace(",", "")

                    tds = ""
                    remarks = ""

                    j = i + 1

                    # 🔥 consume lines until next row
                    while j < len(table_lines):

                        next_line = table_lines[j]

                        # stop if next row starts
                        if re.match(r"^\d{6,}", next_line):
                            break

                        if is_dash_line(next_line):
                            j += 1
                            continue

                        tokens = next_line.split()

                        for t in tokens:
                            if re.fullmatch(r"[-\d,\.]+", t) and not tds:
                                tds = re.sub(r"[^\d.]", "", t)
                            else:
                                if remarks:
                                    remarks += " " + t
                                else:
                                    remarks = t

                        j += 1

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
                        "Remarks": remarks.strip()
                    })

                    i = j  # jump to next row

                else:
                    i += 1

    # 🔹 Add Payment Made row
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

    return df[
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
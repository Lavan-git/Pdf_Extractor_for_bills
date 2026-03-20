from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import shutil
import uuid
import os
from app.parser import extract_data

app = FastAPI()

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.post("/upload/")
async def upload_pdf(file: UploadFile = File(...)):

    file_id = str(uuid.uuid4())

    pdf_path = f"{UPLOAD_DIR}/{file_id}.pdf"
    excel_path = f"{OUTPUT_DIR}/{file_id}.xlsx"

    # save pdf
    with open(pdf_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # process
    df = extract_data(pdf_path)
    df.to_excel(excel_path, index=False)

    return FileResponse(excel_path, filename="output.xlsx")
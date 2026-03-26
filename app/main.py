# from fastapi import FastAPI, UploadFile, File
# from fastapi.responses import FileResponse
# import shutil
# import uuid
# import os
# from app.parser import extract_data

# app = FastAPI()

# UPLOAD_DIR = "uploads"
# OUTPUT_DIR = "outputs"

# os.makedirs(UPLOAD_DIR, exist_ok=True)
# os.makedirs(OUTPUT_DIR, exist_ok=True)

# @app.post("/upload/")
# async def upload_pdf(file: UploadFile = File(...)):

#     file_id = str(uuid.uuid4())

#     pdf_path = f"{UPLOAD_DIR}/{file_id}.pdf"
#     excel_path = f"{OUTPUT_DIR}/{file_id}.xlsx"

#     # save pdf
#     with open(pdf_path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)

#     # process
#     df = extract_data(pdf_path)
#     df.to_excel(excel_path, index=False)

#     return FileResponse(excel_path, filename="output.xlsx")






from typing import List
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import pandas as pd
import uuid
import shutil
import os

from app.parser import extract_data

app = FastAPI()

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post(
    "/upload/",
    response_class=FileResponse,   # 🔥 IMPORTANT
)
async def upload_pdfs(files: List[UploadFile] = File(...)):

    print("RUNNING CORRECT ENDPOINT")

    all_dfs = []
    file_id = str(uuid.uuid4())
    excel_path = os.path.join(OUTPUT_DIR, f"{file_id}.xlsx")

    for file in files:
        pdf_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}.pdf")

        with open(pdf_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        df = extract_data(pdf_path)

        if df is not None and not df.empty:
            all_dfs.append(df)

    if not all_dfs:
        return {"error": "No valid data"}

    final_df = pd.concat(all_dfs, ignore_index=True)
    final_df.to_excel(excel_path, index=False)

    return excel_path  # 🔥 return path, NOT FileResponse manually
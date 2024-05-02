from fastapi import FastAPI, UploadFile, Request, Form, File
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import status
from function import save_upload_file, get_dataframes, merge_and_validate, send_alerts
from pydantic import BaseModel

app = FastAPI()

class RequestModel(BaseModel):
    upload_file: UploadFile
    calendar_ids: list[int]

@app.get("/hello")
async def read_root():
    return {"Hello": "World"}

@app.exception_handler(RequestValidationError)
async def handler(request:Request, exc:RequestValidationError):
    print(exc)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()}
    )

@app.post("/receipt_check")
async def receipt_check(
        upload_file: UploadFile = File(...),
        calendar_ids: str = Form(...)
    ):
    file_path = await save_upload_file(upload_file)
    calendar_df, ibow_df = get_dataframes(file_path,calendar_ids)
    results_df = merge_and_validate(calendar_df, ibow_df)

    return results_df.to_json(orient="records", force_ascii=False)
    # Chatworkにアラートを送信
    # send_alerts(results_df)

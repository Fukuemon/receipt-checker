from fastapi import FastAPI, UploadFile, Request, File
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import status
from function import receipt_check
from pydantic import BaseModel

app = FastAPI()

class RequestModel(BaseModel):
    receipt_file: UploadFile
    calendar_id_file: UploadFile

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
        receipt_file: UploadFile = File(...),
        calendar_id_file: UploadFile = File(...)
    ):

    results_df = receipt_check(receipt_file, calendar_id_file)

    return results_df.to_json(orient="records", force_ascii=False)
    # Chatworkにアラートを送信
    # send_alerts(results_df)
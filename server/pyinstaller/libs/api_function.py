from fastapi import UploadFile
from server.archive import calendar_ids_from_csv, get_dataframes, merge_and_validate
import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile

def receipt_check(receipt_file, calendar_file):
    receipt_file_path = save_upload_file_tmp(receipt_file)
    calendar_file_path = save_upload_file_tmp(calendar_file)
    calendar_ids = calendar_ids_from_csv(calendar_file_path)
    calendar_df, ibow_df = get_dataframes(receipt_file_path, calendar_ids)
    results_df = merge_and_validate(calendar_df, ibow_df)
    results_df = results_df[
        ["訪問日", "利用者名", "主訪問者", "サービス内容", "開始時間_カレンダー", "開始時間_Ibow", "終了時間_カレンダー", "終了時間_Ibow",
         "提供時間_カレンダー", "提供時間_Ibow"]]
    return results_df


# ファイルを保存
def save_upload_file_tmp(upload_file: UploadFile):
    tmp_path:Path = ""
    try:
        suffix = Path(upload_file.filename).suffix
        with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(upload_file.file, tmp)
            tmp_path = Path(tmp.name)
    finally:
        upload_file.file.close()
    return tmp_path



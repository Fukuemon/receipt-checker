
import requests
import pandas as pd
import io
from pathlib import Path
from tkinter import messagebox
from .constant import CALENDER_GAS_API_URL, USE_IBOW_COLUMNS

def create_google_calendar_to_csv(calendar_gas_api_url: str = CALENDER_GAS_API_URL) -> pd.DataFrame:
    """
    GoogleカレンダーのCSVデータを取得し、データフレームを作成する
    :param calendar_gas_api_url: GoogleカレンダーのAPIのURL（デフォルトはCALENDER_GAS_API_URL）
    :return: calendar_df: Googleカレンダーのデータフレーム
    """
    try:
        response = requests.get(calendar_gas_api_url)
        if response.status_code == 200:
            calendar_df = pd.read_csv(io.BytesIO(response.content), sep=",")
            return calendar_df
        elif response.status_code == 500:
            messagebox.showerror("エラー", "データの取得に失敗しました: 開発者にお問い合わせください。")
            raise ValueError("データの取得に失敗しました: 開発者にお問い合わせください。")
    except Exception:
        messagebox.showerror("エラー", "データの取得に失敗しました: 開発者にお問い合わせください。")
        raise ValueError("データの取得に失敗しました: 開発者にお問い合わせください。")

def get_dataframes(file_path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    ファイルパスからカレンダーのDataFrameとIbowのDataFrameを作成する
    :param file_path:
    :return: calendar_df, ibow_df
    """
    calendar_df = create_google_calendar_to_csv()
    try:
        ibow_df = pd.read_csv(file_path, encoding='utf-8', usecols=USE_IBOW_COLUMNS)
    except UnicodeDecodeError:
        raise ValueError("Ibowのファイルの文字コードが誤っています。UTF-8形式のファイルを選択してください。")
    except Exception:
        raise ValueError("Ibowのファイルが誤っています。正しいファイルが選択されているか確認してください。")

    ibow_df['加算'] = ibow_df[["加算①", "加算②", "加算③", "加算④", "加算⑤"]].apply(
        lambda x: ', '.join(x.dropna().astype(str)), axis=1
    )

    return calendar_df, ibow_df[["訪問日", "利用者名", "開始時間", "終了時間", "提供時間", "サービス内容", "主訪問者", "加算"]]
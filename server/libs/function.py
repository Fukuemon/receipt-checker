import requests
import pandas as pd
from server.libs.const_data import key_columns, check_columns, api_url
import csv
import io
from pathlib import Path


def receipt_check(receipt_file, calendar_file):
    calendar_ids = calendar_ids_from_csv(calendar_file)
    calendar_df, ibow_df = get_dataframes(receipt_file, calendar_ids)
    results_df = merge_and_validate(calendar_df, ibow_df)
    results_df = results_df[
        ["訪問日", "利用者名", "主訪問者", "サービス内容", "開始時間_カレンダー", "開始時間_Ibow", "終了時間_カレンダー", "終了時間_Ibow",
         "提供時間_カレンダー", "提供時間_Ibow"]]
    return results_df


# カレンダーIDのCSVファイルを元にをリストに変換
def calendar_ids_from_csv(csv_file):
    # 空の辞書を作成
    data_dict = {}

    # CSVファイルを読み込んで辞書に変換する
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)  # タブ区切りの場合
        next(reader)  # ヘッダーをスキップ
        for row in reader:
            name = row[0]  # 担当者名
            calendar_id = row[1]  # カレンダーID
            data_dict[name] = calendar_id

    # 辞書から間まで連結した文字列に変換
    result = ",".join(data_dict.values())
    return result


# GoogleカレンダーのCSVデータを取得
def create_google_calendar_to_csv(url):
    response = requests.get(url)
    if response.status_code == 200:
        calendar_df = pd.read_csv(io.BytesIO(response.content), sep=",")
        print(calendar_df)
        return calendar_df
    else:
        print("エラーが発生しました。ステータスコード:", response.status_code)


# 開始時間と終了時間のフォーマットを統一
def start_end_dateformat(df_1, df_2):
    columns = ['開始時間', '終了時間']
    for column in columns:
        # 開始時間と終了時間のフォーマットを統一
        df_1[column] = pd.to_datetime(df_1[column], format='%H:%M').dt.strftime('%H:%M')
        df_2[column] = pd.to_datetime(df_2[column], format='%H:%M').dt.strftime('%H:%M')


# データフレームを取得
def get_dataframes(file_path: Path, calendar_ids: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    URL = api_url
    URL += "?calendarIds=" + calendar_ids
    calendar_df = create_google_calendar_to_csv(URL)
    ibow_df = pd.read_csv(file_path, usecols=[0, 1, 11, 12, 13, 17, 25])
    start_end_dateformat(calendar_df, ibow_df)
    return calendar_df, ibow_df


def merge_and_validate(calendar_df: pd.DataFrame, ibow_df: pd.DataFrame) -> pd.DataFrame:
    # 訪問日を日付型に変換
    calendar_df = calendar_df.sort_values(by=['訪問日', '開始時間'])

    # 日付を調整
    calendar_df['訪問日'] = pd.to_datetime(calendar_df['訪問日']).dt.tz_localize('Asia/Tokyo', ambiguous='infer').dt.tz_localize(None)
    ibow_df['訪問日'] = pd.to_datetime(ibow_df['訪問日']).dt.tz_localize('Asia/Tokyo', ambiguous='infer').dt.tz_localize(None)

    # データフレームをマージ
    merged_df = pd.merge(calendar_df, ibow_df, on=key_columns, suffixes=('_カレンダー', '_Ibow'))
    for column in check_columns:
        merged_df[column + '_match'] = merged_df[column + '_カレンダー'] == merged_df[column + '_Ibow']

    filtered_df = merged_df[(merged_df['開始時間_match'] == False) | (merged_df['終了時間_match'] == False) & (merged_df['提供時間_match'] == False)]
    return filtered_df


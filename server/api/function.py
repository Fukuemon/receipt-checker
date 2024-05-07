import requests
from fastapi import UploadFile
import pandas as pd
from const_data import managers, key_columns, check_columns, api_url, chatwork_base_url
import os
import csv


def receipt_check(file_path, calendar_file):
    calendar_ids = get_calendar_ids(calendar_file)
    calendar_df, ibow_df = get_dataframes(file_path, calendar_ids)
    results_df = merge_and_validate(calendar_df, ibow_df)
    results_df = results_df[["訪問日", "利用者名", "主訪問者", "サービス内容", "開始時間_カレンダー", "終了時間_カレンダー", "提供時間_カレンダー", "開始時間_Ibow", "終了時間_Ibow", "提供時間_Ibow"]]
    return results_df

# カレンダーIDを取得
def get_calendar_ids(calendar_ids_csv_path):
    if calendar_ids_csv_path is None:
        calendar_ids_csv_path = "./calendar_ids.csv"
    return calendar_id_to_list(calendar_ids_csv_path)

# カレンダーIDのCSVファイルを元にをリストに変換
def calendar_id_to_list(csv_file):
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
    result = result = ",".join(data_dict.values())
    return result

# ファイルを保存
async def save_upload_file(upload_file: UploadFile):
    file_location = f"temp/{upload_file.filename}"
    # ディレクトリが存在するか確認し、存在しない場合は作成する
    os.makedirs(os.path.dirname(file_location), exist_ok=True)
    with open(file_location, "wb+") as file_object:
        # UploadedFileを読み込み、一時ファイルに書き込む
        file_object.write(await upload_file.read())
    return file_location

# GoogleカレンダーのCSVデータを取得
def create_google_calendar_to_csv(url , csv_file):
    response = requests.get(url)
    if response.status_code == 200:
        with open(csv_file, 'w') as file:
            file.write(response.text)
        return csv_file
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
def get_dataframes(file_path: str, calendar_ids: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    google_calendar_csv = create_google_calendar_to_csv(api_url, "./google_calendar_events.csv")
    calendar_df = pd.read_csv(google_calendar_csv)
    ibow_df = pd.read_csv(file_path, usecols=[0, 1, 11, 12, 13, 17, 25])
    start_end_dateformat(calendar_df, ibow_df)
    return calendar_df, ibow_df

# データフレームをマージし、一致しないデータを抽出

def merge_and_validate(calendar_df: pd.DataFrame, ibow_df: pd.DataFrame) -> pd.DataFrame:
    calendar_df['訪問日'] = pd.to_datetime(calendar_df['訪問日']).dt.tz_localize('Asia/Tokyo', ambiguous='infer').dt.tz_localize(None)
    calendar_df = calendar_df.sort_values(by=['訪問日', '開始時間'])
    ibow_df['訪問日'] = pd.to_datetime(ibow_df['訪問日']).dt.tz_localize('Asia/Tokyo', ambiguous='infer').dt.tz_localize(None)
    merged_df = pd.merge(calendar_df, ibow_df, on=key_columns, suffixes=('_カレンダー', '_Ibow'))
    for column in check_columns:
        merged_df[column + '_match'] = merged_df[column + '_カレンダー'] == merged_df[column + '_Ibow']
    return merged_df[merged_df[['開始時間_match', '終了時間_match', '提供時間_match']].any(axis=1) == False]

## メッセージを送信
def send_message(room_id, message):
    payload = {
        "self_unread": 0,
        "body": message
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/x-www-form-urlencoded",
        "x-chatworktoken": "415e3d094069523a8b9fb1828f36c8a4"
    }
    response = requests.post(f"{chatwork_base_url}/rooms/{room_id}/messages", data=payload, headers=headers)
    if response.status_code == 200:
        print("メッセージを送信しました。")
    else:
        print("エラーが発生しました。ステータスコード:", response.status_code)
        print(response.text)


def send_alerts(filtered_df: pd.DataFrame):
    for index, row in filtered_df.iterrows():
        room_id = managers.get(row['主訪問者'])
        if room_id:
            message = (
                f"以下のカレンダーとレセプトの内容が一致しませんでした.\n"
                f"訪問日: {row['訪問日']}\n"
                f"利用者名: {row['利用者名']}\n"
                f"サービス内容: {row['サービス内容']}\n"
                f"時間情報:\n"
                f"  - カレンダー時間:\n"
                f"    - 開始時間: {row['開始時間_カレンダー']}\n"
                f"    - 終了時間: {row['終了時間_カレンダー']}\n"
                f"    - 提供時間: {row['提供時間_カレンダー']}分\n"
                f"  - Ibow時間:\n"
                f"    - 開始時間: {row['開始時間_Ibow']}\n"
                f"    - 終了時間: {row['終了時間_Ibow']}\n"
                f"    - 提供時間: {row['提供時間_Ibow']}分"
            )
            send_message(room_id, message)
# ファイルを保存
async def save_upload_file(upload_file: UploadFile):
    file_location = f"temp/{upload_file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(await upload_file.read())
    return file_location

# GoogleカレンダーのCSVデータを取得
def create_google_calendar_to_csv(url , csv_file):
    response = requests.get(url)
    if response.status_code == 200:
        with open(csv_file, 'w') as file:
            file.write(response.text)
        return csv_file
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
def get_dataframes(file_path: str, calendar_ids: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    URL = api_url
    URL += "?calendarIds=" + calendar_ids
    print(URL)
    google_calendar_csv = create_google_calendar_to_csv(URL, "./google_calendar_events.csv")
    calendar_df = pd.read_csv(google_calendar_csv)
    ibow_df = pd.read_csv(file_path, usecols=[0, 1, 11, 12, 13, 17, 25])
    start_end_dateformat(calendar_df, ibow_df)
    return calendar_df, ibow_df

# データフレームをマージし、一致しないデータを抽出

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

## メッセージを送信
def send_message(room_id, message):
    payload = {
        "self_unread": 0,
        "body": message
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/x-www-form-urlencoded",
        "x-chatworktoken": "415e3d094069523a8b9fb1828f36c8a4"
    }
    response = requests.post(f"{chatwork_base_url}/rooms/{room_id}/messages", data=payload, headers=headers)
    if response.status_code == 200:
        print("メッセージを送信しました。")
    else:
        print("エラーが発生しました。ステータスコード:", response.status_code)
        print(response.text)


def send_alerts(filtered_df: pd.DataFrame):
    for index, row in filtered_df.iterrows():
        room_id = managers.get(row['主訪問者'])
        if room_id:
            message = (
                f"以下のカレンダーとレセプトの内容が一致しませんでした.\n"
                f"訪問日: {row['訪問日']}\n"
                f"利用者名: {row['利用者名']}\n"
                f"サービス内容: {row['サービス内容']}\n"
                f"時間情報:\n"
                f"  - カレンダー時間:\n"
                f"    - 開始時間: {row['開始時間_カレンダー']}\n"
                f"    - 終了時間: {row['終了時間_カレンダー']}\n"
                f"    - 提供時間: {row['提供時間_カレンダー']}分\n"
                f"  - Ibow時間:\n"
                f"    - 開始時間: {row['開始時間_Ibow']}\n"
                f"    - 終了時間: {row['終了時間_Ibow']}\n"
                f"    - 提供時間: {row['提供時間_Ibow']}分"
            )
            send_message(room_id, message)
import requests
import pandas as pd
from server.libs.const_data import key_columns, check_columns, api_url
import io
from pathlib import Path
from tkinter import messagebox


def receipt_check(receipt_file, calendar_file):
    calendar_ids = calendar_ids_from_csv(calendar_file)
    calendar_df, ibow_df = get_dataframes(receipt_file, calendar_ids)
    results_df = merge_and_validate(calendar_df, ibow_df)
    results_df = results_df[
        ["訪問日", "利用者名", "主訪問者", "サービス内容", "開始時間_カレンダー", "開始時間_Ibow",
         "終了時間_カレンダー", "終了時間_Ibow",
         "提供時間_カレンダー", "提供時間_Ibow"]]
    return results_df


def calendar_ids_from_csv(csv_file):
    """
    カレンダーIDのCSVファイルを読み込み、カレンダーIDのリストを取得する
    :param csv_file: カレンダーIDのCSVファイル
    :return: カレンダーIDのリスト（,で連結された文字列）
    例外処理: FileNotFoundError, ValueError（CSVファイルの形式が間違っている場合）
    """
    try:
        # CSVをpandasのDataFrameとして読み込む
        df = pd.read_csv(csv_file)

        # 最低限必要なカラムが存在するかチェック
        if '担当者名' not in df.columns or 'カレンダーID' not in df.columns:
            messagebox.showerror("エラー", "カレンダーIDのファイルが誤っています。正しいファイルが選択されているか確認してください。")
            raise ValueError("カレンダーIDのCSVファイルを確認してください。")
        # カレンダーIDのリストを取得し、カンマ区切りの文字列に変換
        result = ",".join(df['カレンダーID'].astype(str).tolist())
        return result

    except FileNotFoundError:
        messagebox.showwarning("エラー", f"ファイル '{csv_file}' が見つかりませんでした。")
        print(f"エラー: ファイル '{csv_file}' が見つかりませんでした。")


# GoogleカレンダーのCSVデータを取得
def create_google_calendar_to_csv(url):
    """
    引数から受け取ったGASのURLを元にスクリプトを実行し、
    GoogleカレンダーのCSVデータを取得し、データフレームを作成する
    :param url: GASのURL
    :return calendar_df: Googleカレンダーのデータフレーム
    """
    try:
        response = requests.get(url)
        if response.status_code == 200:
            calendar_df = pd.read_csv(io.BytesIO(response.content), sep=",")
            return calendar_df
        elif response.status_code == 500:
            messagebox.showerror("エラー",
                                 "データの取得に失敗しました: 開発者にお問い合わせください。")
            raise ValueError("データの取得に失敗しました: 開発者にお問い合わせください。")
    except Exception:
        messagebox.showerror("エラー",
                             "Googleカレンダーの取得に失敗しました: カレンダーIDのファイルに誤りがないか確認してください。")
        raise ValueError(
            "Googleカレンダーの取得に失敗しました: カレンダーIDのファイルに誤りがないか確認してください。")

# 開始時間と終了時間のフォーマットを統一
def start_end_dateformat(df_1, df_2):
    """
    開始時間と終了時間のフォーマットを統一する
    :param df_1:
    :param df_2:
    :return:
    """
    columns = ['開始時間', '終了時間']
    for column in columns:
        # 開始時間と終了時間のフォーマットを統一
        df_1[column] = pd.to_datetime(df_1[column], format='%H:%M').dt.strftime('%H:%M')
        df_2[column] = pd.to_datetime(df_2[column], format='%H:%M').dt.strftime('%H:%M')


def get_dataframes(file_path: Path, calendar_ids: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    ファイルパスとカレンダーのIDからデータフレームを作成する
    :param file_path: receiptファイルのパス
    :param calendar_ids: カンマ（,)で連結されたカレンダーIDの文字列
    :return calendar_df, ibow_df: Googleカレンダーのデータフレーム, ibowのデータフレーム
    """
    # API URLを構築
    calendar_url = api_url
    calendar_url += "?calendarIds=" + calendar_ids

    # APIからカレンダーデータフレームを作成
    calendar_df = create_google_calendar_to_csv(calendar_url)

    # CSVファイルを読み込んで整形したibowデータフレームを作成
    try:
        ibow_df = pd.read_csv(file_path,
                              usecols=["訪問日", "利用者名", "開始時間", "終了時間", "提供時間", "サービス内容",
                                       "主訪問者"])
    except Exception:
        messagebox.showerror("エラー", "Ibowのファイルが誤っています。正しいファイルが選択されているか確認してください。")
        raise ValueError("Ibowのファイルが誤っています。正しいファイルが選択されているか確認してください。")

    # 日付フォーマットを統一
    start_end_dateformat(calendar_df, ibow_df)
    return calendar_df, ibow_df


def merge_and_validate(calendar_df: pd.DataFrame, ibow_df: pd.DataFrame) -> pd.DataFrame:
    """
    カレンダーとibowのデータフレームをマージし、不整合データを取得する
    :param calendar_df: カレンダーのデータフレーム
    :param ibow_df:
    :return filtered_df: 不整合データのデータフレーム
    """
    # 訪問日を日付型に変換
    calendar_df = calendar_df.sort_values(by=['訪問日', '開始時間'])

    # 日付を調整
    calendar_df['訪問日'] = pd.to_datetime(calendar_df['訪問日']).dt.tz_localize('Asia/Tokyo',
                                                                                 ambiguous='infer').dt.tz_localize(None)
    ibow_df['訪問日'] = pd.to_datetime(ibow_df['訪問日']).dt.tz_localize('Asia/Tokyo',
                                                                         ambiguous='infer').dt.tz_localize(None)

    # データフレームをマージ
    merged_df = pd.merge(calendar_df, ibow_df, on=key_columns, suffixes=('_カレンダー', '_Ibow'))
    for column in check_columns:
        merged_df[column + '_match'] = merged_df[column + '_カレンダー'] == merged_df[column + '_Ibow']

    filtered_df = merged_df[(merged_df['開始時間_match'] == False) | (merged_df['終了時間_match'] == False) & (
            merged_df['提供時間_match'] == False)]

    return filtered_df

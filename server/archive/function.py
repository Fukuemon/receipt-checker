import requests
import pandas as pd
from server.archive.const_data import key_columns, check_columns, calendar_gas_api_url, columns_to_replace, VALID_TIME_RANGES
import io
from pathlib import Path
from tkinter import messagebox
import re

# 定数として時間範囲を定義

# 半角数字を全角数字に変換する関数
def to_fullwidth_numbers(text):
    if isinstance(text, str):
        return ''.join(chr(ord(char) + 0xFEE0) if '0' <= char <= '9' else char for char in text)
    return text

# サービス内容の置き換え
def replace_service_content(service):
    if isinstance(service, str):
        service = re.sub(r'[Ⅰ１1]', 'I', service) # 1をIに変換
        service = re.sub(r'･', '・', service) # 半角ドットを全角ドットに変換
        service = to_fullwidth_numbers(service)
    return service


def receipt_check(receipt_file):
    calendar_df, ibow_df = get_dataframes(receipt_file)
    results_df = merge_and_validate(calendar_df, ibow_df)
    results_df = results_df[
        ["訪問日", "利用者名", "主訪問者", "サービス内容_Ibow", "サービス内容_カレンダー", "開始時間_Ibow",
         "開始時間_カレンダー",
         "終了時間_Ibow", "終了時間_カレンダー",
         "提供時間_Ibow", "提供時間_カレンダー", "加算①", "加算②"]]
    return results_df

def create_google_calendar_to_csv():
    """
    GoogleカレンダーのCSVデータを取得し、データフレームを作成する
    :return calendar_df: Googleカレンダーのデータフレーム
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

def start_end_dateformat(df_1: pd.DataFrame, df_2: pd.DataFrame, columns: list = ['開始時間', '終了時間']) -> None:
    """
    開始時間と終了時間のフォーマットを統一する
    :param df_1: データフレーム1
    :param df_2: データフレーム2
    :param columns: フォーマットを統一するカラム名のリスト
    :return: None
    """
    for column in columns:
        df_1[column] = pd.to_datetime(df_1[column], format='%H:%M').dt.strftime('%H:%M')
        df_2[column] = pd.to_datetime(df_2[column], format='%H:%M').dt.strftime('%H:%M')

def replace_fullwidth_to_halfwidth_space(df: pd.DataFrame, columns: list) -> None:
    """
    指定したカラム内の全角スペースを半角スペースに変換する
    :param df: データフレーム
    :param columns: カラム名のリスト
    :return: None
    """
    for column in columns:
        df[column] = df[column].apply(lambda text: text.replace('　', ' ') if isinstance(text, str) else text)

def get_dataframes(file_path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    ファイルパスとカレンダーのIDからデータフレームを作成する
    :param file_path: receiptファイルのパス
    :return: calendar_df, ibow_df: Googleカレンダーのデータフレーム, ibowのデータフレーム
    """
    # APIからカレンダーデータフレームを作成
    calendar_df = create_google_calendar_to_csv()

    # CSVファイルを読み込んで整形したibowデータフレームを作成
    try:
        ibow_df = pd.read_csv(file_path, encoding='utf-8',
                              usecols=["訪問日", "利用者名", "開始時間", "終了時間", "提供時間", "サービス内容",
                                       "主訪問者", "加算①", "加算②"])
    except UnicodeDecodeError:
        messagebox.showerror("エラー", "Ibowのファイルの文字コードが誤っています。UTF-8形式のファイルを選択してください。")
        raise ValueError("Ibowのファイルの文字コードが誤っています。UTF-8形式のファイルを選択してください。")
    except Exception:
        messagebox.showerror("エラー", "Ibowのファイルが誤っています。正しいファイルが選択されているか確認してください。")
        raise ValueError("Ibowのファイルが誤っています。正しいファイルが選択されているか確認してください。")

    # 日付フォーマットを統一
    start_end_dateformat(calendar_df, ibow_df)

    # 全角スペースを半角スペースに変換
    replace_fullwidth_to_halfwidth_space(ibow_df, columns_to_replace)
    replace_fullwidth_to_halfwidth_space(calendar_df, columns_to_replace)

    # サービス内容の置き換え
    calendar_df['サービス内容'] = calendar_df['サービス内容'].apply(replace_service_content)
    ibow_df['サービス内容'] = ibow_df['サービス内容'].apply(replace_service_content)

    return calendar_df, ibow_df

def validate_service_time(service, time):
    """
    サービス内容と提供時間の整合性をチェックし、有効範囲を返す
    :param service: サービス内容
    :param time: 提供時間
    :return: (bool, str) チェック結果と有効範囲の文字列
    """
    for key, (start, end) in VALID_TIME_RANGES.items():
        if key == service:
            if start <= time <= end:
                return True, f"(:({start}~{end}))"
            else:
                return False, f"(:({start}~{end}))"
    return False, ""

def merge_and_validate(calendar_df: pd.DataFrame, ibow_df: pd.DataFrame) -> pd.DataFrame:
    """
    カレンダーとibowのデータフレームをマージし、不整合データを取得する
    :param calendar_df: カレンダーのデータフレーム
    :param ibow_df: ibowのデータフレーム
    :return: final_df: 不整合データと整合データを結合したデータフレーム
    """
    # 訪問日を日付型に変換
    calendar_df['訪問日'] = pd.to_datetime(calendar_df['訪問日']).dt.tz_localize('Asia/Tokyo', ambiguous='infer').dt.tz_localize(None).dt.date
    ibow_df['訪問日'] = pd.to_datetime(ibow_df['訪問日']).dt.tz_localize('Asia/Tokyo', ambiguous='infer').dt.tz_localize(None).dt.date

    # データフレームをソート
    calendar_df = calendar_df.sort_values(by=['訪問日', '開始時間'])
    ibow_df = ibow_df.sort_values(by=['訪問日', '開始時間'])

    # 利用者名の空白を無視するために、全ての空白を削除
    calendar_df['利用者名'] = calendar_df['利用者名'].str.replace(' ', '')
    ibow_df['利用者名'] = ibow_df['利用者名'].str.replace(' ', '')

    # データフレームをマージ（片方しかデータがないものも出力するようにouter joinを使用）
    merged_df = pd.merge(calendar_df, ibow_df, on=key_columns, suffixes=('_カレンダー', '_Ibow'), how='outer')

    # 片方しかないデータをフィルタリング
    calendar_only_df = merged_df[merged_df[[col + '_Ibow' for col in check_columns]].isnull().all(axis=1)]
    ibow_only_df = merged_df[merged_df[[col + '_カレンダー' for col in check_columns]].isnull().all(axis=1)]

    # 片方しかないデータを除いたデータフレーム
    merged_df = merged_df[~(merged_df.index.isin(calendar_only_df.index) | merged_df.index.isin(ibow_only_df.index))]

    for column in check_columns:
        if column == 'サービス内容':
            merged_df[column + '_match'] = merged_df.apply(
                lambda row: row[column + '_カレンダー'] == row[column + '_Ibow'] or
                            (row[column + '_カレンダー'] == '医' and '基本療養費' in row[column + '_Ibow']), axis=1)
        else:
            merged_df[column + '_match'] = merged_df[column + '_カレンダー'] == merged_df[column + '_Ibow']

    # カレンダーとIbowの両方でチェック
    merged_df[['カレンダー_サービス時間_match', 'カレンダー_有効範囲']] = merged_df.apply(
        lambda row: pd.Series(validate_service_time(row['サービス内容_カレンダー'], row['提供時間_カレンダー'])), axis=1)

    merged_df[['Ibow_サービス時間_match', 'Ibow_有効範囲']] = merged_df.apply(
        lambda row: pd.Series(validate_service_time(row['サービス内容_Ibow'], row['提供時間_Ibow'])), axis=1)

    def mark_mismatch(row):
        for column in check_columns:
            if row[column + '_match'] is False:
                row[column + '_カレンダー'] = str(row[column + '_カレンダー']) + ' ❌'
                row[column + '_Ibow'] = str(row[column + '_Ibow']) + ' ❌'
        if row['カレンダー_サービス時間_match'] is False:
            row['提供時間_カレンダー'] = f"{row['提供時間_カレンダー']} (不正 {row['カレンダー_有効範囲']}) ❌"
        if row['Ibow_サービス時間_match'] is False:
            row['提供時間_Ibow'] = f"{row['提供時間_Ibow']} (不正 {row['Ibow_有効範囲']}) ❌"
        return row

    # 不整合データをフィルタリングし、❌をつける
    mismatched_df = merged_df[(merged_df['開始時間_match'] == False) |
                              (merged_df['終了時間_match'] == False) |
                              (merged_df['提供時間_match'] == False) |
                              (merged_df['サービス内容_match'] == False) |
                              (merged_df['カレンダー_サービス時間_match'] == False) |
                              (merged_df['Ibow_サービス時間_match'] == False)].apply(mark_mismatch, axis=1)

    matched_df = merged_df[(merged_df['開始時間_match'] == True) &
                           (merged_df['終了時間_match'] == True) &
                           (merged_df['提供時間_match'] == True) &
                           (merged_df['サービス内容_match'] == True) &
                           (merged_df['カレンダー_サービス時間_match'] == True) &
                           (merged_df['Ibow_サービス時間_match'] == True)]

    boundary_mismatched_df = pd.DataFrame({col: ['---'] for col in merged_df.columns})
    boundary_mismatched_df['訪問日'] = '不整合データ'

    boundary_matched_df = pd.DataFrame({col: ['---'] for col in merged_df.columns})
    boundary_matched_df['訪問日'] = '整合データ'

    boundary_calendar_only_df = pd.DataFrame({col: ['---'] for col in merged_df.columns})
    boundary_calendar_only_df['訪問日'] = 'カレンダーのみ'

    boundary_ibow_only_df = pd.DataFrame({col: ['---'] for col in merged_df.columns})
    boundary_ibow_only_df['訪問日'] = 'Ibowのみ'

    final_df = pd.concat([boundary_mismatched_df, mismatched_df,
                          boundary_calendar_only_df, calendar_only_df, boundary_ibow_only_df, ibow_only_df,
                          boundary_matched_df, matched_df], ignore_index=True)

    return final_df

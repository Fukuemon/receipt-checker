import requests
import pandas as pd
from server.libs.const_data import key_columns, check_columns, calendar_gas_api_url, columns_to_replace
import io
from pathlib import Path
from tkinter import messagebox


def receipt_check(receipt_file):
    calendar_df, ibow_df = get_dataframes(receipt_file)
    results_df = merge_and_validate(calendar_df, ibow_df)
    results_df = results_df[
        ["訪問日", "利用者名", "主訪問者", "サービス内容_Ibow", "サービス内容_カレンダー", "開始時間_Ibow",
         "開始時間_カレンダー",
         "終了時間_Ibow", "終了時間_カレンダー",
         "提供時間_Ibow", "提供時間_カレンダー"]]
    return results_df


# GoogleカレンダーのCSVデータを取得
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
            messagebox.showerror("エラー",
                                 "データの取得に失敗しました: 開発者にお問い合わせください。")
            raise ValueError("データの取得に失敗しました: 開発者にお問い合わせください。")
    except Exception:
        messagebox.showerror("エラー",
                             "データの取得に失敗しました: 開発者にお問い合わせください。")
        raise ValueError("データの取得に失敗しました: 開発者にお問い合わせください。")


# 開始時間と終了時間のフォーマットを統一
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
    :param calendar_ids: カンマ（,)で連結されたカレンダーIDの文字列
    :return calendar_df, ibow_df: Googleカレンダーのデータフレーム, ibowのデータフレーム
    """
    # APIからカレンダーデータフレームを作成
    calendar_df = create_google_calendar_to_csv()

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

    # 全角スペースを半角スペースに変換
    replace_fullwidth_to_halfwidth_space(ibow_df, columns_to_replace)
    replace_fullwidth_to_halfwidth_space(calendar_df, columns_to_replace)
    return calendar_df, ibow_df


def merge_and_validate(calendar_df: pd.DataFrame, ibow_df: pd.DataFrame) -> pd.DataFrame:
    """
    カレンダーとibowのデータフレームをマージし、不整合データを取得する
    :param calendar_df: カレンダーのデータフレーム
    :param ibow_df: ibowのデータフレーム
    :return final_df: 不整合データと整合データを結合したデータフレーム
    """

    # 訪問日を日付型に変換
    calendar_df['訪問日'] = pd.to_datetime(calendar_df['訪問日']).dt.tz_localize('Asia/Tokyo',
                                                                                 ambiguous='infer').dt.tz_localize(
        None).dt.date
    ibow_df['訪問日'] = pd.to_datetime(ibow_df['訪問日']).dt.tz_localize('Asia/Tokyo',
                                                                         ambiguous='infer').dt.tz_localize(None).dt.date

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
                lambda row: (row[column + '_カレンダー'] == row[column + '_Ibow']) or
                            (row[column + '_カレンダー'] == '医' and '基本療養費' in row[column + '_Ibow']), axis=1)
        else:
            merged_df[column + '_match'] = merged_df[column + '_カレンダー'] == merged_df[column + '_Ibow']

    # サービス内容と提供時間の整合性チェック
    # サービス内容と提供時間の整合性チェック
    def validate_service_time(service, time):
        if service in ['訪看Ⅰ２', '予防訪看Ⅰ２'] and 20 <= time <= 29:
            return True
        if service in ['訪看Ⅰ３', '予防訪看Ⅰ３'] and 30 <= time <= 59:
            return True
        if service in ['訪看Ⅰ４', '予防訪看Ⅰ４'] and 60 <= time <= 89:
            return True
        if service in ['訪看Ⅰ５', '予防訪看Ⅰ５'] and 21 <= time <= 40:
            return True
        if service in ['訪看Ⅰ５2超', '予防訪看Ⅰ５2超'] and 41 <= time <= 60:
            return True
        if '基本療養費' in service or service == '医':
            if 30 <= time <= 89:
                return True
        return False

    print(merged_df)
    # カレンダーとIbowの両方でチェック
    merged_df['カレンダー_サービス時間_match'] = merged_df.apply(
        lambda row: validate_service_time(row['サービス内容_カレンダー'], row['提供時間_カレンダー']), axis=1)

    merged_df['Ibow_サービス時間_match'] = merged_df.apply(
        lambda row: validate_service_time(row['サービス内容_Ibow'], row['提供時間_Ibow']), axis=1)

    # 不整合データをフィルタリング
    mismatched_df = merged_df[(merged_df['開始時間_match'] == False) |
                              (merged_df['終了時間_match'] == False) |
                              (merged_df['提供時間_match'] == False) |
                              (merged_df['サービス内容_match'] == False) |
                              (merged_df['カレンダー_サービス時間_match'] == False) |
                              (merged_df['Ibow_サービス時間_match'] == False)]

    # 整合データをフィルタリングÒ
    matched_df = merged_df[(merged_df['開始時間_match'] == True) &
                           (merged_df['終了時間_match'] == True) &
                           (merged_df['提供時間_match'] == True) &
                           (merged_df['サービス内容_match'] == True) &
                           (merged_df['カレンダー_サービス時間_match'] == True) &
                           (merged_df['Ibow_サービス時間_match'] == True)]

    # 境界線を作成
    boundary_mismatched_df = pd.DataFrame({col: ['---'] for col in merged_df.columns})
    boundary_mismatched_df['訪問日'] = '不整合データ'

    boundary_matched_df = pd.DataFrame({col: ['---'] for col in merged_df.columns})
    boundary_matched_df['訪問日'] = '整合データ'

    boundary_calendar_only_df = pd.DataFrame({col: ['---'] for col in merged_df.columns})
    boundary_calendar_only_df['訪問日'] = 'カレンダーのみ'

    boundary_ibow_only_df = pd.DataFrame({col: ['---'] for col in merged_df.columns})
    boundary_ibow_only_df['訪問日'] = 'Ibowのみ'

    # 最終データフレームを結合
    final_df = pd.concat([boundary_mismatched_df, mismatched_df,
                          boundary_calendar_only_df, calendar_only_df, boundary_ibow_only_df, ibow_only_df,
                          boundary_matched_df, matched_df], ignore_index=True)

    return final_df

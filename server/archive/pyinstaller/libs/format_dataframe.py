import pandas as pd
import re
from server.libs.constant import  COLUMNS_TO_DATETIME, COLUMNS_TO_REPLACES


def replace_service_content(service) -> str:
    """
    サービス内容の置き換え
    :param service: サービス内容
    :return: 変換後のサービス内容
    """

    # 半角数字を全角数字に変換
    def _to_fullwidth_numbers(text):
        if isinstance(text, str):
            return ''.join(chr(ord(char) + 0xFEE0) if '0' <= char <= '9' else char for char in text)
        return text

    if isinstance(service, str):
        service = re.sub(r'[Ⅰ１1]', 'I', service)  # 1をIに変換
        service = re.sub(r'･', '・', service)  # 半角ドットを全角ドットに変換
        service = _to_fullwidth_numbers(service)
    return service


def start_end_dateformat(df: pd.DataFrame, columns: list = COLUMNS_TO_DATETIME) -> None:
    """
    開始時間と終了時間のフォーマットを統一
    :param df: DataFrame
    :param columns: フォーマットを統一するカラム名のリスト(デフォルトはCOLUMNS_TO_DATETIME)
    :return: None
    """
    for column in columns:
        df[column] = pd.to_datetime(df[column], format='%H:%M').dt.strftime('%H:%M')


def replace_columns_spaces(df: pd.DataFrame, columns: list = COLUMNS_TO_REPLACES) -> None:
    """
    指定した列の全角スペースを半角スペースに変換する
    :param df: DataFrame
    :param columns: 変換する列名のリスト（デフォルトはCOLUMNS_TO_REPLACES）
    :return: None
    """

    def convert_fullwidth_to_halfwidth(text):
        if isinstance(text, str):
            return text.replace('　', ' ')
        return text

    for column in columns:
        df[column] = df[column].apply(convert_fullwidth_to_halfwidth)


def convert_to_date(df: pd.DataFrame, column_name: str = "訪問日") -> None:
    """
    指定したカラムを日付型に変換する
    """
    df[column_name] = pd.to_datetime(df[column_name]).dt.tz_localize('Asia/Tokyo', ambiguous='infer').dt.tz_localize(
        None).dt.date


def remove_whitespace(df: pd.DataFrame, column_name: str = "利用者名") -> None:
    """
    指定したカラムのすべての空白を削除する
    """
    df[column_name] = df[column_name].str.replace(' ', '')


def format_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    データフレームのフォーマットの整形
    :param df: DataFrame
    :return: 整形後のDataFrame
    """
    # 日付フォーマットの統一
    start_end_dateformat(df)

    # 全角スペースを半角スペースに変換
    replace_columns_spaces(df)

    # サービス内容の置き換え
    df["サービス内容"] = df["サービス内容"].apply(replace_service_content)

    # 日付型に変換
    convert_to_date(df)

    # 空白を削除
    remove_whitespace(df)

    # データフレームをソート
    df = df.sort_values(by=['訪問日', '開始時間'])

    return df


def format_dataframes(calendar_df: pd.DataFrame, ibow_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    カレンダーとibowのデータフレームのフォーマットの整形
    :param calendar_df: カレンダーのデータフレーム
    :param ibow_df: ibowのデータフレーム
    :return: 整形後のカレンダーのデータフレームとibowのデータフレーム
    """
    # 各データフレームをフォーマットする
    format_calendar_df = format_dataframe(calendar_df)
    format_ibow_df = format_dataframe(ibow_df)

    return format_calendar_df, format_ibow_df
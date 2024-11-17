from .get_dataframe import get_dataframes
from .validate_dataframe import merge_and_validate
from .format_dataframe import format_dataframes


def receipt_check(receipt_file):
    calendar_df, ibow_df = get_dataframes(receipt_file)
    calendar_df, ibow_df = format_dataframes(calendar_df, ibow_df)
    results_df = merge_and_validate(calendar_df, ibow_df)
    return results_df[
        ["訪問日", "利用者名", "主訪問者",  "サービス内容_カレンダー",
         "開始時間_カレンダー","終了時間_カレンダー","提供時間_カレンダー",
         "サービス内容_Ibow","開始時間_Ibow","終了時間_Ibow", "提供時間_Ibow", "加算"]].fillna('データなし')

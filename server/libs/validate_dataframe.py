import pandas as pd
from datetime import datetime
from .constant import SERVICE_CODE_VALID_TIME_RANGES, MERGE_KEY_COLUMNS, CHECK_COLUMNS, MATCH_COLUMNS


def merge_dataframes(calendar_df: pd.DataFrame, ibow_df: pd.DataFrame) -> pd.DataFrame:
    """
    2つのデータフレームを外部結合でマージする
    """
    return pd.merge(calendar_df, ibow_df, on=MERGE_KEY_COLUMNS, suffixes=('_カレンダー', '_Ibow'), how='outer')


def filter_mismatched_data(merged_df: pd.DataFrame) -> (pd.DataFrame, pd.DataFrame):
    """
    片方にしかないデータをフィルタリングする
    """
    calendar_only_df = merged_df[merged_df[[col + '_Ibow' for col in MATCH_COLUMNS]].isnull().all(axis=1)]
    ibow_only_df = merged_df[merged_df[[col + '_カレンダー' for col in MATCH_COLUMNS]].isnull().all(axis=1)]
    return calendar_only_df, ibow_only_df


def validate_service_time(service, time):
    """
    サービス内容と提供時間の整合性をチェックし、有効範囲を返す
    :param service: サービス内容
    :param time: 提供時間
    :return: (bool, str) チェック結果と有効範囲の文字列
    """
    # サービス内容がNaN（空の値）またはfloat型（不正な値）であれば、Falseを返す
    if pd.isna(service) or isinstance(service, float):
        return False, ""

    # サービス内容が特定の文字列を含む場合、対応するキーを設定
    if '基本療養費' in service:
        key = '基本療養費'
    elif '難病等複数回訪問' in service:
        key = '難病等複数回訪問加算(２回)'
    else:
        key = service

    # 通常のサービスコードに基づく時間範囲チェック
    if key not in SERVICE_CODE_VALID_TIME_RANGES:
        return False, ""

    start, end = SERVICE_CODE_VALID_TIME_RANGES[key]

    # Check if time is within the valid range
    if start <= time <= end:
        return True, f"{start}~{end}"
    else:
        return False, f"{start}~{end}"


def validate_service_times(merged_df: pd.DataFrame) -> pd.DataFrame:
    """
    サービス時間をチェックする
    """
    # DataFrameのコピーを作成してから操作
    merged_df = merged_df.copy()

    merged_df.loc[:, 'カレンダー_サービス時間_match'], merged_df.loc[:, 'カレンダー_有効範囲'] = zip(*merged_df.apply(
        lambda row: validate_service_time(row['サービス内容_カレンダー'], row['提供時間_カレンダー']), axis=1))

    merged_df.loc[:, 'Ibow_サービス時間_match'], merged_df.loc[:, 'Ibow_有効範囲'] = zip(*merged_df.apply(
        lambda row: validate_service_time(row['サービス内容_Ibow'], row['提供時間_Ibow']), axis=1))

    return merged_df


def validate_end_time(service, start_time, end_time):
    """
    サービス内容に基づいて終了時間が有効範囲内かをチェックする
    :param service: サービス内容
    :param start_time: 開始時間 (フォーマット: "HH:MM")
    :param end_time: 終了時間 (フォーマット: "HH:MM")
    :return: (bool, str) チェック結果と有効範囲の文字列
    """
    if pd.isna(service) or isinstance(service, float):
        return False, ""

    # サービス内容が特定の文字列を含む場合、対応するキーを設定
    if '基本療養費' in service:
        key = '基本療養費'
    elif '難病等複数回訪問' in service:
        key = '難病等複数回訪問加算(２回)'
    else:
        key = service

    # 通常のサービスコードに基づく時間範囲チェック
    if key not in SERVICE_CODE_VALID_TIME_RANGES:
        return False, ""

    start_minutes, end_minutes = SERVICE_CODE_VALID_TIME_RANGES[key]

    # Convert start and end time to datetime objects
    start_dt = datetime.strptime(start_time, "%H:%M")
    end_dt = datetime.strptime(end_time, "%H:%M")

    # Calculate duration in minutes
    duration_minutes = (end_dt - start_dt).seconds / 60

    # Check if duration is within valid range
    if start_minutes <= int(duration_minutes) <= end_minutes:
        return True, f"{start_minutes}~{end_minutes}"
    else:
        return False, f"{start_minutes}~{end_minutes}"


def check_columns(merged_df: pd.DataFrame) -> pd.DataFrame:
    """
    一致判定用のカラムを追加する
    """
    # DataFrameのコピーを作成してから操作
    validate_df = merged_df.copy()

    for column in CHECK_COLUMNS:
        if column == 'サービス内容':
            validate_df.loc[:, column + '_match'] = validate_df.apply(
                lambda row: (
                    row[column + '_カレンダー'] == row[column + '_Ibow'] or
                    (row[column + '_カレンダー'] == '医' and
                     isinstance(row[column + '_Ibow'], str) and  # 型チェックを追加
                     ('基本療養費' in row[column + '_Ibow'] or
                      '難病等複数回訪問' in row[column + '_Ibow']))
                ), axis=1)
        elif column == "開始時間":
            validate_df.loc[:, column + '_match'] = validate_df[column + '_カレンダー'] == validate_df[column + '_Ibow']
        elif column == "終了時間":
            validate_df.loc[:, column + '_match'] = validate_df[column + '_カレンダー'] == validate_df[column + '_Ibow']
            validate_df.loc[:, '終了時間_カレンダー_match'], validate_df.loc[:, '終了時間_カレンダー_有効範囲'] = zip(*validate_df.apply(
                lambda row: validate_end_time(
                    row['サービス内容_カレンダー'],
                    row['開始時間_カレンダー'],
                    row['終了時間_カレンダー']
                ), axis=1))
            validate_df.loc[:, '終了時間_Ibow_match'], validate_df.loc[:, '終了時間_Ibow_有効範囲'] = zip(*validate_df.apply(
                lambda row: validate_end_time(
                    row['サービス内容_Ibow'],
                    row['開始時間_Ibow'],
                    row['終了時間_Ibow']
                ), axis=1))
        elif column == "提供時間":
            validate_df.loc[:, column + '_match'] = validate_df[column + '_カレンダー'] == validate_df[column + '_Ibow']
            validate_df = validate_service_times(validate_df)
        elif column == "加算":
            validate_df.loc[:, '加算_check'] = validate_df[column].apply(lambda x: x == '通常')
        else:
            validate_df.loc[:, column + '_match'] = validate_df[column + '_カレンダー'] == validate_df[column + '_Ibow']

    return validate_df


def mark_mismatches(merged_df: pd.DataFrame) -> pd.DataFrame:
    """
    不整合データに❌マークを追加する
    """

    def mark_mismatch(row):
        for column in MATCH_COLUMNS:
            if row[column + '_match'] is False:
                row[column + '_カレンダー'] = str(row[column + '_カレンダー']) + ' ❌'
                row[column + '_Ibow'] = str(row[column + '_Ibow']) + ' ❌'
        if row["終了時間_カレンダー_match"] is False:
            row["終了時間_カレンダー"] = f"{row['終了時間_カレンダー']} ❌ ({row['終了時間_カレンダー_有効範囲']})"
        if row["終了時間_Ibow_match"] is False:
            row["終了時間_Ibow"] = f"{row['終了時間_Ibow']} ❌ ({row['終了時間_Ibow_有効範囲']})"
        if row['カレンダー_サービス時間_match'] is False:
            row['提供時間_カレンダー'] = f"{row['提供時間_カレンダー']}  ❌ ({row['カレンダー_有効範囲']})"
        if row['Ibow_サービス時間_match'] is False:
            row['提供時間_Ibow'] = f"{row['提供時間_Ibow']} ❌ ({row['Ibow_有効範囲']})"
        if row['加算_check'] is False:
            row['加算'] = f"{row['加算']} ※"
        return row

    mismatched_df = merged_df[(merged_df['開始時間_match'] == False) |
                              (merged_df['終了時間_カレンダー_match'] == False) |
                              (merged_df['終了時間_Ibow_match'] == False) |
                              (merged_df['サービス内容_match'] == False) |
                              (merged_df['カレンダー_サービス時間_match'] == False) |
                              (merged_df["加算_check"] == False) |
                              (merged_df['Ibow_サービス時間_match'] == False)].apply(mark_mismatch, axis=1)
    return mismatched_df


def create_boundary_dataframe(label: str, columns: list) -> pd.DataFrame:
    """
    境界データフレームを作成する
    """
    boundary_df = pd.DataFrame({col: ['---'] for col in columns})
    boundary_df['訪問日'] = label
    return boundary_df


def merge_and_validate(calendar_df: pd.DataFrame, ibow_df: pd.DataFrame) -> pd.DataFrame:
    merged_df = merge_dataframes(calendar_df, ibow_df)

    calendar_only_df, ibow_only_df = filter_mismatched_data(merged_df)

    # matchしているデータのみ抽出
    merged_df = merged_df[~(merged_df.index.isin(calendar_only_df.index) | merged_df.index.isin(ibow_only_df.index))]

    # データのvalidation
    validate_df = check_columns(merged_df)



    # 不整合データにマークを追加
    mismatched_df = mark_mismatches(validate_df)


    print(validate_df.columns)

    def mark_match(row):
        if row["提供時間_match"] is False and row["カレンダー_サービス時間_match"] is True and row["Ibow_サービス時間_match"] is True:
            row["提供時間_カレンダー"] = f"{row['提供時間_カレンダー']} ※ ({row['カレンダー_有効範囲']})"
            row["提供時間_Ibow"] = f"{row['提供時間_Ibow']} ※ ({row['Ibow_有効範囲']})"
        if row["終了時間_match"] is False and row["終了時間_Ibow_match"] is True and row["終了時間_カレンダー_match"] is True:
            row["終了時間_カレンダー"] = f"{row['終了時間_カレンダー']} ※"
            row["終了時間_Ibow"] = f"{row['終了時間_Ibow']} ※"

        return row
    # 整合データの抽出
    matched_df = validate_df[(validate_df['開始時間_match'] == True) &
                             (validate_df['サービス内容_match'] == True) &
                             (validate_df['終了時間_カレンダー_match'] == True) &
                             (validate_df['終了時間_Ibow_match'] == True) &
                             (validate_df['カレンダー_サービス時間_match'] == True) &
                             (validate_df['Ibow_サービス時間_match'] == True) &
                             (validate_df["加算_check"] == True)].apply(mark_match, axis=1)

    # 境界データフレームの作成
    boundary_mismatched_df = create_boundary_dataframe('不整合データ', merged_df.columns)
    boundary_matched_df = create_boundary_dataframe('整合データ', merged_df.columns)
    boundary_calendar_only_df = create_boundary_dataframe('カレンダーのみ', merged_df.columns)
    boundary_ibow_only_df = create_boundary_dataframe('Ibowのみ', merged_df.columns)

    # 最終的なデータフレームの作成
    final_df = pd.concat([boundary_mismatched_df, mismatched_df,
                          boundary_calendar_only_df, calendar_only_df,
                          boundary_ibow_only_df, ibow_only_df,
                          boundary_matched_df, matched_df], ignore_index=True)
    return final_df

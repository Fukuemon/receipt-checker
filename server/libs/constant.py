from dotenv import load_dotenv
from os.path import dirname, join
import os

load_dotenv(verbose=True)
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
CALENDER_GAS_API_URL="https://script.google.com/macros/s/AKfycbygVKDMEhnbeu4UKDB7TgAFaRQpegkJ8lh1vYFfkH0vR0dpFb2ewc_Qyh4Wz2ap3tlHGg/exec"

USE_IBOW_COLUMNS = ["訪問日", "利用者名", "開始時間", "終了時間", "提供時間", "サービス内容", "主訪問者", "加算①", "加算②", "加算③", "加算④", "加算⑤"]
COLUMNS_TO_DATETIME = ['開始時間', '終了時間']
COLUMNS_TO_REPLACES = ['主訪問者', '利用者名', 'サービス内容']
SERVICE_CODE_VALID_TIME_RANGES = {
    '訪看I２': (20, 29),
    '予防看I２': (20, 29),
    '予訪看I２': (20, 29),
    '予防訪看I２': (20, 29),
    '訪看I３': (30, 59),
    '予防看I３': (30, 59),
    '予訪看I３': (30, 59),
    '予防訪看I３': (30, 59),
    '訪看I４': (60, 89),
    '予防看I４': (60, 89),
    '予訪看I４': (60, 89),
    '予防訪看I４': (60, 89),
    '訪看I５': (21, 40),
    '予防看I５': (21, 40),
    '予訪看I５':(21, 40),
    '予防訪看I５': (21, 40),
    '訪看I５・２超': (41, 60),
    '訪看I５２超': (41, 60),
    '予防看I５・２超': (41, 60),
    '予訪看I５・２超': (41, 60),
    '予防訪看I５２超': (41, 60),
    '基本療養費': (30, 90),
    '医': (30, 90),
    '難病等複数回訪問加算(２回)': (30, 90)
}

MERGE_KEY_COLUMNS = ['訪問日', '利用者名', '主訪問者']

MATCH_COLUMNS = ['開始時間', '提供時間', 'サービス内容']

CHECK_COLUMNS = ['開始時間', '終了時間', '提供時間', 'サービス内容', "加算"]


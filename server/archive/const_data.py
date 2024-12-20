
# GoogleカレンダーapiのURLを指定
calendar_gas_api_url = "https://script.google.com/macros/s/AKfycbwanC_EH2aK7gJa97KJhOsM-CCqocDYxPY6ZaAlDie-uKDDxPkgtlvR-1IC3SajM9xPYw/exec"

default_calendar_ids = {
 "笠間　律子": "c_5cdab208784f5f4d735eace490690d8ab8f12e57f1abd21edd32bca125206d70@group.calendar.google.com",
 "竹房　和美": "c_d941630c89637f830aacdab897a4d6324090f005c36b1b1b54f6b6b8f39cce95@group.calendar.google.com"
}

columns_to_replace = ['主訪問者', '利用者名', 'サービス内容']

# サービスコードを指定
service_code = {
 '訪看Ⅰ２': 29,
 '訪看Ⅰ３': 59,
 '訪看Ⅰ４': 89,
 '訪看Ⅰ５': 40,
 '訪看Ⅰ５2超': 60,
 '予防訪看Ⅰ２': 29,
 '予防訪看Ⅰ３': 59,
 '予防訪看Ⅰ４': 89,
 '予防訪看Ⅰ５': 40,
 '予防訪看Ⅰ５2超':60,
 "基本療養費Ⅰ・３日": 60,
 "難病等複数回訪問加算(２回)":40
}

VALID_TIME_RANGES = {
    '訪看I２': (20, 29),
    '予防看I２': (20, 29),
    '訪看I３': (30, 59),
    '予防看I３': (30, 59),
    '訪看I４': (60, 89),
    '予防看I４': (60, 89),
    '訪看I５': (21, 40),
    '予防看I５': (21, 40),
    '訪看I５・２超': (41, 60),
    '予防看I５・２超': (41, 60),
    '基本療養費': (30, 90),
    '医': (30, 90),
    '難病等複数回訪問加算(２回)': (30, 90)
}


# マネージャーのIDを指定
managers = {
    '笠間　律子': 358398312,
    '竹房　和美': 358398319
}

# マージのキーカラムを指定
key_columns = ['訪問日', '利用者名', '主訪問者']
# 照合するカラムを指定
check_columns = ['開始時間', '終了時間', '提供時間', 'サービス内容']

# ChatworkのAPIのURLを指定
chatwork_base_url = "https://api.chatwork.com/v2"

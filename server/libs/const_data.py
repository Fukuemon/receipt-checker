# GoogleカレンダーapiのURLを指定
api_url = 'https://script.google.com/macros/s/AKfycbxBZ55s_KiGC8xGTpdoihdi14kJ7LSr9IPmy2bkxiNbZZNjJw8JOjpFV0rDuTiDZjnT/exec'

default_calendar_ids = {
 "笠間　律子": "c_5cdab208784f5f4d735eace490690d8ab8f12e57f1abd21edd32bca125206d70@group.calendar.google.com",
 "竹房　和美": "c_d941630c89637f830aacdab897a4d6324090f005c36b1b1b54f6b6b8f39cce95@group.calendar.google.com"
}

# サービスコードを指定
service_code = {'訪看Ⅰ２': '20-29',
 '訪看Ⅰ３': '30-59',
 '訪看Ⅰ４': '60-89',
 '訪看Ⅰ５': '21-40',
 '訪看Ⅰ５2超': '41-60',
 '予防訪看Ⅰ２': '20-29',
 '予防訪看Ⅰ３': '30-59',
 '予防訪看Ⅰ４': '60-89',
 '予防訪看Ⅰ５': '21-40',
 '予防訪看Ⅰ５2超':
 '41-60'
}

# マネージャーのIDを指定
managers = {
    '笠間　律子': 358398312,
    '竹房　和美': 358398319
}

# マージのキーカラムを指定
key_columns = ['訪問日', '利用者名', '主訪問者', 'サービス内容']
# 照合するカラムを指定
check_columns = ['開始時間', '終了時間', '提供時間']

# ChatworkのAPIのURLを指定
chatwork_base_url = "https://api.chatwork.com/v2"

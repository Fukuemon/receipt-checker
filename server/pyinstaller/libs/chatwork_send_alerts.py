import requests
import pandas as pd
from server.archive.const_data import managers, chatwork_base_url


# メッセージを送信
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

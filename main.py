import pandas as pd
import numpy as np
import os
from scraping import YahooKeibaScraper
from preprocess import clean_data
from feature_engineering import create_features
from train import train_model
from predict import predict_upcoming_race
import datetime

def run_prediction_pipeline():
    print("--- 競馬予測システム実行 ---")

    # 1. モデルの準備 (初回のみ、または定期的に実行)
    # 実際には大量の過去データで学習しますが、ここではダミーデータでモデルを生成します。
    # 既にモデルが存在する場合はスキップしても良いですが、ここでは毎回生成します。
    print("\n[フェーズ3] モデル学習 (ダミーデータ使用)")
    dummy_train_data = pd.DataFrame({
        'date': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05',
                                '2023-01-06', '2023-01-07', '2023-01-08', '2023-01-09', '2023-01-10']),
        'horse_id': [1, 2, 3, 4, 5, 1, 2, 3, 4, 5],
        'race_id': [101, 101, 101, 101, 101, 102, 102, 102, 102, 102],
        'rank': [1, 2, 3, 4, 5, 2, 1, 3, 5, 4],
        'weight': [480, 500, 470, 490, 510, 485, 505, 475, 495, 515],
        'odds': [2.5, 5.0, 1.8, 10.0, 3.0, 3.2, 2.0, 6.0, 12.0, 4.0],
        'distance': ['1600m', '1600m', '1600m', '1600m', '1600m', '1800m', '1800m', '1800m', '1800m', '1800m']
    })
    # 学習用ダミーデータも前処理（数値化・欠損値処理）を行ってから学習に渡す
    model, trained_features = train_model(clean_data(dummy_train_data))
    print("モデル学習完了。")

    # 2. 今週の土曜日のレースをシミュレート
    today = datetime.date(2026, 4, 23) # 現在の日付を2026年4月23日(木)と仮定
    # 次の土曜日を計算
    days_until_saturday = (5 - today.weekday() + 7) % 7 # 月曜=0, 土曜=5
    if days_until_saturday == 0: # 今日が土曜日の場合
        next_saturday = today
    else:
        next_saturday = today + datetime.timedelta(days=days_until_saturday)

    print(f"\n[フェーズ2] 今週の土曜日 ({next_saturday}) のレースデータを取得 (シミュレーション)")
    
    scraper = YahooKeibaScraper()
    # 最初のレースIDのみを取得する想定
    race_ids_for_saturday = scraper.fetch_race_ids_for_date(next_saturday)
    first_race_id = race_ids_for_saturday[0] if race_ids_for_saturday else None

    if not first_race_id:
        print("今週土曜日のレースIDが見つかりませんでした。")
        return

    # ダミーのレースデータ (今週土曜日のどこかの第一レースを想定)
    # 実際のデータは scraping.py で取得し、preprocess.py と feature_engineering.py で処理されます。
    # ここでは、それらの処理後の形式に近いダミーデータを作成します。
    # predict.py が期待するカラムを含める必要があります。
    simulated_race_data = pd.DataFrame({
        'date': [pd.to_datetime(next_saturday)] * 3,
        'horse_id': [101, 102, 103],
        'race_id': [first_race_id] * 3, # 取得した最初のレースIDを使用
        'weight': [490, 510, 485],
        'rank': [np.nan] * 3, # 特徴量生成スクリプトが参照するため、空の着順カラムを用意
        'odds': [3.5, 2.0, 7.0],
        'distance': ['1600m', '1600m', '1600m'],
        # feature_engineering.py で生成される可能性のある特徴量もダミーで含める
        'rank_avg_3': [3.0, 2.5, 4.0],
        # 他の特徴量も必要に応じて追加
    })
    
    # 前処理と特徴量生成 (ダミーデータに対して実行)
    processed_data = clean_data(simulated_race_data.copy())
    final_race_data = create_features(processed_data.copy())
    
    # 3. 予測と購入判断
    print("\n[フェーズ4] 予測と購入判断")
    # train.pyで学習した際の特徴量リストをpredict_upcoming_raceに渡す
    recommendations = predict_upcoming_race(final_race_data.copy(), model_path='models/lightgbm_model.pkl', feature_columns=trained_features)

    if not recommendations.empty:
        print(f"\n--- 今週土曜日 ({next_saturday}) の第一レース ({first_race_id}) 予測結果 (購入推奨馬) ---")
        print(recommendations.to_string(index=False))
        print("\n※この予測はダミーデータで学習・推論されたものであり、実際の精度を保証するものではありません。")
    else:
        print(f"\n今週土曜日 ({next_saturday}) の第一レース ({first_race_id}) で推奨する馬はいませんでした。")
        print("\n※この予測はダミーデータで学習・推論されたものであり、実際の精度を保証するものではありません。")

if __name__ == "__main__":
    run_prediction_pipeline()
import pandas as pd
import joblib
from train import calculate_expected_value, should_purchase

def predict_upcoming_race(race_data, model_path='models/lightgbm_model.pkl'):
    """
    ⑨ 本番運用: 予測から購入判断までの自動化
    """
    model = joblib.load(model_path)
    
    # 特徴量抽出
    # 注意: ここでは推論用にID系以外のカラムを特徴量として扱う
    features = [col for col in race_data.columns if col not in ['date', 'horse_id', 'race_id', 'odds']]
    
    # 勝率予測
    race_data['win_prob'] = model.predict(race_data[features])
    
    # 期待値計算
    race_data['expected_value'] = race_data.apply(
        lambda x: calculate_expected_value(x['win_prob'], x['odds']), axis=1
    )
    
    # 購入推奨馬の抽出
    recommendations = race_data[race_data.apply(
        lambda x: should_purchase(x['expected_value'], x['odds']), axis=1
    )]
    
    return recommendations[['horse_id', 'win_prob', 'odds', 'expected_value']]

if __name__ == "__main__":
    print("Prediction script initialized. Connect this to your daily scraping flow.")
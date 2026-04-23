import pandas as pd
import joblib
from train import calculate_expected_value, should_purchase

def predict_upcoming_race(race_data, model_path='models/lightgbm_model.pkl', feature_columns=None):
    """
    ⑨ 本番運用: 予測から購入判断までの自動化
    """
    model = joblib.load(model_path)
    
    # 特徴量抽出
    # train.pyで学習した際の特徴量リストを使用する
    if feature_columns is None:
        if hasattr(model, 'feature_name_'):
            features = model.feature_name_
        else:
            features = [col for col in race_data.columns if col not in ['rank', 'is_win', 'date', 'horse_id', 'race_id', 'odds']]
            print("Warning: feature_columns not provided and model does not have feature_name_. Using default exclusion list.")
    else:
        features = feature_columns
    
    # 予測に必要な特徴量がrace_dataに存在するか確認し、存在しない場合は0で埋める
    for f in features:
        if f not in race_data.columns:
            race_data[f] = 0 # 存在しない特徴量は0で埋めるか、適切なデフォルト値で埋める

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
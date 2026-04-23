import pandas as pd
import lightgbm as lgb
import joblib
import os
import numpy as np

def train_model(df):
    """
    ⑤ モデル学習: LightGBMによる学習
    """
    # ターゲットの作成 (1着=1, その他=0)
    target = 'is_win'
    if 'rank' in df.columns:
        df[target] = (df['rank'] == 1).astype(int)
    
    # 特徴量の選択 (ID系や日付を除外)
    features = [col for col in df.columns if col not in ['rank', 'is_win', 'date', 'horse_id', 'race_id']]
    
    # 時系列を考慮した分割 (8:2)
    df = df.sort_values('date')
    split_idx = int(len(df) * 0.8)
    train_df = df.iloc[:split_idx]
    val_df = df.iloc[split_idx:]
    
    X_train, y_train = train_df[features], train_df[target]
    X_val, y_val = val_df[features], val_df[target]
    
    # LightGBMデータセット
    train_data = lgb.Dataset(X_train, label=y_train)
    val_data = lgb.Dataset(X_val, label=y_val, reference=train_data)
    
    params = {
        'objective': 'binary',
        'metric': 'binary_logloss',
        'boosting_type': 'gbdt',
        'random_state': 42,
        'verbosity': -1
    }
    
    print("Training LightGBM model...")
    model = lgb.train(
        params,
        train_data,
        valid_sets=[train_data, val_data],
        callbacks=[lgb.early_stopping(stopping_rounds=10)]
    )
    
    os.makedirs('models', exist_ok=True)
    joblib.dump(model, 'models/lightgbm_model.pkl')
    return model, features

def calculate_expected_value(win_prob, odds):
    """
    ⑥ 期待値計算: 勝率 × オッズ
    """
    return win_prob * odds

def should_purchase(expected_value, odds, threshold=1.0):
    """
    ⑦ 購入ロジック: 期待値が閾値を超え、かつオッズが2.0以上の馬を推奨
    """
    return expected_value > threshold and odds >= 2.0

if __name__ == "__main__":
    # テスト用のダミーデータ作成
    data = pd.DataFrame({
        'date': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05']),
        'horse_id': [1, 2, 3, 4, 5],
        'rank': [1, 2, 1, 3, 1],
        'weight': [480, 500, 470, 490, 510],
        'odds': [2.5, 5.0, 1.8, 10.0, 3.0]
    })
    
    model, feat_cols = train_model(data)
    
    # 予測と購入判定のシミュレーション
    sample_prob = model.predict(data[feat_cols])[0]
    sample_odds = data.iloc[0]['odds']
    ev = calculate_expected_value(sample_prob, sample_odds)
    decision = should_purchase(ev, sample_odds)
    
    print(f"Sample Prediction - Prob: {sample_prob:.2f}, EV: {ev:.2f}, Purchase: {decision}")
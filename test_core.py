import pandas as pd
import numpy as np
import pytest
from preprocess import clean_data
from feature_engineering import create_features
from train import calculate_expected_value, should_purchase

def test_clean_data():
    df = pd.DataFrame({
        'distance': ['1600m', '2000m'],
        'weight': [480, np.nan]
    })
    cleaned = clean_data(df)
    assert cleaned['distance'].iloc[0] == 1600.0
    assert not cleaned['weight'].isnull().any()

def test_create_features():
    df = pd.DataFrame({
        'horse_id': [1, 1, 1, 1],
        'date': pd.to_datetime(['2023-01-01', '2023-02-01', '2023-03-01', '2023-04-01']),
        'rank': [1, 2, 3, 4]
    })
    features = create_features(df)
    # 4行目の rank_avg_3 は直近3走 [1, 2, 3] の平均 = 2.0 になるはず
    assert features['rank_avg_3'].iloc[3] == 2.0

def test_train_logic():
    # 期待値計算のテスト
    prob = 0.5
    odds = 3.0
    ev = calculate_expected_value(prob, odds)
    assert ev == 1.5
    
    # 購入判定のテスト
    assert should_purchase(ev, odds) is True
    assert should_purchase(0.9, 3.0) is False  # 期待値 < 1.0
    assert should_purchase(1.5, 1.5) is False  # オッズ < 2.0
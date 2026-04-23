import pandas as pd
import numpy as np

def clean_data(df):
    """
    基本的なクレンジング処理
    """
    # 欠損値処理
    df = df.fillna({
        'weight': df['weight'].mean() if 'weight' in df.columns else 0,
        'odds': 0
    })

    # 距離情報の数値化 (例: "1600m" -> 1600)
    if 'distance' in df.columns and df['distance'].dtype == 'object':
        df['distance'] = df['distance'].str.extract('(\d+)').astype(float)

    # 日付型の変換
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])

    return df

if __name__ == "__main__":
    # テスト用ダミーデータ
    dummy_df = pd.DataFrame({
        'distance': ['1600m', '2000m'],
        'weight': [480, np.nan]
    })
    print("Preprocessed data sample:\n", clean_data(dummy_df))
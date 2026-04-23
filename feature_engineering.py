import pandas as pd

def create_features(df):
    """
    特徴量生成: 直近成績の集計など
    """
    # 時系列でソート
    df = df.sort_values(['horse_id', 'date'])

    # 各馬の直近3走の平均着順
    df['rank_avg_3'] = df.groupby('horse_id')['rank'].transform(
        lambda x: x.rolling(window=3, min_periods=1).mean().shift(1)
    )

    # 騎手の勝率計算 (リーク防止のため過去データのみを使用)
    # 注: 本来的には学習データ内でのみ計算すべきですが、ここでは構造のみ示します
    
    return df

if __name__ == "__main__":
    # テスト用ダミーデータ
    dummy_df = pd.DataFrame({
        'horse_id': [1, 1, 1, 1],
        'date': pd.to_datetime(['2023-01-01', '2023-02-01', '2023-03-01', '2023-04-01']),
        'rank': [5, 2, 1, 3]
    })
    features = create_features(dummy_df)
    print("Feature engineering sample:\n", features[['horse_id', 'date', 'rank_avg_3']])
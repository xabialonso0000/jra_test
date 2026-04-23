import pandas as pd
import joblib
import os
from train import calculate_expected_value, should_purchase

def run_backtest(df, model_path='models/lightgbm_model.pkl'):
    """
    ⑧ バックテスト: 過去データでのシミュレーション
    """
    if not os.path.exists(model_path):
        print(f"Model file {model_path} not found.")
        return

    model = joblib.load(model_path)
    
    # 特徴量の選択 (train.pyの学習時と同じ特徴量を使用)
    features = [col for col in df.columns if col not in ['rank', 'is_win', 'date', 'horse_id', 'race_id']]
    
    # 予測（勝率）
    df['win_prob'] = model.predict(df[features])
    
    # 期待値計算と購入判定
    df['expected_value'] = df.apply(lambda x: calculate_expected_value(x['win_prob'], x['odds']), axis=1)
    df['is_bought'] = df.apply(lambda x: should_purchase(x['expected_value'], x['odds']), axis=1)
    
    # 回収率の計算
    bought_horses = df[df['is_bought']]
    total_investment = len(bought_horses)
    # 1着(rank=1)の馬のオッズ合計が払戻金
    total_payout = bought_horses[bought_horses['rank'] == 1]['odds'].sum()
    
    recovery_rate = (total_payout / total_investment) if total_investment > 0 else 0
    
    print(f"--- Backtest Results ---")
    print(f"Total Races/Horses: {len(df)}")
    print(f"Total Investment: {total_investment} units")
    print(f"Total Payout: {total_payout:.1f} units")
    print(f"Recovery Rate: {recovery_rate:.2%}")
    
    return recovery_rate

if __name__ == "__main__":
    print("Backtest script initialized. Ready to run with historical data.")
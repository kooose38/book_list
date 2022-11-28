'''Create PFI modules.
Usage:
    > from permutatino_importance import PermutationFeatureImportance
    > pfi = PermutationFeatureImportance(model, x, y, var_names)
    > pfi.permutation_feature_importance()
    > pfi.plot()

'''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error # 分類の場合は必要に応じて変更する

@dataclass
class PermutationFeatureImportance:
    '''PFIを算出するクラス

    Args:
        model: 学習済モデル
        x: テストデータの特徴量
        y: テストデータの正解ラベル
        var_names: 特徴量の名称リスト
    
    '''

    model: Any
    x: np.ndarray
    y: np.ndarray
    var_names: list[str]

    def __post_init__(self) -> None:
        '''シャッフルしない場合のベースラインとなる予測精度
        '''
        self.baseline = mean_squared_error(
            self.y, self.model.predict(self.x), squared=False
        )

    def _permutation_metrics(self, idx: int) -> float:
        '''idx番目の特徴量をシャッフルしたときのモデルの予測精度を算出する
        
        Args:
            idx: シャッフルする特徴量のインデックス番号
        '''
        # 実行ごとの上書を防ぐ
        x_permuted = self.x.copy()
        # 指定された特徴量をランダムにシャッフルして学習済モデルで予測精度を算出する
        x_permuted[:, idx] = np.random.permutation(
            x_permuted[:, idx]
        )
        y_pred = self.model.predict(x_permuted)
        
        return mean_squared_error(
            self.y, y_pred, squared=False
        ) 

    def permutation_feature_importance(self, n_shuffle: int=10) -> None:
        '''PFIを求める

        Args:
            n_shuffle: 各特徴量をシャッフルする回数。数が多いほど安定する。
        '''
        # 特徴量の個数
        J = self.x.shape[1]
        # 特徴量の分だけループする
        metrics_permuted = []
        for j in range(J):
            # n_shuffleの分だけ予測精度を算出し、平均値をとる
            _metrics_permuted = [self._permutation_metrics(j) for _ in range(n_shuffle)]
            metrics_permuted.append(np.mean(_metrics_permuted))

        data_features = pd.DataFrame({
            'var_names': self.var_names,
            'baseline': self.baseline,
            'permutation': metrics_permuted,
            'difference': metrics_permuted - baseline, # 差分
            'ratio': metrics_permuted / baseline, # 比率
        })

        self.feature_importance = data_features.sort_values('permutation', ascending=False)

    def plot(self, importance_type: str='difference') -> None:
        '''PFIを可視化する

        Args:
            importance_type: 差分・比率の選択をする
        '''

        fig, ax = plt.subplots()
        ax.barh(
            self.feature_importance['var_names'],
            self.feature_importance[importance_type],
            label=f'baseline: {self.baseline:.2f}'
        )
        ax.set(
            xlabel=importance_type, ylabel=None
        )
        ax.invert_yaxis()
        ax.legend(loc='lower right')
        fig.suptitle(f'PFIによる特徴量の重要度（{importance_type}）')

        fig.show()

        

# GPFIの実装をする
'''Plot PD
    Usage:
    > from partical_dependece import ParticalDependence
    pd = ParticalDependence(model, x_test, var_names)
    pd.partical_dependence(var_name)
    pd.plot()

'''

import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt 

@dataclass
class ParticalDependence:
    '''PDクラス

    Args:
        model: 学習済モデル
        x: testデータの特徴量
        var_names: 特徴量の名前リスト
    '''
    model: Any
    x: np.ndarray
    var_names: list[str]

    def _counterfactual_prediction(self, var_index: int, value_to_replace: float) -> np.ndarray:
        '''ある特徴量を引数で指定された値に変更して、モデルで予測する

        Args:
            var_index: PDを算出する特徴量のindex
            value_to_replace: 変更値
        '''

        x_replaced = self.x.copy()
        x_replaced[:, var_index] = value_to_replace

        return self.model(x_replaced)

    def partical_dependence(self, var_name: str, n_grid: int=50) -> None:
        '''指定された特徴量のPDを算出する

        Args:
            var_name: PD を算出したい特徴量名
            n_grid: var_nameの最大 - 最小の幅数
        '''
        self.target_var_name = var_name 
        var_index = self.var_names.index(self.target_var_name)
        # 指定した特徴量のレンジ幅を作成する
        self.value_range = np.linspace(
            self.x[:, var_index].min(),
            self.x[:, var_index].max()
        )
        # レンジごとの予測平均を算出する
        average_prediction = []
        for x in self.value_range:
            # 全テストデータに対して、ある特徴量をxに変更したときの予測平均を返す
            _avg_predict = self._counterfactual_prediction(var_index, x).mean()
            average_prediction.append(_avg_predict)
        average_prediction = np.array(average_prediction)

        self.df_partical_dependence = pd.DataFrame({
            'var_name': self.value_range , 
            'avg_pred': average_prediction
        })

    def plot(self, ylim = None) -> None:
        '''結果を描画する

        '''

        fig, ax = plt.subplots()
        ax.plot(
            self.df_partical_dependence['var_name'],
            self.df_partical_dependence['avg_pred']
        )
        ax.set(
            xlabel = self.target_var_name,
            ylabel = 'Average Prediction.',
            ylim = (
                self.x[:, self.var_index].min(),
                self.x[:, self.var_index].max()
            )
        )
        fig.suptitle(f'Partical Dependence Plot ({self.target_var_name})')
        fig.show()

    



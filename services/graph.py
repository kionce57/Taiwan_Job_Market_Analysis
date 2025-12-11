import matplotlib.pyplot as plt
import pandas as pd


class Graphmarker:
    def __init__(self):
        try:
            plt.rcParams["font.family"] = ["Microsoft JhengHei"]
            plt.rcParams["axes.unicode_minus"] = False

            pd.set_option("display.max_rows", 15)
            pd.set_option("display.max_columns", 10)
            pd.set_option("display.width", 100)
        except Exception:
            pass

    def _use_104bronze_make_dataframe(self, datas: list[list[dict]]) -> pd.DataFrame:
        df = pd.DataFrame(datas)
        series = df.stack()
        df_flat = pd.DataFrame(series.to_list())

        return df_flat

    # def make_graph(figsize:tuple, )
    # # 基本: 圖的大小, 一或二個變數(先不考慮更多), label, 圖的類型, 內容物(線, 柱子)的顏色, x 軸與 y 軸的名稱與圖表名稱,

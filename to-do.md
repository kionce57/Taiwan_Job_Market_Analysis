# Description

分成 Crawler, Database, Graph, Heart(control crawler, db, Graph)

## 使用流程

1. 鍵入 keyword, area(只允許到縣市級別)
2. 爬取資料
3. 清洗與整理 (Bronze?)
4. 存放進 Non-SQL(不能省略, 它能直接儲存 json 格式, 非常簡單)
5. 更深入的清洗與整理, 尤其是 job description 中那些非結構化資料, 很多企業喜歡把真正的工作細節與要求藏在那裏(但我時間
應該不夠)(Silver?)
6. 根據已有的資料建幾張圖表出來
    e.g. 薪水面議出現的次數以及最常出現在哪個職稱,
    善用工具中出現次數前三的是哪些,
    要求工作經歷 1 年以上的工作的薪水中位數與平均值是多少?
    學歷的要求分布

最簡單的:
    一個 DF -> [工作名, salary, 學歷, workExp, major]
    第二個 工具 -> [公司名, Python, Linux, NLP, LLM,....] -> 有要求就T, 沒有就F, 可以統計工具出現總次數之類的
    第三個 技能 -> [公司名, Machine Learning, AI,....] -> 如上
    第二跟第三具有公司名是預留給第一個 merge 的空間

## dev step

可省略除了 Bronze 以外的清洗儲存步驟, 直接從任一步開始建立圖表

A. Extract
    1. 逆向工程 API
    2. 拆解 resp 的資料結構
    3. 先剔除掉最不需要的資料欄位
    x. try-except 查不到工作的情況

B. Load: 先將剃除過的 json 格式的資料儲存到 MongoDB (Bronze)

C. Transformer: 建圖表, 建 DF

B. Load: 從 db 取出資料進行二次清洗,  (Silver)

C. Transformer: 建圖表, 建 DF

D. 針對這個資料模型要做什麼樣的資料分析?

## 簡報結構

1. 簡述程序的功能, 使用到的技術(Python, uv, powerBI, MongoDB Altas), 簡單一句話講述使用(uv, MongoDB, PowerBI)的原因
    - uv: 用來管理專案環境, 非常簡單好上手
    - MongoDB Altas: 用來儲存非結構化資料, 例如 JSON, 使用雲端則是個人嘗試
    - PowerBI: 我用它做的圖比 Matplot 好看
2. 描述資料 pipe
3. 展示成果(3個圖表)

## Log

Non-SQL 是我面對儲存問題時想到的解法, 不過因為我沒用過 Non-SQL 所以拿著想法與 todo.md 與爬取資料的 pattern 去跟 Gemini 討論作業流程是否是個好的解法

儲存問題: 要從爬取的 JSON 資料中將其分門別類, 建立多個互相關聯的 table 實在過於繁瑣與複雜, 且使用上也不如直接拿 JSON 資料來的便利與簡單

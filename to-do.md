# Description

分成 Crawler, Database, Graph, Heart(control crawler, db, Graph)

## 使用流程

### 無資料情況
1. 爬取
2. 存入 DB
3. 從 DB 讀取資料
4. 篩選資料
5. 建圖表

### 有資料情況
1. 從 DB 讀取資料
2. 篩選資料
3. 建圖表


## dev step

可省略除了 Bronze 以外的清洗儲存步驟, 直接從任一步開始建立圖表

A. Extract
    1. 逆向工程 API
    2. 拆解 resp 的資料結構
    3. 先剔除掉最不需要的資料欄位
    x. try-except 查不到工作的情況 (if data == [], 已處理)

B. Load: 先將剃除過的 json 格式的資料儲存到 MongoDB (Bronze)

C. Question: 針對這個資料模型要做什麼樣的資料分析?

D. Transformer: 建圖表, 建 DF

D. Load: 從 db 取出資料進行二次清洗, 有需要可以存到 Silver db

E. Transformer: 根據需求建立 DataFrame 以供 PowerBI 使用

F. 

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

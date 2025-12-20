#!/bin/bash
set -e

# 檢查是否讀取到必要的環境變數，若無則報錯 (Strong Typing 概念)
if [ -z "$MYSQL_CRAWLER_USER" ] || [ -z "$MYSQL_CRAWLER_PASSWORD" ]; then
    echo "Error: CRAWLER user environment variables are not set."
    exit 1
fi

if [ -z "$MYSQL_WEB_USER" ] || [ -z "$MYSQL_WEB_PASSWORD" ]; then
    echo "Error: WEB user environment variables are not set."
    exit 1
fi

echo "Creating custom users..."

# 使用 heredoc 語法將 SQL 注入 MySQL
# 注意：這裡使用 root 權限登入 (腳本執行當下 root 密碼已由官方腳本設定完成)
mysql -u root -p"$MYSQL_ROOT_PASSWORD" <<-EOSQL
    -- 建立 Crawler 使用者
    CREATE USER IF NOT EXISTS '$MYSQL_CRAWLER_USER'@'%' IDENTIFIED BY '$MYSQL_CRAWLER_PASSWORD';
    GRANT ALL PRIVILEGES ON \`$MYSQL_DATABASE\`.* TO '$MYSQL_CRAWLER_USER'@'%';

    -- 建立 Web 使用者
    CREATE USER IF NOT EXISTS '$MYSQL_WEB_USER'@'%' IDENTIFIED BY '$MYSQL_WEB_PASSWORD';
    GRANT SELECT, INSERT, UPDATE, DELETE ON \`$MYSQL_DATABASE\`.* TO '$MYSQL_WEB_USER'@'%';

    FLUSH PRIVILEGES;
EOSQL

echo "Custom users created successfully."
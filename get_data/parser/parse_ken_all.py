from sqlalchemy import create_engine

from parse_utils import make_ken_all, merge_lines, preproc_ken_all, set_index, to_narrow

# DB接続
SQLALCHEMY_DATABASE_URL = "sqlite:///../../fastapi/zipcode.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# DF作成
ken_all = make_ken_all("../crawler/csv/KEN_ALL.CSV")

# インデックス追加
set_index(ken_all)

# 全角 -> 半角
for column_name, _ in ken_all.items():
    ken_all[column_name] = ken_all[column_name].apply(to_narrow)

# 町域名のマージ
ken_all = merge_lines(ken_all)

# 前処理
ken_all = preproc_ken_all(ken_all)

# idはintにしてDBに書き込み（上書き）
ken_all["id"] = ken_all["id"].astype(int)
ken_all.to_sql("ken_all", con=engine, if_exists="replace", index=False)

print("done: parse ken_all")

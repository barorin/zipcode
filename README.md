# 郵便番号 API

## Overview

郵便番号と住所を相互変換する API です。  
API 部分は FastAPI で実装しています。

![zipcode_api](https://user-images.githubusercontent.com/38820722/196036226-47501943-b8d1-44e6-af8d-c6cc4fd3a40c.png)

## Requirement

- Ubuntu 20.04
- Python 3.8.10

## Usage

```bash
# Install libraries
cd zipcode
pip install -r requirements.txt

# Crawling
cd get_data/crawler
python get_csv.py

# Parse
cd ../
cd parser
python get_ken_all.py
python get_jigyosyo.py

# Run FastAPI
cd ../../
cd fastapi
uvicorn main:app

# Access
http://127.0.0.1:8000/docs
```

## Reference

- [FastAPI](https://fastapi.tiangolo.com/)

## Author

[Mastodon - @barorin](https://fedibird.com/@barorin)  
[Blog - barorin&?](https://barorin-to.com)

## Licence

[MIT](https://github.com/barorin/fir_watcher/blob/master/LICENSE)

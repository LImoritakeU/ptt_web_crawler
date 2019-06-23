啟動 pipeline方法，

## subscriber
```
觸發條件：pubsub
主題：ptt_urls
ram: 1G
逾時：540 seconds
環境變數
role: subscriber
board: Gossiping
```

`subscriber` 需要較多的concurrency 確保 9 分鐘能運行完畢，`subscriber` 本身不處理任何狀態，
僅處理url列表，以往是多個worker 各自儲存，現在改成最後收集起來一次儲存一個大檔進s3。

## publisher
```
觸發條件：cloud scheduler
時間：每天早上9點
ram: 256 mb
逾時： 540 seconds
環境變數：
role: publisher
board: Gossiping
```

`publisher` 有順序與狀態，每天處理完的結果會除存在 `ptt_crawl_v2` bucket 的 `pub` 目錄內，並且更新
bucket root 的 `status.json` ，一般來說只需要使用到 last_timestamp_utc+8 即可，然而如果subscriber 
處理失敗，可以再次從 initial_timestamp_utc+8 重新處理，由於是單執行緒，天數過多可能會跑不完。

## retry
可以從 `ptt_crawl_v2/pub` 找尋適當的inital_timestamp, last_timestamp 執行。
pipeline 本身沒有處理重複的功能，

## 使用GCP pubsub 建構爬蟲 pipeline 

1. 與傳統架構不同，serverless 大多都要特別注意逾時問題，不論是publisher與subscriber在遇到爬取多天文章時都
極有可能逾時，這在傳統long runtime較不需特別考慮。
2. config 與status放在 gcs bucket ，取用並不像本地端這麼容易。
3. 盡量讓運行函數需要較少的 status
4. 設計函數時，需盡量同時考慮到本地偵錯，相較之下，aws有sam框架，在本地運行docker模擬aws lambda，
即使如此，這些偵錯都還是比傳統做法費時費工，對於單元測試可能要更加注重。
5. 不要為了切函數而切分函數，每一次切分都要先確認是否有必要，並且最好先設計出介面與 input/output 格式。
6. 同屬於一個大的目的的各個處理函數可以考慮寫在同一個project，指定不同handler 即可，較容易一併管理。
7. 在這種serverless的架構中，每個作用域都先天受限，可以多考慮使用全局變數。

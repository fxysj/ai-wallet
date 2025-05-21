✅ 1. 导出为 CSV 文件（默认导出全部记录）
curl -X GET "http://localhost:8000/db/v1/agent_record/export/csv" -o agent_records.csv

✅ 如果只导出指定用户的记录（例如用户 ID 为 user123）：
curl -X GET "http://localhost:8000/db/v1/agent_record/export/csv?user_id=user123" -o agent_records_user123.csv


✅ 2. 导出为 Excel 文件（默认导出全部记录）

curl -X GET "http://localhost:8000/db/v1/agent_record/export/excel" -o agent_records.xlsx

 如果只导出指定用户的记录（例如用户 ID 为 user123）：
 
curl -X GET "http://localhost:8000/db/v1/agent_record/export/excel?user_id=user123" -o agent_records_user123.xlsx

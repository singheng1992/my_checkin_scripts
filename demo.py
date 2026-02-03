import base64
import requests

url = "https://open.bigmodel.cn/api/paas/v4/layout_parsing"

# 读取本地文件并转换为 base64
with open("local_file.png", "rb") as f:
    file_base64 = base64.b64encode(f.read()).decode("utf-8")

payload = {
    "model": "GLM-OCR",
    "file": file_base64,
}
headers = {"Authorization": "Bearer <token>", "Content-Type": "application/json"}

response = requests.post(url, json=payload, headers=headers)

print(response.text)

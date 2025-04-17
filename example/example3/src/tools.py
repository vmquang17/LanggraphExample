import json
import requests
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig

# Định nghĩa các tham số Agent cần truyền vào khi gọi Tool
class GetGoldAndWeatherInput(BaseModel):
    query: str = Field(description="search query to look up")

    
# @tool("GetGoldAndWeather", args_schema=GetGoldAndWeatherInput)
def GetGoldAndWeather(query: str = "") -> str:
    """Used to retrieve weather info and gold prices."""
    api_url = "https://webapi.dantri.com.vn/misc"
    response = requests.request("GET", api_url)
    status_code = response.status_code
    if status_code != 200:
        return {
            "result": "error",
            "note": "Trả lời xin lỗi hiện tại không lấy được thông tin này."
        }
    body = response.json()
    body['description'] = "Thông tin hôm nay."

    formatted_body_golds = []
    for el in body['golds']:
        el['buy'] = el['buy'] + "0000 VNĐ/cây"
        el['sell'] = el['sell'] + "0000 VNĐ/cây"
        formatted_body_golds.append(el)
    body['golds'] = formatted_body_golds
    print(body)
    return {
        "result": body,
        "note": """
        - Nếu hỏi về thời tiết, nhận diện vị trí địa lý trong user_message có trong result/body không. Nếu có thì trả lời mỗi vị trí đó. Nếu không, có thì báo Không có thông tin.
        - Nếu hỏi về giá vàng, mặc định lấy thông tin ở Hà Nội. Đơn vị tính 1 cây vàng = 10 chỉ vàng.
        Yêu cầu: TRẢ LỜI NGẮN GỌN. Xưng mình là em."""
    }

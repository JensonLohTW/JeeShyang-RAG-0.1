from langchain.tools import Tool
from server.agent.tools import *

tools = [
    Tool.from_function(
        func=duckgosearch,
        name="DuckDuckGoSearch",
        description="useful for when you need to search the internet for information",
        args_schema=DuckGoSearchInput,
    ),
    Tool.from_function(
        func=get_weather,
        name="GetWeather",
        description="你是一个善于获取天气的智能助手",
        args_schema=GetWeatherInput,
    ),

]

tool_names = [tool.name for tool in tools]

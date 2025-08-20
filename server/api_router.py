#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi.staticfiles import StaticFiles
from typing import List
from pathlib import Path
from configs import logger

from typing import Union
from fastapi import FastAPI
from server.chat.chat import chat
import uvicorn
import argparse
from fastapi.middleware.cors import CORSMiddleware


def create_app(run_mode: str = None):
    app = FastAPI(
        title="JeeShyang-RAG API Server",
    )
    # Add CORS middleware to allow all origins
    # 在config.py中设置OPEN_DOMAIN=True，允许跨域
    # set OPEN_DOMAIN=True in config.py to allow cross-domain

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 挂载路由
    mount_app_routes(app)

    # 挂载 Vue 构建的前端静态文件夹（若存在且包含 index.html）
    static_dir = Path("static/dist")
    index_file = static_dir / "index.html"
    if static_dir.exists() and index_file.exists():
        app.mount("/", StaticFiles(directory=str(static_dir)), name="static")
        msg = f"Static files mounted from: {static_dir}"
        print(msg)
        try:
            logger.info(msg)
        except Exception:
            pass
    else:
        warn = f"[Warning] Static directory '{static_dir}' not found or empty (no index.html). API will run without frontend. Endpoints under /api/* remain available."
        print(warn)
        try:
            logger.warning(warn)
        except Exception:
            pass
    return app



from server.verify.utils import create_conversation, get_user_conversations, get_conversation_messages, ConversationResponse, MessageResponse
from server.chat.knowledge_base_chat import knowledge_base_chat
from server.chat.search_engine_chat import search_engine_chat
from server.chat.recommendation_chat import recommend_base_chat
from server.chat.agent_chat import agent_chat


def mount_app_routes(app: FastAPI):
    """
    这里定义通用领域问答对话的接口
    """
    
    # 大模型对话接口
    app.post("/api/chat",
             tags=["Chat"],
             summary="大模型对话交互接口",
             )(chat)

    # 新建会话接口
    app.post("/api/conversations",
             tags=["Conversations"],
             summary="新建会话接口",
             )(create_conversation)

    # 获取用户会话列表接口
    app.get("/api/users/{user_id}/conversations",  # 确保路径正确表示用户ID的参数化
             response_model=List[ConversationResponse],  # 使用正确的响应模型
             tags=["Users"],
             summary="获取指定用户的会话列表",
             )(get_user_conversations)

    # # 通用知识库问答接口
    app.post("/api/chat/knowledge_base_chat",
             tags=["Chat"],
             summary="与知识库对话")(knowledge_base_chat)

    # 获取会话消息列表接口
    app.get("/api/conversations/{conversation_id}/messages",
             response_model=List[MessageResponse],  # 使用正确的响应模型
             tags=["Messages"],
             summary="获取指定会话的消息列表",
             )(get_conversation_messages)
             
    app.post("/api/chat/search_engine_chat",
             tags=["Chat"],
             summary="与搜索引擎对话",
             )(search_engine_chat)

    app.post("/api/chat/recommend_chat",
             tags=["Chat"],
             summary="推荐",
             )(recommend_base_chat)

    app.post("/api/chat/agent_chat",
             tags=["Chat"],
             summary="Agent对话能力",
             )(agent_chat)



def run_api(host, port, **kwargs):
    if kwargs.get("ssl_keyfile") and kwargs.get("ssl_certfile"):
        uvicorn.run(app,
                    host=host,
                    port=port,
                    ssl_keyfile=kwargs.get("ssl_keyfile"),
                    ssl_certfile=kwargs.get("ssl_certfile"),
                    )
    else:
        uvicorn.run(app, host=host, port=port)




if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="localhost")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--ssl_keyfile", type=str)
    parser.add_argument("--ssl_certfile", type=str)
    # 初始化消息
    args = parser.parse_args()
    args_dict = vars(args)

    app = create_app()

    run_api(host=args.host,
            port=args.port,
            ssl_keyfile=args.ssl_keyfile,
            ssl_certfile=args.ssl_certfile,
            )
    
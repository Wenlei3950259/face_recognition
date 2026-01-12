import base64
import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional, List
from contextlib import asynccontextmanager

import cv2
import numpy as np
from fastapi import FastAPI, File, UploadFile, Form, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel, Field

# 导入核心算法模块
from core.face_core import encode_embedding, decode_embedding, cosine_similarity
from config import config
from face_process.init_InsightFace import init_face_model, detect_faces_async

"""
______________________________
  Author: wen_l
   Time : 2024-11-01
______________________________
"""

# -------------------------- Pydantic 模型 --------------------------
class ExtractRequest(BaseModel):
    """人脸特征提取请求模型"""
    image_type: str = Field(default="base64", description="图片类型：base64 或 file")
    image: str = Field(..., description="base64编码的图片数据")

class SimilarityRequest(BaseModel):
    """相似度计算请求模型"""
    current_embedding: str = Field(..., description="当前人脸特征向量")
    known_embeddings: List[str] = Field(..., description="已知人脸特征向量列表")

# -------------------------- 日志配置 --------------------------
# -------------------------- 日志配置 --------------------------
log_level = config.get("log.level", "INFO")
log_file_rel = config.get("log.file", "log/face_recognition.log")
max_bytes = config.get("log.max_bytes", 10 * 1024 * 1024)
backup_count = config.get("log.backup_count", 5)

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
log_file_abs = os.path.join(project_root, log_file_rel)

log_dir = os.path.dirname(log_file_abs)
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logger = logging.getLogger(__name__)
logger.setLevel(logging.getLevelName(log_level))
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s")

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
file_handler = RotatingFileHandler(
    log_file_abs,
    maxBytes=max_bytes,
    backupCount=backup_count,
    encoding="utf-8"
)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

# -------------------------- 应用生命周期管理 --------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用启动和关闭时的生命周期管理"""
    # 启动时初始化模型
    logger.info("🚀 正在初始化人脸识别模型...")
    await init_face_model()
    logger.info("✅ 模型初始化完成")
    yield
    # 关闭时清理资源
    logger.info("🔄 应用关闭，清理资源...")

# -------------------------- FastAPI 应用初始化 --------------------------
app = FastAPI(
    title="人脸识别系统 API",
    description="基于 InsightFace 的人脸特征提取和相似度计算服务",
    version="2.0.0",
    lifespan=lifespan
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 限流配置
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

THRESHOLD = config.get("face_model.threshold", 0.5)


# -------------------------- 工具函数 --------------------------
async def decode_image(image_data, image_type: str):
    """异步解码图片（支持base64和文件流）"""
    try:
        if image_type == "base64":
            base64_str = image_data.split(",")[-1] if "," in image_data else image_data
            img_bytes = base64.b64decode(base64_str)
        else:  # file
            img_bytes = await image_data.read()

        np_arr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if frame is None:
            raise ValueError("图片解码失败，格式不支持")
        return frame
    except Exception as e:
        logger.error(f"图片解码失败（类型：{image_type}）", exc_info=True)
        return None


# -------------------------- 核心API接口 --------------------------
@app.post('/api/face/extract')
@limiter.limit("10/second")
async def extract_face_feature(
    request: Request,
    image_type: Optional[str] = Form(default="file"),
    image: Optional[UploadFile] = File(default=None),
    body: Optional[ExtractRequest] = None
):
    """人脸检测+特征提取接口（给Java调用）
    
    支持两种调用方式：
    1. JSON格式：{"image_type": "base64", "image": "base64编码的图片"}
    2. 表单格式：multipart/form-data，image_type=file，image为文件
    """
    client_ip = request.client.host
    logger.info(f"收到人脸特征提取请求（IP：{client_ip}）")

    try:
        # 处理不同的请求格式
        if body is not None:
            # JSON 请求
            image_type_val = body.image_type
            image_data = body.image
        elif image is not None:
            # 表单请求
            image_type_val = image_type
            image_data = image
        else:
            return JSONResponse(
                status_code=400,
                content={
                    "code": 400,
                    "msg": "未传入图片数据",
                    "data": None
                }
            )

        # 解码图片
        frame = await decode_image(image_data, image_type_val)
        if frame is None:
            return JSONResponse(
                status_code=400,
                content={
                    "code": 400,
                    "msg": "图片解析失败",
                    "data": {"retry_interval": 1000}
                }
            )

        # 异步检测人脸并提取特征
        faces = await detect_faces_async(frame)
        if len(faces) == 0:
            return JSONResponse(
                status_code=200,
                content={
                    "code": 201,
                    "msg": "未检测到人脸",
                    "data": {"retry_interval": 800}
                }
            )
        if len(faces) > 1:
            return JSONResponse(
                status_code=200,
                content={
                    "code": 202,
                    "msg": "检测到多个人脸",
                    "data": {"retry_interval": 1000}
                }
            )

        # 返回特征向量
        face = faces[0]
        embedding_str = await encode_embedding(face.embedding)
        return JSONResponse(
            status_code=200,
            content={
                "code": 200,
                "msg": "特征提取成功",
                "data": {
                    "face_bbox": [int(v) for v in face.bbox],
                    "embedding": embedding_str
                }
            }
        )

    except Exception as e:
        logger.error(f"特征提取异常", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "msg": f"提取失败：{str(e)}",
                "data": None
            }
        )


@app.post('/api/face/calculate')
@limiter.limit("10/second")
async def calculate_similarity(request: Request, body: SimilarityRequest):
    """相似度计算接口（给Java调用）"""
    client_ip = request.client.host
    logger.info(f"收到相似度计算请求（IP：{client_ip}）")

    try:
        # 解码特征向量
        current_embedding = await decode_embedding(body.current_embedding)
        known_embeddings = [await decode_embedding(emb_str) for emb_str in body.known_embeddings]

        # 计算相似度
        similarities = await cosine_similarity(known_embeddings, current_embedding)

        return JSONResponse(
            status_code=200,
            content={
                "code": 200,
                "msg": "相似度计算成功",
                "data": {
                    "similarities": similarities.tolist()
                }
            }
        )

    except Exception as e:
        logger.error(f"相似度计算异常", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "msg": f"计算失败：{str(e)}",
                "data": None
            }
        )


@app.get('/health')
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "service": "face-recognition-api"}


# -------------------------- 启动服务 --------------------------
if __name__ == "__main__":
    import uvicorn
    
    host = config.get("server.host", "0.0.0.0")
    port = config.get("server.port", 5000)
    
    logger.info(f"🚀 人脸核心算法服务启动中（{host}:{port}）")
    
    uvicorn.run(
        "face_recognition_api:app",
        host=host,
        port=port,
        reload=False,
        workers=1,  # 由于模型是全局单例，使用单worker
        log_level="info"
    )

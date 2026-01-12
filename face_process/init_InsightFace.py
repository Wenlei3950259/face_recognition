import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from insightface.app import FaceAnalysis
from config import config
"""
______________________________
  Author: wen_l
   Time : 2024-11-01
______________________________
"""
# 初始化日志
logger = logging.getLogger(__name__)

# 全局模型实例
face_model = None
# 线程池用于执行CPU密集型任务
executor = ThreadPoolExecutor(max_workers=4)

def _init_face_model():
    """初始化InsightFace模型（单例模式）- 同步版本"""
    global face_model
    if face_model is None:
        try:
            # 从配置读取模型参数
            det_size = tuple(config.get("face_model.det_size"))
            providers = config.get("face_model.providers")

            # 初始化模型
            face_model = FaceAnalysis(providers=providers)
            face_model.prepare(ctx_id=0, det_size=det_size)
            logger.info(f"✅ 人脸模型初始化成功（检测尺寸：{det_size}，计算后端：{providers}）")
        except Exception as e:
            logger.error("❌ 人脸模型初始化失败", exc_info=True)
            raise
    return face_model

async def init_face_model():
    """异步初始化人脸模型"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, _init_face_model)

def get_face_model():
    """获取已初始化的模型实例"""
    return face_model

async def detect_faces_async(frame):
    """异步人脸检测"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, face_model.get, frame)
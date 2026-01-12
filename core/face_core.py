import base64
import logging
from typing import List
import numpy as np
import torch
"""
______________________________
  Author: wen_l
   Time : 2024-11-01
______________________________
"""
logger = logging.getLogger(__name__)

# 特征向量编解码（供Java端存储使用）
async def encode_embedding(embedding: np.ndarray) -> str:
    """将numpy特征向量转为base64字符串（供Java存储）"""
    try:
        return base64.b64encode(embedding.tobytes()).decode("utf-8")
    except Exception as e:
        logger.error("特征向量编码失败", exc_info=True)
        raise

async def decode_embedding(embedding_str: str) -> np.ndarray:
    """将base64字符串转回numpy特征向量（用于相似度计算）"""
    try:
        return np.frombuffer(base64.b64decode(embedding_str), dtype=np.float32)
    except Exception as e:
        logger.error("特征向量解码失败", exc_info=True)
        raise

# 相似度计算核心逻辑
async def cosine_similarity(known_encodings: List[np.ndarray], current_encoding: np.ndarray) -> np.ndarray:
    """计算余弦相似度（CPU版）"""
    with torch.no_grad():
        known = torch.tensor(known_encodings, dtype=torch.float32)
        current = torch.tensor(current_encoding, dtype=torch.float32)
        known_norm = torch.linalg.norm(known, dim=1)
        current_norm = torch.linalg.norm(current)
        return (torch.matmul(known, current) / (known_norm * current_norm)).numpy()
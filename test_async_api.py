#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
异步 API 测试脚本
用于验证接口兼容性和功能正确性
"""
import asyncio
import aiohttp
import base64
import json
from pathlib import Path

API_BASE_URL = "http://localhost:5000"


async def test_health_check():
    """测试健康检查接口"""
    print("\n=== 测试健康检查接口 ===")
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_BASE_URL}/health") as resp:
            result = await resp.json()
            print(f"状态码: {resp.status}")
            print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
            return resp.status == 200


async def test_extract_base64(image_path: str):
    """测试特征提取接口（base64格式）"""
    print("\n=== 测试特征提取接口（base64格式）===")
    
    # 读取测试图片
    if not Path(image_path).exists():
        print(f"❌ 测试图片不存在: {image_path}")
        return False
    
    with open(image_path, "rb") as f:
        image_bytes = f.read()
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    
    # 发送请求
    async with aiohttp.ClientSession() as session:
        payload = {
            "image_type": "base64",
            "image": image_base64
        }
        async with session.post(
            f"{API_BASE_URL}/api/face/extract",
            json=payload
        ) as resp:
            result = await resp.json()
            print(f"状态码: {resp.status}")
            print(f"响应码: {result.get('code')}")
            print(f"消息: {result.get('msg')}")
            if result.get('code') == 200:
                data = result.get('data', {})
                print(f"人脸框: {data.get('face_bbox')}")
                print(f"特征向量长度: {len(data.get('embedding', ''))}")
                return data.get('embedding')
            return None


async def test_extract_file(image_path: str):
    """测试特征提取接口（文件格式）"""
    print("\n=== 测试特征提取接口（文件格式）===")
    
    if not Path(image_path).exists():
        print(f"❌ 测试图片不存在: {image_path}")
        return False
    
    async with aiohttp.ClientSession() as session:
        with open(image_path, "rb") as f:
            data = aiohttp.FormData()
            data.add_field('image_type', 'file')
            data.add_field('image', f, filename='test.jpg')
            
            async with session.post(
                f"{API_BASE_URL}/api/face/extract",
                data=data
            ) as resp:
                result = await resp.json()
                print(f"状态码: {resp.status}")
                print(f"响应码: {result.get('code')}")
                print(f"消息: {result.get('msg')}")
                if result.get('code') == 200:
                    data = result.get('data', {})
                    print(f"人脸框: {data.get('face_bbox')}")
                    print(f"特征向量长度: {len(data.get('embedding', ''))}")
                    return data.get('embedding')
                return None


async def test_calculate_similarity(embedding1: str, embedding2: str):
    """测试相似度计算接口"""
    print("\n=== 测试相似度计算接口 ===")
    
    if not embedding1 or not embedding2:
        print("❌ 缺少特征向量，跳过测试")
        return False
    
    async with aiohttp.ClientSession() as session:
        payload = {
            "current_embedding": embedding1,
            "known_embeddings": [embedding2]
        }
        async with session.post(
            f"{API_BASE_URL}/api/face/calculate",
            json=payload
        ) as resp:
            result = await resp.json()
            print(f"状态码: {resp.status}")
            print(f"响应码: {result.get('code')}")
            print(f"消息: {result.get('msg')}")
            if result.get('code') == 200:
                similarities = result.get('data', {}).get('similarities', [])
                print(f"相似度: {similarities}")
                return True
            return False


async def test_concurrent_requests(image_path: str, num_requests: int = 10):
    """测试并发请求"""
    print(f"\n=== 测试并发请求（{num_requests}个）===")
    
    if not Path(image_path).exists():
        print(f"❌ 测试图片不存在: {image_path}")
        return
    
    with open(image_path, "rb") as f:
        image_bytes = f.read()
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    
    async def single_request(session, idx):
        payload = {
            "image_type": "base64",
            "image": image_base64
        }
        try:
            async with session.post(
                f"{API_BASE_URL}/api/face/extract",
                json=payload
            ) as resp:
                result = await resp.json()
                return idx, result.get('code'), resp.status
        except Exception as e:
            return idx, None, str(e)
    
    async with aiohttp.ClientSession() as session:
        tasks = [single_request(session, i) for i in range(num_requests)]
        results = await asyncio.gather(*tasks)
        
        success_count = sum(1 for _, code, _ in results if code == 200)
        print(f"✅ 成功: {success_count}/{num_requests}")
        print(f"❌ 失败: {num_requests - success_count}/{num_requests}")


async def main():
    """主测试流程"""
    print("=" * 60)
    print("人脸识别异步 API 测试")
    print("=" * 60)
    
    # 1. 健康检查
    await test_health_check()
    
    # 2. 准备测试图片（需要用户提供）
    test_image = "test_face.jpg"  # 请替换为实际的测试图片路径
    
    if not Path(test_image).exists():
        print(f"\n⚠️  请将测试人脸图片放置在: {test_image}")
        print("或修改 test_image 变量指向实际图片路径")
        return
    
    # 3. 测试特征提取（base64）
    embedding1 = await test_extract_base64(test_image)
    
    # 4. 测试特征提取（文件）
    embedding2 = await test_extract_file(test_image)
    
    # 5. 测试相似度计算
    if embedding1 and embedding2:
        await test_calculate_similarity(embedding1, embedding2)
    
    # 6. 测试并发
    await test_concurrent_requests(test_image, num_requests=10)
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n测试中断")
    except Exception as e:
        print(f"\n测试异常: {e}")

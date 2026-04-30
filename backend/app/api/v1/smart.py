from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import httpx
import json
import re
import os
from typing import List
import base64

from app.schemas.metric import SmartParseRequest, HealthAdviceRequest
from app.api.deps import get_current_user, get_db
from app.crud import metric as crud_metric
from app.config import settings
from app.utils.logger import get_logger

router = APIRouter(dependencies=[Depends(get_current_user)])
logger = get_logger(__name__)

MODEL_NAME = "deepseek-chat"

def _deepseek_headers() -> dict:
    if not settings.deepseek_api_key:
        raise HTTPException(status_code=500, detail="未配置 DEEPSEEK_API_KEY")
    return {
        "Authorization": f"Bearer {settings.deepseek_api_key}",
        "Content-Type": "application/json",
    }

def _deepseek_url(path: str) -> str:
    return f"{settings.deepseek_base_url.rstrip('/')}{path}"

@router.post("/")
async def parse_smart_text(request: SmartParseRequest):
    """
    使用 DeepSeek 智能解析自然语言体检指标文本，返回 JSON 格式
    """
    prompt = f"""你是一个专业的医疗数据提取助手。
请从以下自然语言文本或表格数据中提取所有的体检指标数据。
要求：
1. 严格返回合法的 JSON 对象格式，不要有任何多余的解释文字、代码块标记。
2. JSON 的键为清理后的指标名称（去掉前面的星号等符号），值为一个对象，包含以下字段：
   - "value": 指标的具体数值（必须是浮点数，去掉 ↑/↓ 等符号）。
   - "unit": 单位（如果没有提取到则为 null）。
   - "expected_min": 参考值/期望区间的最小值（浮点数，如果没有则为 null）。
   - "expected_max": 参考值/期望区间的最大值（浮点数，如果没有则为 null）。
3. 如果遇到类似 "(0-10)" 的参考值，提取 0 为 expected_min，10 为 expected_max。
4. 如果遇到类似 "(>80)" 的参考值，提取 80 为 expected_min，expected_max 为 null。
5. 如果遇到类似 "(<3.4)" 的参考值，提取 3.4 为 expected_max，expected_min 为 null。
6. 如果没有提取到任何指标，返回空对象 {{}}。

待解析文本：
"{request.text}"
"""
    
    user_content = []
    if request.images:
        user_content.append({"type": "text", "text": prompt})
        for img in request.images:
            user_content.append({
                "type": "image_url",
                "image_url": {"url": img}
            })
    else:
        user_content = prompt

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "你是一个严格输出JSON格式数据的医疗数据提取助手。"},
            {"role": "user", "content": user_content}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.1
    }
    headers = _deepseek_headers()
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(_deepseek_url("/chat/completions"), json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            raw_response = result.get("choices", [{}])[0].get("message", {}).get("content", "{}").strip()
            
            # 尝试清理可能存在的 markdown 标记
            raw_response = re.sub(r'^```json\s*', '', raw_response)
            raw_response = re.sub(r'\s*```$', '', raw_response)
            
            try:
                parsed_data = json.loads(raw_response)
                return parsed_data
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON from Ollama response: {raw_response}")
                raise HTTPException(status_code=500, detail="模型返回的数据无法解析为JSON格式")
                
    except httpx.RequestError as e:
        logger.error(f"Error connecting to DeepSeek: {str(e)}")
        raise HTTPException(status_code=502, detail="连接 AI 服务失败")
    except Exception as e:
        logger.error(f"Unexpected error in smart parse: {str(e)}")
        raise HTTPException(status_code=500, detail="智能解析过程发生未知错误")

@router.post("/upload")
async def parse_smart_file(files: List[UploadFile] = File(...)):
    """
    上传文件（支持多图、PDF 或 TXT），提取文本或图片后使用 DeepSeek 智能解析
    """
    text_content = ""
    images_base64 = []

    for file in files:
        content = await file.read()
        filename = file.filename.lower()

        if filename.endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif')):
            encoded = base64.b64encode(content).decode('utf-8')
            mime_type = "image/jpeg"
            if filename.endswith('.png'): mime_type = "image/png"
            elif filename.endswith('.webp'): mime_type = "image/webp"
            elif filename.endswith('.gif'): mime_type = "image/gif"
            images_base64.append(f"data:{mime_type};base64,{encoded}")
        elif filename.endswith('.pdf'):
            try:
                import PyPDF2
                import io
                reader = PyPDF2.PdfReader(io.BytesIO(content))
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text_content += extracted + "\n"
            except Exception as e:
                logger.error(f"Failed to parse PDF {filename}: {str(e)}")
                raise HTTPException(status_code=400, detail=f"PDF解析失败: {filename} - {str(e)}")
        else:
            # 尝试解码为文本
            try:
                text_content += content.decode('utf-8') + "\n"
            except UnicodeDecodeError:
                try:
                    text_content += content.decode('gbk') + "\n"
                except UnicodeDecodeError:
                    raise HTTPException(status_code=400, detail=f"不支持的文件格式或编码: {filename}，仅支持图片、PDF和文本文件")

    text_content = text_content.strip()
    if not text_content and not images_base64:
        raise HTTPException(status_code=400, detail="未能从文件中提取到有效内容")

    # 限制文本长度避免超出上下文 (截取前 8000 个字符)
    request = SmartParseRequest(
        text=text_content[:8000] if text_content else "请从以下图片中提取所有的体检指标数据：",
        images=images_base64 if images_base64 else None
    )
    return await parse_smart_text(request)

@router.post("/advice")
async def generate_health_advice(request: HealthAdviceRequest, db: Session = Depends(get_db)):
    """
    根据人员的所有体检指标历史数据，使用 DeepSeek 生成健康建议
    """
    # 1. 获取人员信息和所有指标记录
    persons = crud_metric.get_persons(db, limit=1000)
    person = next((p for p in persons if p.id == request.person_id), None)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")

    records = crud_metric.get_metrics(db, person_id=request.person_id, limit=1000)
    if not records:
        raise HTTPException(status_code=400, detail="该人员暂无体检数据，无法生成建议")

    # 2. 按指标对记录进行分组和排序，整理成提示词需要的格式
    metrics_data = {}
    for record in records:
        metric_name = record.metric.name
        if metric_name not in metrics_data:
            metrics_data[metric_name] = {
                "unit": record.metric.unit or "",
                "expected_min": record.metric.expected_min,
                "expected_max": record.metric.expected_max,
                "history": []
            }
        metrics_data[metric_name]["history"].append({
            "date": record.record_date.isoformat(),
            "value": record.value
        })

    # 将历史记录按日期升序排序，以便大模型看出趋势
    for metric_name in metrics_data:
        metrics_data[metric_name]["history"].sort(key=lambda x: x["date"])

    # 3. 构造提示词
    gender_info = f"（性别：{person.gender}）" if person.gender else ""
    prompt = f"""你是一位经验丰富、专业且贴心的全科医生。
现在你需要为一位名叫“{person.name}”{gender_info}的用户提供一份健康评估和生活建议报告。

以下是该用户近期记录的各项体检指标历史数据及其参考正常范围：
"""
    for metric_name, data in metrics_data.items():
        range_str = "未提供"
        if data["expected_min"] is not None and data["expected_max"] is not None:
            range_str = f"{data['expected_min']} - {data['expected_max']}"
        elif data["expected_min"] is not None:
            range_str = f"≥ {data['expected_min']}"
        elif data["expected_max"] is not None:
            range_str = f"≤ {data['expected_max']}"
            
        prompt += f"\n- 【{metric_name}】(单位: {data['unit']}, 参考范围: {range_str})\n"
        for h in data["history"]:
            prompt += f"  > {h['date']}: {h['value']}\n"

    prompt += """
请你根据以上数据：
1. 找出异常或处于临界值的指标，并指出其随时间变化的趋势（变好还是恶化）。
2. 分析可能导致这些异常的原因。
3. 给出具体、可操作的改善建议（包括饮食、运动、作息或复查建议）。
4. 语言要通俗易懂，态度要温暖关怀。

请使用 Markdown 格式输出排版精美的报告。不要包含无关的开头或结尾寒暄，直接输出报告内容。
"""

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "你是一位专业的健康顾问医生。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.5
    }
    headers = _deepseek_headers()
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(_deepseek_url("/chat/completions"), json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            advice_content = result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            if not advice_content:
                raise HTTPException(status_code=500, detail="模型未返回有效内容")
                
            return {"advice": advice_content}
                
    except httpx.RequestError as e:
        logger.error(f"Error connecting to DeepSeek: {str(e)}")
        raise HTTPException(status_code=502, detail="连接 AI 服务失败")
    except Exception as e:
        logger.error(f"Unexpected error in generating advice: {str(e)}")
        raise HTTPException(status_code=500, detail="生成健康建议过程发生未知错误")

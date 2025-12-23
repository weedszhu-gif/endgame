from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# 导入服务层
from services.socratic_hint import generate_socratic_hint
from services.ai_service import get_ai_hint

router = APIRouter(prefix="/api", tags=["math-challenge"])

# 请求和响应模型
class StepRequest(BaseModel):
    content: str
    use_ai: bool = False

class HintResponse(BaseModel):
    type: str = "hint"
    content: str

class HealthResponse(BaseModel):
    status: str
    message: str

@router.post("/hint", response_model=HintResponse)
async def get_hint(request: StepRequest):
    """
    获取解题提示
    
    - **content**: 解题步骤内容
    - **use_ai**: 是否直接使用AI（默认False，先尝试本地规则）
    """
    try:
        if request.use_ai:
            # 直接使用AI
            hint = await get_ai_hint(request.content)
        else:
            # 先尝试本地规则
            hint = generate_socratic_hint(request.content)
            if not hint:
                # 本地规则没有匹配时，使用AI
                hint = await get_ai_hint(request.content)
        
        return HintResponse(content=hint)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取提示失败: {str(e)}")

@router.post("/socratic-hint", response_model=HintResponse)
def get_socratic_hint(request: StepRequest):
    """
    获取基于本地规则的苏格拉底式提示
    
    - **content**: 解题步骤内容
    """
    try:
        hint = generate_socratic_hint(request.content)
        if not hint:
            raise HTTPException(status_code=404, detail="没有找到匹配的提示规则")
        
        return HintResponse(content=hint)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取提示失败: {str(e)}")

@router.post("/ai-hint", response_model=HintResponse)
async def get_ai_hint_endpoint(request: StepRequest):
    """
    获取基于AI的提示
    
    - **content**: 解题步骤内容
    """
    try:
        hint = await get_ai_hint(request.content)
        return HintResponse(content=hint)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取AI提示失败: {str(e)}")

@router.get("/health", response_model=HealthResponse)
def health_check():
    """
    健康检查
    """
    return HealthResponse(status="ok", message="API服务正常运行")

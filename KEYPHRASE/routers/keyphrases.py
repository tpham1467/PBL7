from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import model_keyphrases.utils as utils

from config.env import read_config_model

# Khởi tạo model.
global model

model_variables = read_config_model()
print(model_variables)
if model_variables['MODEL_LOAD'] == 'True':
    model = utils._load_model(verbose = True)
else:
    model = None

# Define the data model using Pydantic
class PredictRequest(BaseModel):
    text: str

class PredictResponse(BaseModel):
    tokens: str
    tags: str
    
router = APIRouter(prefix="/keyphrases")

@router.post("/predict", response_model=PredictResponse)
async def predict(request: PredictRequest):
    try:
        # Lấy văn bản từ dữ liệu
        text = request.text

        # Xử lý văn bản (ở đây chỉ là ví dụ đơn giản, bạn có thể thay đổi thành xử lý khác tùy nhu cầu)
        # Ví dụ: Tách văn bản thành danh sách các từ
        tokens, tags = utils._predict(model=model, sentence=text)

        # Trả về kết quả dưới dạng JSON
        return PredictResponse(tokens=tokens, tags=tags)
    
    except Exception as e:
        # Xử lý lỗi
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get('/save-model')
async def save_model():
    try:
        global model
        model = utils._save_model(verbose=True)
        
        details = { "detail" : "Model saved successfully"}
        return details
    except Exception as e:
        # Xử lý lỗi
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get('/load-model')
async def load_model():
    try:
        global model
        model = utils._load_model(verbose=True)
        
        details = { "detail" : "Model loaded successfully"}
        return details
    except Exception as e:
        # Xử lý lỗi
        raise HTTPException(status_code=500, detail=str(e))
    
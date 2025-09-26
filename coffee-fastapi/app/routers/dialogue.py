from fastapi import APIRouter, Depends, HTTPException, status, Body
from starlette.responses import StreamingResponse
from ..dependencies import get_current_dialogue_user, get_db
from ..llm_multimcp import mcp_client
from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, Union, Annotated
from datetime import datetime
from bson import ObjectId
import json
import asyncio
from pydantic_core import core_schema

router = APIRouter(
    prefix="/dialogue",
    tags=["dialogue"],
    responses={404: {"description" : "Not found"}},
)

class PyObjectId(str):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: Any
    ) -> Dict[str, Any]:
        # 定义验证逻辑：先按任意类型接收，再用我们的 validate 转换
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.union_schema([  # 接受 ObjectId 或 str
                core_schema.is_instance_schema(ObjectId),
                core_schema.str_schema(),
            ])
        )

    @classmethod
    def validate(cls, v: Any) -> str:
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, str) and ObjectId.is_valid(v):
            return str(ObjectId(v))
        raise ValueError("Invalid ObjectId")



class ChatRequest(BaseModel):
    dialogue_id : Optional[str] = None
    history : list[dict]
    query : str

class Dialogue(BaseModel):
    id : PyObjectId = Field(..., alias = "_id")
    title : str
    history : list[dict] = Field(default_factory=list)
    created_at : datetime
    updated_at : datetime
    class Config:
        populate_by_name=True

async def get_dialogue(db, email, dialogue_id: str = None):
        """获取或创建对话"""
        if dialogue_id:
            # 验证是否为有效的 ObjectId
            try:
                obj_id = ObjectId(dialogue_id)
                dialogue = await db.dialogue.find_one({"_id": obj_id})
                dialogue["_id"] = str(dialogue["_id"])
                if dialogue:
                    return Dialogue(**dialogue).model_dump(by_alias=False)
                else:
                    raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=" using a wrong dialogue_id or token"
                )
            except:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="dialogue_id is wrong"
                )
                
        

@router.post('/get_new_dialogue',tags=["dialogue"])
async def get_new_dialogue(user = Depends(get_current_dialogue_user), db=Depends(get_db)):
    
    dialogue = {
        "email" : user.email,
        "title" : "新建会话", 
        "history": [
            {"role": "system", "content": "你是一个智能助手"}
        ],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    result = await db.dialogue.insert_one(dialogue)
    
    dialogue["_id"] = str(result.inserted_id)
    
    #return Dialogue(**dialogue)
    return Dialogue(**dialogue).model_dump(by_alias=False)
        

async def update_dialogue(db, dialogue_id : str, new_messages : list):
    await db.dialogue.update_one(
        {"_id" : ObjectId(dialogue_id)},
        {
            "$push": {"history" : {"$each" : new_messages}},
            "$set" : {"updated_at": datetime.utcnow()}
        }
    )

@router.post("/chat", tags=["dialogue"])
async def chat(chatRequest : ChatRequest, user=Depends(get_current_dialogue_user), db=Depends(get_db)):
    async def generate_response():
        try:
            #生成开头的信息
            dialogue = await get_dialogue(db, user.email, chatRequest.dialogue_id)
            #print(f"dialogue:{dialogue}")
            #print(f"dialogue id:{dialogue.id}")
            messages=dialogue["history"]
            messages.append({"role":"user", "content" : chatRequest.query})
            response_data = {
                "dialogue_id": dialogue["id"],
                "type" : "start",
                "timestamp" : datetime.utcnow().isoformat()
            }
            yield f"data: {json.dumps(response_data, ensure_ascii=False)}\n\n"

            #生成llm返回的信息
            full_response = ""
            async for content in mcp_client.get_response(messages):
                if content:
                    full_response += content
                    chunk_data = {
                        "type" : "chunk",
                        "content" : content
                    }
                    yield f"data: {json.dumps(chunk_data, ensure_ascii=False)}\n\n"
            
            #生成结束的信息
            final_data = {
                "type" : "end",
                "final_response" : full_response,
            }
            yield f"data: {json.dumps(final_data, ensure_ascii=False)}\n\n"

            #更新数据库
            new_messages = [
                {
                    "role":"user", "content": chatRequest.query
                },
                {
                    "role":"assistant", "content" : full_response
                }
            ]
            await update_dialogue(db, dialogue["id"], new_messages)

        #生成错误信息
        except Exception as e:
            error_data = {
                "type" : "error",
                "message" : str(e)
            }
            yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        generate_response(),
        media_type="text/evnet-stream",
        headers={
            "Cache-Control" : "no-cache",
            "Connection" : "keep-alive",
            "Access-Control-Allow-Origin" : "*"
        }
    )
            


@router.post("/get_ids_titles", tags=["dialogue"])
async def get_ids_titles(user = Depends(get_current_dialogue_user) , db = Depends(get_db)):
    cursor = db.dialogue.find({"email" : user.email}, {"_id" : 1, "title" : 1, "created_at":1, "updated_at" :1})
    dialogue_ids_titles_db = await cursor.to_list()
    
    dialogue_ids_titles = [Dialogue(**dialogue_id_title) for dialogue_id_title in dialogue_ids_titles_db]
    print(f"/get_ids_titles : {dialogue_ids_titles}")
    
    #return dialogue_ids_titles
    return [d.model_dump(by_alias=False) for d in dialogue_ids_titles]

@router.post("/get_history_by_id", tags=["dialogue"])
async def get_history_by_id(dialogue_id : Annotated[dict, Body()], user = Depends(get_current_dialogue_user), db=Depends(get_db)):
    cursor = db.dialogue.find({"_id" : ObjectId(dialogue_id["dialogue_id"]), "email": user.email}, {"_id":1, "title":1, "history" :1, "created_at":1, "updated_at":1})
    dialogue = await cursor.to_list()
    dialogue = dialogue[0]
    print(f"get_history_by_id:{dialogue}")
    return Dialogue(**dialogue).model_dump(by_alias=False)


# @router.get("/dialogue/history", tags=["dialogue"])
# async def get_dialogue_history_by_id(user=Depends(get_current_user), db=Depends(get_db)):
#     #get all dialogues of the current user
    
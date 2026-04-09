import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx
import json
import google.auth
import google.auth.transport.requests

app = FastAPI()

# --- [1. 구글 클라우드 인증 설정] ---
try:
    # 시스템에 설정된 ADC(Application Default Credentials)를 자동으로 가져옵니다.
    credentials, project_id = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
    
    # 만약 환경변수에서 ID를 못 가져올 경우를 대비해 유저님의 ID를 고정합니다.
    if not project_id or project_id == "default-project":
        project_id = "project-49f5e2c8-808d-42c8-b09"
        
    print(f"🟢 [시스템] 구글 클라우드 프로젝트 인식 완료: {project_id}")
except Exception as e:
    print(f"🔴 [시스템 오류] 인증 정보를 찾을 수 없습니다: {e}")
    project_id = "project-49f5e2c8-808d-42c8-b09"

def get_access_token():
    """구글 API 호출을 위한 임시 액세스 토큰 생성"""
    auth_req = google.auth.transport.requests.Request()
    credentials.refresh(auth_req)
    return credentials.token

# --- [2. 모드 연동용 엔드포인트] ---

@app.get("/api/tags")
@app.get("/tags")
async def tags():
    """배너로드 모드가 모델 목록을 요청할 때 응답"""
    print("🟢 [연결 확인] 모드에서 모델 리스트를 요청했습니다.")
    return {"models": [{"name": "gemini-3-flash-preview"}]}

@app.post("/api/chat")
@app.post("/api/generate")
async def generate(request: Request):
    """실제 LLM 질문 및 답변 처리"""
    try:
        data = await request.json()
        
        # 모델명은 Gemini 3 Flash Preview로 고정 (또는 모드 설정값 사용)
        model_name = "gemini-3-flash-preview"
        print(f"\n🟡 [질문 접수] 모델: {model_name}")
        
        # 1. 메시지 포맷 변환 (Ollama -> Gemini)
        messages = data.get("messages", [{"role": "user", "content": data.get("prompt", "안녕?")}])
        gemini_contents = []
        system_instruction = None
        
        for msg in messages:
            if msg["role"] == "system":
                system_instruction = {"parts": [{"text": msg["content"]}]}
                continue
            
            role = "user" if msg["role"] == "user" else "model"
            
            # 연속된 동일 역할 메시지 병합 (구글 API 규격 준수)~
            if gemini_contents and gemini_contents[-1]["role"] == role:
                gemini_contents[-1]["parts"][0]["text"] += "\n" + msg["content"]
            else:
                gemini_contents.append({
                    "role": role,
                    "parts": [{"text": msg["content"]}]
                })
        
        # 2. 요청 페이로드 구성 (Thinking 기능 포함)
        payload = {
                    "contents": gemini_contents,
                    "systemInstruction": system_instruction, 
                    "generationConfig": {
                        "temperature": 0.8,           
                        "maxOutputTokens": 2000,      
                        "topP": 0.8,
                        "topK": 40                 
                    },
                    "safetySettings": [
                        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
                    ]
        }
        if system_instruction:
            payload["systemInstruction"] = system_instruction
            
        # 3. 액세스 토큰 갱신 및 URL 설정
        token = get_access_token()
        # 글로벌 위치와 v1beta1 프리뷰 채널 사용
        url = f"https://aiplatform.googleapis.com/v1beta1/projects/{project_id}/locations/global/publishers/google/models/{model_name}:generateContent"
        
        # 4. 구글 서버에 요청 전송
        async with httpx.AsyncClient() as client:
            res = await client.post(
                url, 
                json=payload, 
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                },
                timeout=180.0 # Thinking 시간이 걸릴 수 있으므로 타임아웃을 늘림
            )
            
        res_json = res.json()
        
        # 에러 처리
        if "error" in res_json:
            print(f"🔴 [구글 서버 에러] {json.dumps(res_json, ensure_ascii=False)}")
            return JSONResponse({"error": res_json["error"].get("message", "API Error")}, status_code=500)
            
        # 5. 답변 추출 (Text와 Thought 구분 없이 답변 부분만 추출)
        candidates = res_json.get("candidates", [])
        if not candidates:
            print(f"🔴 [응답 없음] 필터링되었거나 결과가 없습니다.")
            return JSONResponse({"error": "No candidates found"}, status_code=500)
            
        parts = candidates[0]["content"]["parts"]
        # 'thought' 파트는 제외하고 실제 'text' 파트만 합쳐서 모드에 전달
        final_text = "".join([part["text"] for part in parts if "text" in part])
        
        print(f"🟢 [성공] 답변 완료: {final_text[:40]}...")

        usage = res_json.get("usageMetadata") # res_json에서 토큰 정보를 가져옵니다.
        if usage:
            prompt_tokens = usage.get("promptTokenCount", 0)
            candidates_tokens = usage.get("candidatesTokenCount", 0)
            total_tokens = usage.get("totalTokenCount", 0)
            print(f"--- Usage: In {prompt_tokens} / Out {candidates_tokens} / Total {total_tokens} ---")
        return JSONResponse({
            "model": model_name,
            "message": {"role": "assistant", "content": final_text},
            "response": final_text,
            "done": True
        })

    except Exception as e:
        print(f"🔴 [브릿지 내부 에러] {str(e)}")
        return JSONResponse({"error": str(e)}, status_code=500)

if __name__ == "__main__":
    # 포트는 배너로드 모드 설정에 맞춰 11434 사용
    print("🚀 배너로드용 Gemini 3 브릿지 서버 시작 중...")
    uvicorn.run(app, host="127.0.0.1", port=11434)
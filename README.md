# Bannerlord Gemini Bridge

게임 배너로드 LLM 모드(ai influence)가 지원하는 방식중 Ollama API를 클라우드(Vertex AI)로 중계해 주는 가벼운 브릿지 서버입니다.

## 왜 만들었나요?

* **쾌적한 게임 환경**: 로컬에서 LLM 돌릴 자원 아껴서 1프레임이라도 더 뽑고 싶었습니다.
* **똑똑한 NPC**: Gemini 3 Flash의 추론(Thinking) 기능을 써보고 싶었습니다. 
* **귀찮음 해소**: 모드 소스코드 건드리는 수고로움을 피하고자 그냥 "Ollama인 척" 하는 서버를 띄웠습니다.

## 기술적 선택: 왜 Vertex AI인가?

사실 AI Studio가 훨씬 쉽지만, 굳이 GCP(Vertex AI)를 거쳐서 사용했습니다 (+ 300$의 무료지원금)
* **끊김 없는 대화**: 무료 API의 빡빡한 호출 제한(Rate Limit)에서 벗어나 NPC와 길게 대화하고 싶었습니다.
* **진짜 클라우드 맛보기**: 단순 API 키 복붙 말고, 실제 서비스 환경에서 쓰는 인증(ADC) 방식을 제대로 한 번 경험해 보고 싶었습니다.
* **디버깅의 편리함**: GCP 콘솔에서 로그를 보며 문제 원인을 파악하는 게 훨씬 편하니까요.

## 접근 방식 (Vibe Coding)

* **설계 방식**: 복잡한 설계도 좋지만, 일단 돌아가는 코드를 가장 빠르게 만드는 데 집중했습니다.

## 주요 기능

* **Ollama 인터페이스 구현**: 모드가 던지는 요청을 버텍스 API 서버를 거쳐 Gemini에게 전달합니다.
* **에러 방지 병합**: 연속된 유저 메시지를 하나로 합쳐 구글 API 에러를 원천 차단했습니다.

## 시작하기

1. **준비**: `gcloud auth application-default login` 명령어로 구글 인증을 진행합니다.
2. **설정**: `bridge.py` 파일 상단에 본인의 `project_id`를 입력합니다.
3. **실행**: `python bridge.py`를 실행합니다. (11434 포트에서 대기합니다.)
4. **게임 설정**: 모드 설정 메뉴에서 Provider를 **Ollama**로, URL을 `http://127.0.0.1:11434`로 지정합니다.

## 향후 계획 (Next Step)

* [ ] 하드코딩된 설정값들 .env로 분리
* [ ] 메시지 변환 로직 함수화 (Refactoring)
* [ ] 모델/리전 변경이 자유로운 동적 URL 빌더 적용

<img width="1103" height="616" alt="image" src="https://github.com/user-attachments/assets/174c3957-4587-4340-b548-0caeeb4b6fc2" />
<img width="1096" height="609" alt="image" src="https://github.com/user-attachments/assets/a165c356-2f12-4bb6-9132-d06b77cb8e4e" />

# Bannerlord Gemini Bridge

**"로컬 자원은 게임에, NPC 지능은 클라우드에."** 배너로드 LLM 모드를 위해 제작된 Vertex AI 기반 Ollama 에뮬레이터입니다.

## 왜 만들었나요?

* **성능 올인**: 로컬에서 LLM 돌릴 자원(VRAM/CPU)을 아껴서 게임 프레임에 보탰습니다.
* **지능 업그레이드**: Gemini 3 Flash의 압도적인 한국어 성능과 추론(Thinking) 능력을 활용합니다.
* **심리스 연동**: 모드 수정 없이 "Ollama인 척" 하여 URL 설정만으로 즉시 작동합니다.

## 접근 방식

* **실용주의**: 복잡한 설계보다 AI와 협업하여 가장 빠르게 돌아가는 코드를 짰습니다.
* **주니어의 시각**: GCP 인증(ADC)과 인프라를 직접 다루며 실무적인 연동 체계를 경험했습니다.
* **데이터 가시성**: 터미널 로그만 봐도 토큰 사용량과 상태를 한눈에 알 수 있게 설계했습니다.

## 주요 기능

* **API 호환**: Ollama의 /api/chat, /api/tags 엔드포인트 완벽 대응
* **메시지 최적화**: 구글 API 규격에 맞는 자동 메시지 병합 및 전처리
* **몰입형 설정**: 게임 몰입을 위해 세이프티 필터 최소화 (BLOCK_NONE)

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

import ollama
# import google.generativeai as genai  # [Future] 구글 Gemini API 사용 시 주석 해제

class Brain:
    def __init__(self, model_name="gemma2", mode="local"):
        """
        초기화 설정
        :param model_name: 사용할 모델 이름 (gemma2, llama3 등)
        :param mode: 'local' (Ollama) 또는 'api' (Cloud API)
        """
        self.mode = mode
        self.model_name = model_name
        self.chat_history = []
        
        # 시스템 프롬프트 (뇌의 성격 및 행동 지침)
        self.system_prompt = """
        너는 AI 비서 '자비스'야. 사용자 D를 위해 비서 업무를 수행해.
        
        [행동 규칙] - 답변 끝에 반드시 태그를 붙여서 행동해.
        1. 유튜브 재생: "노래 틀어줘/재생해" -> `[[PLAY:검색어]]`
        2. 유튜브 검색: "찾아봐/검색해" -> `[[YOUTUBE:검색어]]`
        3. 날씨/정보: "오늘 날씨/정보 알려줘" -> `[[NAVER:검색어]]` 또는 `[[GOOGLE:검색어]]`
           (주의: 너는 실시간 인터넷 접속이 안 되므로, "브라우저를 띄워드릴게요"라고 답할 것)
        4. 앱 제어: "계산기/메모장 켜" -> `[[APP:calc]]` / `[[APP:notepad]]`
        5. 끄기/닫기: "브라우저/계산기 꺼" -> `[[CLOSE:browser]]` / `[[CLOSE:calc]]`
        
        [대화 스타일]
        - 답변은 친절하고 자연스러운 한국어 구어체로 짧게(1~2문장).
        """
        
        # 기억 초기화
        self._reset_memory()

    def _reset_memory(self):
        """기억을 지우고 시스템 프롬프트를 다시 심습니다."""
        self.chat_history = [{'role': 'system', 'content': self.system_prompt}]

    def think(self, user_input):
        """
        외부에서 호출하는 메인 함수.
        설정된 모드(Local/API)에 따라 적절한 뇌를 사용합니다.
        """
        print(f"[🧠 생각 중...] (모드: {self.mode})")
        
        if self.mode == "local":
            return self._think_local(user_input)
        elif self.mode == "api":
            return self._think_api(user_input)
        else:
            return "오류: 알 수 없는 뇌 모드입니다."

    def _think_local(self, user_input):
        """1. 로컬 뇌 (Ollama) 사용 로직"""
        # 사용자 입력 기억
        self.chat_history.append({'role': 'user', 'content': user_input})
        
        # 기억 용량 관리 (너무 길어지면 시스템 프롬프트(0번) 제외하고 오래된 기억 삭제)
        if len(self.chat_history) > 15:
            del self.chat_history[1:3]

        try:
            response = ollama.chat(model=self.model_name, messages=self.chat_history)
            ai_text = response['message']['content']
            
            # AI 답변 기억
            self.chat_history.append({'role': 'assistant', 'content': ai_text})
            return ai_text
        except Exception as e:
            return f"로컬 뇌 오류가 발생했습니다: {str(e)}"

    def _think_api(self, user_input):
        """
        2. [Future] 클라우드 API 뇌 (Gemini/GPT) 사용 로직
        나중에 API 키를 발급받으면 이 부분을 채워넣으면 됩니다.
        """
        # 예시 코드 (나중에 활성화):
        # model = genai.GenerativeModel('gemini-pro')
        # response = model.generate_content(user_input)
        # return response.text
        
        return "아직 API 모드가 연결되지 않았습니다. 코드를 설정해주세요."

    def clear_memory_cache(self):
        """종료 시 VRAM 정리"""
        if self.mode == "local":
            try:
                ollama.generate(model=self.model_name, prompt="", keep_alive=0)
                print("[System] 로컬 모델 메모리 해제 완료")
            except:
                pass
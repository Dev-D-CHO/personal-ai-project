from jarvis_senses import Ears, Mouth
from jarvis_brain import Brain
from jarvis_actions import Hands

def main():
    # 1. 부품 조립 (초기화)
    print("[System] 자비스 모듈 로딩 중...")
    ear = Ears()
    mouth = Mouth()
    brain = Brain(model_name="gemma2") # 사용하시는 모델명
    hand = Hands()

    mouth.speak("자비스 시스템, 모든 모듈이 정상 작동 중입니다.")

    while True:
        # 2. 듣기
        user_text = ear.listen()
        if not user_text:
            continue

        # 3. 종료 확인
        if "종료" in user_text or "꺼져" in user_text:
            mouth.speak("시스템을 종료합니다. D님, 좋은 하루 되세요.")
            brain.clear_memory_cache() # 메모리 청소
            break
        
        # 4. 생각하기 (LLM)
        ai_reply = brain.think(user_text)
        
        # 5. 행동하기 (Action) - 태그가 있으면 실행
        hand.execute(ai_reply)
        
        # 6. 말하기 (TTS)
        mouth.speak(ai_reply)

if __name__ == "__main__":
    main()
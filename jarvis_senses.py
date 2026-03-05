import speech_recognition as sr
import re
import whisper
import os
import torch
import asyncio
import edge_tts
import pygame
import pyaudio
import audioop

# [안전장치] FFmpeg 경로 추가
os.environ["PATH"] += os.pathsep + os.getcwd()

class Ears:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = 1.2
        self.recognizer.energy_threshold = 400  # [수정] 감도를 300 -> 400으로 높여서 작은 잡음 무시
        
        self.wake_words = ["자비스", "야", "저기", "헤이"]
        
        print("\n[System] Whisper(로컬 귀) 로딩 준비 중...")
        if torch.cuda.is_available():
            device = "cuda"
            print(f"✅ 그래픽카드 감지 성공: {torch.cuda.get_device_name(0)}")
        else:
            device = "cpu"
            print("⚠️ 그래픽카드를 찾지 못했습니다. CPU로 동작합니다.")

        try:
            self.model = whisper.load_model("base", device=device)
            print(f"[System] Whisper 로딩 완료! (모드: {device})")
        except Exception as e:
            print(f"\n🛑 Whisper 모델 로딩 실패: {e}")

        # 초기 소음 측정
        try:
            with sr.Microphone() as source:
                print("[System] 주변 소음 측정 중... (1초만 조용히 해주세요)")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print(f"[System] 소음 측정 완료 (감도: {self.recognizer.energy_threshold})")
        except:
            pass

    def listen(self):
        """명령을 듣는 메인 함수 (활성 상태)"""
        with sr.Microphone() as source:
            print("\n[👂 듣는 중...] (명령을 말씀하세요)")
            try:
                # 5초 대기, 말 시작하면 최대 10초까지 듣기
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                print("[..] 인식 변환 중...")
                return self._transcribe(audio, verbose=True)
            except:
                return None

    def wait_for_wake_word(self):
        """[NEW] 이름을 부를 때까지 조용히 대기하는 함수"""
        print(f"\n[💤 대기 모드] '{self.wake_words[0]}'라고 부르기 전까지는 듣지 않습니다...")
        
        with sr.Microphone() as source:
            while True:
                try:
                    # [수정] 대기 시간을 1초 -> 2초로 늘려 너무 짧은 단어 무시
                    # phrase_time_limit도 3초 -> 4초로 늘려 '자비스'를 여유롭게 듣게 함
                    audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=4)
                    
                    # 로그 없이 내부적으로만 확인
                    text = self._transcribe(audio, verbose=False)
                    
                    if text:
                        for wake in self.wake_words:
                            # 호출어가 포함되어 있고, 문장이 너무 길지 않을 때만 반응 (오인식 방지)
                            if wake in text:
                                print(f"⚡ 호출 확인: '{text}'")
                                return True 
                except sr.WaitTimeoutError:
                    continue 
                except Exception:
                    continue

    def _transcribe(self, audio, verbose=True):
        """오디오 -> 텍스트 변환 내부 함수"""
        try:
            with open("temp_voice.wav", "wb") as f:
                f.write(audio.get_wav_data())
            
            # [핵심] 힌트를 대폭 강화하여 '계산기', '메모장' 인식률 상승
            prompt_text = "자비스, 종료, 날씨, 유튜브, 재생, 틀어줘, 꺼져, 안녕, 계산기, 메모장, 켜줘, 꺼줘"
            
            result = self.model.transcribe(
                "temp_voice.wav", 
                fp16=False, 
                language="ko", 
                initial_prompt=prompt_text
            )
            text = result['text'].strip()
            
            # [후처리] 자주 틀리는 단어 강제 교정
            if "Staging" in text or "스테이징" in text:
                text = text.replace("Staging", "종료").replace("스테이징", "종료")
            
            # '계단기' -> '계산기' 교정
            if "계단" in text:
                text = text.replace("계단", "계산")
            
            if os.path.exists("temp_voice.wav"):
                os.remove("temp_voice.wav")
                
            if text:
                if verbose:
                    print(f"[👤 D님]: {text}")
                return text
        except Exception:
            pass
        return None

class Mouth:
    def __init__(self):
        self.voice = "ko-KR-InJoonNeural" 
        self.output_file = "tts_output.mp3"
        
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.interrupt_threshold = 2000 

    async def _generate_audio(self, text):
        communicate = edge_tts.Communicate(text, self.voice, rate="+20%")
        await communicate.save(self.output_file)

    def speak(self, text):
        clean_text = re.sub(r'\[\[.*?\]\]', '', text)
        clean_text = re.sub(r'[*#]', '', clean_text)
        
        if not clean_text.strip(): return

        print(f"\n[🔊 자비스]: {clean_text}")
        
        try:
            asyncio.run(self._generate_audio(clean_text))
            
            pygame.mixer.init()
            pygame.mixer.music.load(self.output_file)
            pygame.mixer.music.play()
            
            p = pyaudio.PyAudio()
            stream = p.open(format=self.format, channels=self.channels, 
                          rate=self.rate, input=True, frames_per_buffer=self.chunk)
            
            interrupted = False
            
            while pygame.mixer.music.get_busy():
                data = stream.read(self.chunk, exception_on_overflow=False)
                rms = audioop.rms(data, 2)
                
                if rms > self.interrupt_threshold:
                    print("\n[✋ 감지] 사용자의 개입으로 말하기를 중단합니다.")
                    pygame.mixer.music.stop()
                    interrupted = True
                    break
                    
                pygame.time.Clock().tick(10)
            
            stream.stop_stream()
            stream.close()
            p.terminate()
            pygame.mixer.quit()
            
            if os.path.exists(self.output_file):
                os.remove(self.output_file)
                
            return interrupted

        except Exception as e:
            print(f"⚠️ TTS 오류: {e}")
            return False
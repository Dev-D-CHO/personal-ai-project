import os
import webbrowser
import re
import subprocess  # [NEW] os.system 대신 사용하는 멈춤 방지 도구

# 유튜브 자동 재생 라이브러리 체크
try:
    import pywhatkit
    HAS_PYWHATKIT = True
except ImportError:
    HAS_PYWHATKIT = False

class Hands:
    def execute(self, response_text):
        """AI 답변에 포함된 태그([[COMMAND]])를 실행"""
        
        # 1. 유튜브 바로 재생 ([[PLAY:제목]])
        play_match = re.search(r'\[\[PLAY:(.*?)\]\]', response_text)
        if play_match:
            query = play_match.group(1)
            print(f"🚀 [Action] 유튜브 영상 재생: {query}")
            if HAS_PYWHATKIT:
                pywhatkit.playonyt(query)
            else:
                webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
            return

        # 2. 유튜브 검색 결과창 ([[YOUTUBE:검색어]])
        yt_match = re.search(r'\[\[YOUTUBE:(.*?)\]\]', response_text)
        if yt_match:
            query = yt_match.group(1)
            print(f"🚀 [Action] 유튜브 검색: {query}")
            webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
            return

        # 3. 구글 검색 ([[GOOGLE:검색어]])
        google_match = re.search(r'\[\[GOOGLE:(.*?)\]\]', response_text)
        if google_match:
            query = google_match.group(1)
            print(f"🚀 [Action] 구글 검색: {query}")
            webbrowser.open(f"https://www.google.com/search?q={query}")
            return

        # 4. 네이버 검색 ([[NAVER:검색어]])
        naver_match = re.search(r'\[\[NAVER:(.*?)\]\]', response_text)
        if naver_match:
            query = naver_match.group(1)
            print(f"🚀 [Action] 네이버 검색: {query}")
            webbrowser.open(f"https://search.naver.com/search.naver?query={query}")
            return

        # 5. 앱 실행 ([[APP:이름]])
        app_match = re.search(r'\[\[APP:(.*?)\]\]', response_text)
        if app_match:
            app = app_match.group(1)
            print(f"🚀 [Action] 앱 실행: {app}")
            
            # [핵심 수정] Popen을 써야 자비스가 멈추지 않고 앱을 띄운 뒤 바로 다음 대기 상태로 돌아옵니다.
            try:
                if app == "calc":
                    subprocess.Popen("calc.exe", shell=True)
                elif app == "notepad":
                    subprocess.Popen("notepad.exe", shell=True)
            except Exception as e:
                print(f"⚠️ 앱 실행 실패: {e}")
            return

        # 6. 프로그램 종료 ([[CLOSE:타겟]])
        close_match = re.search(r'\[\[CLOSE:(.*?)\]\]', response_text)
        if close_match:
            target = close_match.group(1)
            print(f"🚀 [Action] 강제 종료: {target}")
            try:
                if target == "browser":
                    os.system("taskkill /f /im chrome.exe")
                    os.system("taskkill /f /im msedge.exe")
                    os.system("taskkill /f /im whale.exe")
                elif target == "calc":
                    os.system("taskkill /f /im CalculatorApp.exe") # 윈도우 10/11 앱
                    os.system("taskkill /f /im calc.exe")          # 클래식
                elif target == "notepad":
                    os.system("taskkill /f /im notepad.exe")
            except Exception as e:
                print(f"⚠️ 종료 실패: {e}")
            return
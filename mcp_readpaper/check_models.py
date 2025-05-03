# 스크립트 내에서 사용 가능한 모델 확인
import google.generativeai as genai
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# API 키 설정
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY가 설정되지 않았습니다.")

genai.configure(api_key=api_key)

print("\n=== 현재 API 키로 접근 가능한 모델 목록 ===")
for m in genai.list_models():
    # 'generateContent'를 지원하는 모델만 필터링 (일반적인 텍스트 생성 모델)
    if 'generateContent' in m.supported_generation_methods:
        print(f"\n모델명: {m.name}")
        print(f"디스플레이명: {m.display_name}")
        print(f"설명: {m.description}")
        print(f"지원하는 생성 메소드: {m.supported_generation_methods}")
        print("-" * 50)
print("\n=========================================") 
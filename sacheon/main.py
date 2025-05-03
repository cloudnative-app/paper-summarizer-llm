import os
import pandas as pd
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
from dotenv import load_dotenv
import traceback
import time

# 환경 변수 로드
load_dotenv()

# Azure 서비스 설정
endpoint = os.getenv("AZURE_ENDPOINT")
key = os.getenv("AZURE_KEY")

# Text Analytics 클라이언트 생성
credential = AzureKeyCredential(key)
text_analytics_client = TextAnalyticsClient(endpoint=endpoint, credential=credential)

def analyze_sentiment(text):
    """텍스트의 감정을 분석하는 함수"""
    try:
        result = text_analytics_client.analyze_sentiment([text])[0]
        return {
            "sentiment": result.sentiment,
            "confidence_scores": {
                "positive": result.confidence_scores.positive,
                "neutral": result.confidence_scores.neutral,
                "negative": result.confidence_scores.negative
            }
        }
    except Exception as e:
        print(f"감정 분석 중 오류 발생: {str(e)}")
        return None

def analyze_all_rows(file_path):
    """전체 파일을 분석하는 함수"""
    try:
        # 파일 확장자 확인
        file_extension = os.path.splitext(file_path)[1].lower()
        
        # 파일 읽기
        print(f"\n파일 읽기 중: {file_path}")
        if file_extension == '.csv':
            df = pd.read_csv(file_path, encoding='utf-8')
        elif file_extension in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path, engine='openpyxl')
        else:
            raise ValueError(f"지원하지 않는 파일 형식입니다: {file_extension}")
        
        total_rows = len(df)
        print(f"총 {total_rows}개의 행을 분석합니다.")
        
        # 분석 결과를 저장할 리스트
        results = []
        
        # 각 텍스트에 대해 감정 분석 수행
        print("\n감정 분석 시작...")
        start_time = time.time()
        
        for i, text in enumerate(df['본문']):
            if (i + 1) % 10 == 0:  # 10개마다 진행 상황 출력
                elapsed_time = time.time() - start_time
                rows_per_second = (i + 1) / elapsed_time
                remaining_time = (total_rows - (i + 1)) / rows_per_second
                print(f"\r진행 중: {i+1}/{total_rows} (완료: {((i+1)/total_rows*100):.1f}%, 예상 남은 시간: {remaining_time/60:.1f}분)", end="")
            
            analysis = analyze_sentiment(text)
            results.append(analysis)
        
        # 결과를 데이터프레임에 추가
        df['sentiment_analysis'] = results
        
        # 감정 점수를 개별 컬럼으로 분리
        df['sentiment'] = df['sentiment_analysis'].apply(lambda x: x['sentiment'] if x else None)
        df['positive_score'] = df['sentiment_analysis'].apply(lambda x: x['confidence_scores']['positive'] if x else None)
        df['neutral_score'] = df['sentiment_analysis'].apply(lambda x: x['confidence_scores']['neutral'] if x else None)
        df['negative_score'] = df['sentiment_analysis'].apply(lambda x: x['confidence_scores']['negative'] if x else None)
        
        # 원본 sentiment_analysis 컬럼 제거
        df = df.drop('sentiment_analysis', axis=1)
        
        # 결과 저장
        output_file = 'analyzed_' + os.path.basename(file_path)
        if file_extension == '.csv':
            df.to_csv(output_file, index=False, encoding='utf-8-sig')
        else:
            df.to_excel(output_file, index=False, engine='openpyxl')
        
        # 통계 정보 출력
        print("\n\n=== 분석 완료 ===")
        print(f"총 분석 시간: {(time.time() - start_time)/60:.1f}분")
        print(f"분석 결과가 {output_file}에 저장되었습니다.")
        
        sentiments = [r['sentiment'] for r in results if r]
        print("\n=== 전체 분석 통계 ===")
        print(f"총 분석 수: {len(sentiments)}")
        print(f"긍정: {sentiments.count('positive')} ({(sentiments.count('positive')/len(sentiments)*100):.1f}%)")
        print(f"중립: {sentiments.count('neutral')} ({(sentiments.count('neutral')/len(sentiments)*100):.1f}%)")
        print(f"부정: {sentiments.count('negative')} ({(sentiments.count('negative')/len(sentiments)*100):.1f}%)")
        
        # 발신자2별 통계
        print("\n=== 발신자2별 분석 통계 ===")
        df['sentiment'] = sentiments
        sender_stats = df.groupby('발신자2').agg({
            'sentiment': 'count',
            'positive_score': lambda x: (x > 0.5).sum(),
            'neutral_score': lambda x: (x > 0.5).sum(),
            'negative_score': lambda x: (x > 0.5).sum()
        }).rename(columns={
            'sentiment': '총 건수',
            'positive_score': '긍정 건수',
            'neutral_score': '중립 건수',
            'negative_score': '부정 건수'
        })
        
        # 비율 계산
        sender_stats['긍정 비율'] = (sender_stats['긍정 건수'] / sender_stats['총 건수'] * 100).round(1)
        sender_stats['중립 비율'] = (sender_stats['중립 건수'] / sender_stats['총 건수'] * 100).round(1)
        sender_stats['부정 비율'] = (sender_stats['부정 건수'] / sender_stats['총 건수'] * 100).round(1)
        
        # 결과 출력
        pd.set_option('display.max_rows', None)
        pd.set_option('display.width', None)
        print("\n발신자2별 상세 통계:")
        print(sender_stats)
        
    except Exception as e:
        print("\n=== 오류 정보 ===")
        print(f"오류 타입: {type(e).__name__}")
        print(f"오류 메시지: {str(e)}")
        print("\n=== 상세 오류 정보 ===")
        print(traceback.format_exc())

if __name__ == "__main__":
    # 파일 경로 설정
    input_file = "input/analysis_azure.csv"  # 또는 .xlsx 파일
    
    if os.path.exists(input_file):
        print(f"파일을 찾았습니다: {input_file}")
        analyze_all_rows(input_file)
    else:
        print(f"파일을 찾을 수 없습니다: {input_file}")
        print(f"현재 작업 디렉토리: {os.getcwd()}")
        print("디렉토리 내용:")
        print(os.listdir('.')) 
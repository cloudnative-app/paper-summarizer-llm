import os
import json
from datetime import datetime
from paper_analyzer import PaperAnalyzer
from paper_reader import PaperReader

def main():
    try:
        # 결과 디렉토리 생성
        result_dir = "result"
        if not os.path.exists(result_dir):
            os.makedirs(result_dir)
        
        # 파일 읽기
        reader = PaperReader()
        papers = reader.read_papers("papers")
        
        if not papers:
            print("분석할 논문이 없습니다.")
            return
        
        # 논문 분석
        analyzer = PaperAnalyzer()
        results = []
        
        for paper in papers:
            try:
                # 각 논문 분석
                analysis = analyzer.analyze_paper(paper)
                if analysis:
                    results.append(analysis)
            except Exception as e:
                print(f"논문 분석 중 오류 발생: {str(e)}")
                continue
        
        if not results:
            print("분석된 결과가 없습니다.")
            return
        
        # 결과 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(result_dir, f"논문분석_결과_{timestamp}.csv")
        
        # CSV 파일로 저장
        analyzer.save_to_csv(results, filename)
        
        # JSON 파일로도 백업 저장
        json_filename = os.path.join(result_dir, f"논문분석_결과_{timestamp}.json")
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"분석이 완료되었습니다. 결과는 {result_dir} 디렉토리에 저장되었습니다.")
        
    except Exception as e:
        print(f"프로그램 실행 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    main() 
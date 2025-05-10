import os
import json

class PaperReader:
    def read_papers(self, directory):
        """지정된 디렉토리에서 논문 파일들을 읽어옵니다."""
        papers = []
        
        try:
            # 디렉토리가 존재하는지 확인
            if not os.path.exists(directory):
                print(f"디렉토리를 찾을 수 없습니다: {directory}")
                return papers
            
            # 디렉토리 내의 모든 파일 검색
            for filename in os.listdir(directory):
                if filename.endswith('.json'):
                    file_path = os.path.join(directory, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            paper_data = json.load(f)
                            papers.append(paper_data)
                    except Exception as e:
                        print(f"파일 읽기 오류 ({filename}): {str(e)}")
                        continue
            
            print(f"총 {len(papers)}개의 논문을 읽었습니다.")
            return papers
            
        except Exception as e:
            print(f"논문 읽기 중 오류 발생: {str(e)}")
            return papers 
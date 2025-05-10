import csv

class PaperAnalyzer:
    def analyze_paper(self, paper):
        """논문 데이터를 분석하여 비즈니스 모델 요소를 추출합니다."""
        try:
            result = {
                '제목': paper.get('title', ''),
                '저자': paper.get('authors', ''),
                '발행일': paper.get('publication_date', ''),
                '저널명': paper.get('journal', ''),
                'DOI': paper.get('doi', ''),
                '초록': paper.get('abstract', ''),
                '키워드': paper.get('keywords', ''),
                '비즈니스 모델 분석': self._analyze_business_model(paper),
                '고객 세그먼트': self._extract_customer_segments(paper),
                '가치 제안': self._extract_value_proposition(paper),
                '수익 모델': self._extract_revenue_model(paper),
                '핵심 활동': self._extract_key_activities(paper),
                '핵심 자원': self._extract_key_resources(paper),
                '핵심 파트너십': self._extract_key_partnerships(paper),
                '채널': self._extract_channels(paper),
                '고객 관계': self._extract_customer_relationships(paper),
                '비용 구조': self._extract_cost_structure(paper),
                '시사점': self._extract_implications(paper),
                '한계점': self._extract_limitations(paper),
                '향후 연구 방향': self._extract_future_research(paper)
            }
            return result
        except Exception as e:
            print(f"논문 분석 중 오류 발생: {str(e)}")
            return None

    def _analyze_business_model(self, paper):
        """비즈니스 모델 분석"""
        # 실제 구현에서는 더 복잡한 분석 로직이 들어갈 수 있습니다
        return "비즈니스 모델 분석 결과"

    def _extract_customer_segments(self, paper):
        """고객 세그먼트 추출"""
        return "고객 세그먼트 분석 결과"

    def _extract_value_proposition(self, paper):
        """가치 제안 추출"""
        return "가치 제안 분석 결과"

    def _extract_revenue_model(self, paper):
        """수익 모델 추출"""
        return "수익 모델 분석 결과"

    def _extract_key_activities(self, paper):
        """핵심 활동 추출"""
        return "핵심 활동 분석 결과"

    def _extract_key_resources(self, paper):
        """핵심 자원 추출"""
        return "핵심 자원 분석 결과"

    def _extract_key_partnerships(self, paper):
        """핵심 파트너십 추출"""
        return "핵심 파트너십 분석 결과"

    def _extract_channels(self, paper):
        """채널 추출"""
        return "채널 분석 결과"

    def _extract_customer_relationships(self, paper):
        """고객 관계 추출"""
        return "고객 관계 분석 결과"

    def _extract_cost_structure(self, paper):
        """비용 구조 추출"""
        return "비용 구조 분석 결과"

    def _extract_implications(self, paper):
        """시사점 추출"""
        return "시사점 분석 결과"

    def _extract_limitations(self, paper):
        """한계점 추출"""
        return "한계점 분석 결과"

    def _extract_future_research(self, paper):
        """향후 연구 방향 추출"""
        return "향후 연구 방향 분석 결과"

    def save_to_csv(self, results, filename):
        """분석 결과를 CSV 파일로 저장"""
        try:
            # 기본값 정의
            default_values = {
                '비즈니스 모델 분석': '분석 불가',
                '고객 세그먼트': '미분류',
                '가치 제안': '미분류',
                '수익 모델': '미분류',
                '핵심 활동': '미분류',
                '핵심 자원': '미분류',
                '핵심 파트너십': '미분류',
                '채널': '미분류',
                '고객 관계': '미분류',
                '비용 구조': '미분류',
                '시사점': '미분류',
                '한계점': '미분류',
                '향후 연구 방향': '미분류'
            }

            # 데이터 전처리 및 품질 검증
            processed_results = []
            for result in results:
                processed_result = result.copy()
                
                # 빈 값 처리
                for key, default_value in default_values.items():
                    if key in processed_result and (not processed_result[key] or processed_result[key] == 'N/A'):
                        processed_result[key] = default_value
                
                # 초록 품질 검증
                if '초록' in processed_result:
                    abstract = processed_result['초록']
                    if len(abstract) < 50:  # 너무 짧은 초록
                        processed_result['초록'] = '초록 데이터 부족'
                    else:
                        # 줄바꿈 제거 및 특수문자 처리
                        processed_result['초록'] = abstract.replace('\n', ' ').replace('\r', ' ')
                
                # 키워드 중복 제거 및 정리
                if '키워드' in processed_result:
                    keywords = processed_result['키워드']
                    if isinstance(keywords, str):
                        # 쉼표로 구분된 키워드를 리스트로 변환
                        keyword_list = [k.strip() for k in keywords.split(',')]
                        # 중복 제거 및 정렬
                        processed_result['키워드'] = ', '.join(sorted(set(keyword_list)))
                
                # 모든 텍스트 필드의 특수문자 처리
                for key, value in processed_result.items():
                    if isinstance(value, str):
                        # 줄바꿈을 공백으로 대체
                        processed_result[key] = value.replace('\n', ' ').replace('\r', ' ')
                        # 따옴표 처리
                        processed_result[key] = value.replace('"', '""')
                
                processed_results.append(processed_result)
            
            # CSV 파일 생성
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                if processed_results:
                    writer = csv.DictWriter(f, fieldnames=processed_results[0].keys())
                    writer.writeheader()
                    writer.writerows(processed_results)
            
            print(f"분석 결과가 {filename}에 저장되었습니다.")
            
        except Exception as e:
            print(f"CSV 파일 저장 중 오류 발생: {str(e)}") 
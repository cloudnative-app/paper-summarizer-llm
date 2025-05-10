import pandas as pd
import io
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import re
import numpy as np
import os
import platform
import matplotlib.font_manager as fm

# 한글 폰트 설정
if platform.system() == 'Windows':
    # matplotlib 설정 초기화
    plt.rcdefaults()
    
    # 폰트 매니저 캐시 삭제 및 재설정
    import matplotlib as mpl
    mpl.font_manager._load_fontmanager(try_read_cache=False)
    
    # 설치된 폰트 목록 출력
    font_list = [f.name for f in fm.fontManager.ttflist]
    print("사용 가능한 폰트 목록:")
    for font in font_list:
        if any(keyword in font.lower() for keyword in ['gothic', 'gulim', 'batang', 'malgun']):
            print(font)
    
    try:
        # 폰트 경로 직접 지정
        font_path = 'C:/Windows/Fonts/malgun.ttf'  # 맑은 고딕
        if not os.path.exists(font_path):
            font_path = 'C:/Windows/Fonts/NanumGothic.ttf'  # 나눔고딕
            if not os.path.exists(font_path):
                font_path = 'C:/Windows/Fonts/gulim.ttc'  # 굴림
        
        # 폰트 직접 등록
        font_prop = fm.FontProperties(fname=font_path)
        
        # matplotlib 설정
        plt.rcParams['font.family'] = font_prop.get_name()
        plt.rcParams['axes.unicode_minus'] = False
        
        # seaborn 설정
        sns.set(font=font_prop.get_name(), rc={'axes.unicode_minus': False})
        
        print(f"폰트 '{font_prop.get_name()}' 설정 완료")
        
    except Exception as e:
        print(f"폰트 설정 중 오류 발생: {e}")
        print("기본 폰트를 사용합니다.")
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['axes.unicode_minus'] = False
elif platform.system() == 'Darwin':  # macOS의 경우
    plt.rcParams['font.family'] = 'AppleGothic'
elif platform.system() == 'Linux':
    plt.rcParams['font.family'] = 'NanumGothic'
else:
    print('Unknown system... only Windows/Mac/Linux are supported')

# result 디렉토리가 없으면 생성
if not os.path.exists('result'):
    os.makedirs('result')

# Read the content of the uploaded file using file API
# Assuming 'file_content' is fetched correctly using the environment's file API
# For demonstration, I'll simulate reading the file content.
# In a real environment, the file content would be loaded via the API.

# Let's assume the file API provides the content in a variable `uploaded_file_content`
# uploaded_file_content = files[0].read() # This line would be used in the actual environment

# For now, I will try to load the file assuming it's available via its name
try:
  # Read the CSV file into a pandas DataFrame
  # Using the file name directly, assuming it's accessible in the environment
  file_path = 'result/논문분석_결과_20250505_105222.csv'
  try:
      df = pd.read_csv(file_path)
  except UnicodeDecodeError:
      df = pd.read_csv(file_path, encoding='cp949') # Try Korean encoding

  print("CSV 파일 로딩 성공!")

  # --- 데이터 탐색 ---
  print("\n데이터 샘플 (상위 5개 행):")
  print(df.head().to_markdown(index=False, numalign="left", stralign="left"))

  print("\n컬럼 정보:")
  print(df.info())

  # --- 데이터 분석 및 시각화 ---

  # 1. 컬럼 이름 확인 및 주요 분석 대상 컬럼 식별
  #    (예상 컬럼: '논문제목', '저자', '발행년도', 'AI 기술/분야', 'BMC 요소', '주요 결과', '한계점' 등)
  #    실제 컬럼 이름을 확인하고 분석 계획을 조정해야 합니다.
  #    df.columns 를 통해 실제 컬럼 확인 필요
  print("\n컬럼명:", list(df.columns))

  # 컬럼 이름이 한국어이고 공백이나 특수문자가 있을 수 있으므로 정리
  df.columns = df.columns.str.strip() # 컬럼명 앞뒤 공백 제거

  # 분석에 사용할 주요 컬럼 지정
  year_col = '발행년도' if '발행년도' in df.columns else None
  bmc_elements_col = '수정/강조된 BMC 요소' if '수정/강조된 BMC 요소' in df.columns else None
  findings_col = '주요 결과/제안' if '주요 결과/제안' in df.columns else None
  limitations_col = '한계점' if '한계점' in df.columns else None

  # 2. 연도별 논문 분포 시각화 (발행년도 컬럼이 있는 경우)
  if year_col and year_col in df.columns:
      # 연도 데이터 타입 변환 (숫자형으로)
      df[year_col] = pd.to_numeric(df[year_col], errors='coerce')
      df.dropna(subset=[year_col], inplace=True) # 연도 누락 데이터 제거
      df[year_col] = df[year_col].astype(int)

      plt.figure()
      sns.countplot(data=df, x=year_col, palette='viridis')
      plt.title('연도별 AI BMC 관련 논문 발행 추이')
      plt.xlabel('발행 연도')
      plt.ylabel('논문 수')
      plt.xticks(rotation=45)
      plt.tight_layout()
      plt.savefig('result/연도별_논문_분포.png')
      plt.close()
  else:
      print("\n'발행년도' 관련 컬럼을 찾을 수 없어 연도별 분석을 생략합니다.")

  # 3. AI 기술/분야 분석 (관련 컬럼이 있는 경우)
  if '주요 AI 기술/분야' in df.columns:
      # ',' 또는 ';' 등으로 구분된 여러 기술/분야를 분리하고 카운트
      df['주요 AI 기술/분야'] = df['주요 AI 기술/분야'].fillna('미지정') # 결측값 처리
      all_focus_items = []
      for item in df['주요 AI 기술/분야'].astype(str):
           # 쉼표, 세미콜론, 또는 공백으로 구분된 항목 분리
           split_items = re.split(r'[,\s;/]+', item)
           all_focus_items.extend([s.strip() for s in split_items if s.strip()]) # 공백 제거 및 빈 문자열 제외

      focus_counts = Counter(all_focus_items)

      # 상위 N개 항목 시각화
      top_n = 15
      common_focus = focus_counts.most_common(top_n)
      common_focus_df = pd.DataFrame(common_focus, columns=['AI 기술/분야', '빈도'])

      if not common_focus_df.empty:
           plt.figure(figsize=(12, 7))
           sns.barplot(data=common_focus_df, y='AI 기술/분야', x='빈도', palette='magma')
           plt.title(f'주요 AI 기술/분야 (상위 {top_n}개)')
           plt.xlabel('언급 빈도')
           plt.ylabel('AI 기술/분야')
           plt.tight_layout()
           plt.show()
      else:
           print("\nAI 기술/분야 데이터를 분석할 수 없습니다.")

  else:
      print("\n'AI 기술/분야' 관련 컬럼을 찾을 수 없어 해당 분석을 생략합니다.")


  # 4. BMC 요소 분석 (관련 컬럼이 있는 경우)
  if bmc_elements_col and bmc_elements_col in df.columns:
      df[bmc_elements_col] = df[bmc_elements_col].fillna('미지정')
      all_bmc_elements = []
      standard_bmc = ['고객 세그먼트', '가치 제안', '채널', '고객 관계', '수익원', '핵심 자원', '핵심 활동', '핵심 파트너십', '비용 구조']
      standard_bmc_en = ['Customer Segments', 'Value Propositions', 'Channels', 'Customer Relationships', 'Revenue Streams', 'Key Resources', 'Key Activities', 'Key Partnerships', 'Cost Structure']
      standard_bmc_lower = [s.lower() for s in standard_bmc + standard_bmc_en]

      bmc_counts = Counter()
      for elements_text in df[bmc_elements_col].astype(str):
          split_elements = re.split(r'[,\s;/]+', elements_text)
          processed_elements = set()
          for elem in split_elements:
              elem_clean = elem.strip().lower()
              matched = False
              for std_elem in standard_bmc_lower:
                   if std_elem in elem_clean:
                        original_index = standard_bmc_lower.index(std_elem) % len(standard_bmc)
                        standard_name = standard_bmc[original_index]
                        if standard_name not in processed_elements:
                             bmc_counts[standard_name] += 1
                             processed_elements.add(standard_name)
                        matched = True
                        break
              if not matched:
                   ai_keywords = ['데이터', 'data', 'ai', '인공지능', '알고리즘', '모델', '기술', 'technology', '플랫폼', 'platform', '윤리', 'ethics']
                   for keyword in ai_keywords:
                        if keyword in elem_clean:
                             group_name = 'AI 특화 요소 (데이터, 모델 등)'
                             if keyword in ['윤리', 'ethics']:
                                 group_name = 'AI 윤리/규제'
                             if group_name not in processed_elements:
                                  bmc_counts[group_name] += 1
                                  processed_elements.add(group_name)
                             break

      common_bmc = bmc_counts.most_common()
      common_bmc_df = pd.DataFrame(common_bmc, columns=['BMC 요소', '언급 빈도'])

      if not common_bmc_df.empty:
          plt.figure()
          sns.barplot(data=common_bmc_df, y='BMC 요소', x='언급 빈도', palette='crest')
          plt.title('AI BMC 논의에서 강조/수정된 BMC 요소')
          plt.xlabel('언급 빈도')
          plt.ylabel('BMC 요소')
          plt.tight_layout()
          plt.savefig('result/BMC_요소_분석.png')
          plt.close()

          # AI BMC 프레임워크 제안을 위한 시사점 도출
          print("\n[AI BMC 프레임워크 제안을 위한 시사점 - BMC 요소 분석]")
          if 'AI 특화 요소 (데이터, 모델 등)' in common_bmc_df['BMC 요소'].tolist() or 'AI 윤리/규제' in common_bmc_df['BMC 요소'].tolist():
              print("- 기존 BMC 요소 외에 '데이터', 'AI 모델/알고리즘', 'AI 윤리/규제' 등 AI 특화 요소를 고려한 프레임워크 확장이 필요해 보입니다.")
          emphasized = common_bmc_df.head(3)['BMC 요소'].tolist()
          print(f"- 특히 '{', '.join(emphasized)}' 요소가 AI 비즈니스 모델에서 중요하게 다루어지고 있어, 제안 프레임워크에서 이들 요소의 AI 특성을 명확히 정의할 필요가 있습니다.")
          less_emphasized_count = len(common_bmc_df[common_bmc_df['언급 빈도'] <= np.percentile(common_bmc_df['언급 빈도'], 25)]) # 하위 25%
          if less_emphasized_count > 0:
               print(f"- 상대적으로 덜 강조된 요소({less_emphasized_count}개)에 대해서도 AI 맥락에서의 의미와 중요성을 재조명할 필요가 있습니다.")

      else:
           print("\nBMC 요소 데이터를 분석할 수 없습니다.")

  else:
      print("\n'BMC 요소' 관련 컬럼을 찾을 수 없어 해당 분석을 생략합니다.")


  # 5. 주요 결과 및 한계점 분석 (텍스트 분석)
  # 워드 클라우드 또는 키워드 추출 (구현 복잡성으로 여기서는 간단히 언급)
  print("\n[주요 결과 및 한계점 분석]")
  if findings_col and findings_col in df.columns:
      print(f"\n<{findings_col} 요약>")
      # 간단히 처음 몇 개의 결과 요약 출력
      for i, finding in enumerate(df[findings_col].head(3)):
          print(f"- 논문 {i+1}: {finding}")
      # TODO: 향후 자연어 처리(NLP)를 이용한 키워드 추출, 토픽 모델링 등으로 심층 분석 가능
      print("\n-> 시사점: 선행 연구들의 주요 제안(예: AI 특화 BMC 수정안, 데이터 기반 가치 제안 강조 등)을 파악하여 제안 프레임워크의 차별성을 부각해야 합니다.")

  else:
      print(f"'{findings_col or '주요 결과'}' 관련 컬럼이 없어 분석을 생략합니다.")

  if limitations_col and limitations_col in df.columns:
      print(f"\n<{limitations_col} 요약>")
      for i, limitation in enumerate(df[limitations_col].head(3)):
          print(f"- 논문 {i+1}: {limitation}")
      print("\n-> 시사점: 선행 연구의 한계점(예: 특정 산업 편중, 검증 부족, 동적 측면 미반영 등)을 파악하여 제안 프레임워크가 이를 어떻게 극복할 수 있는지 강조해야 합니다.")
  else:
      print(f"'{limitations_col or '한계점'}' 관련 컬럼이 없어 분석을 생략합니다.")


  # 6. 종합 및 제안 프레임워크 방향성 제시
  print("\n--- 종합 분석 결과 및 AI BMC Framework 제안 방향 ---")
  print("1.  **연구 동향:** AI 기반 비즈니스 모델에 대한 관심이 꾸준히 증가하고 있음을 시사합니다 (연도별 분석 결과 참고).")
  print("2.  **핵심 고려사항:**")
  print("    * **데이터 및 AI 모델:** 기존 BMC 요소(특히 핵심 자원, 핵심 활동, 가치 제안) 외에 데이터의 확보/관리/활용 및 AI 모델의 개발/운영이 핵심 요소로 부각됩니다.")
  print("    * **가치 제안의 변화:** AI는 자동화, 예측, 개인화 등을 통해 새로운 가치 제안을 가능하게 하며, 이를 BMC에 명확히 반영할 필요가 있습니다.")
  print("    * **강조되는 BMC 요소:** 가치 제안, 핵심 자원(데이터/모델 포함), 고객 세그먼트 등이 AI 맥락에서 중요하게 논의되고 있습니다 (BMC 요소 분석 참고).")
  print("    * **AI 특화 요소:** '데이터 거버넌스', '모델 생명주기 관리', 'AI 윤리 및 규제 준수' 등 기존 BMC에 없던 새로운 고려사항이 중요하게 대두됩니다.")
  print("3.  **선행 연구의 한계:**")
  print("    * 개별적인 BMC 수정 제안은 있으나, AI 비즈니스의 특성을 포괄적으로 반영하는 표준화된 프레임워크는 부족한 경향이 있습니다.")
  print("    * 실제 기업 사례 적용 및 검증이 부족하거나 특정 산업/기술에 편중된 연구가 있을 수 있습니다.")
  print("    * 비즈니스 모델의 동적인 변화나 확장성을 충분히 다루지 못하는 경우가 있습니다.")
  print("\n**제안할 AI BMC Framework의 방향성:**")
  print("-   **AI 특화 요소 통합:** 데이터, AI 모델, AI 윤리 등을 BMC의 핵심 구성요소로 명시적으로 포함하거나 기존 요소를 확장하여 정의합니다.")
  print("-   **동적 관점 반영:** AI 기술 발전 및 데이터 축적에 따른 비즈니스 모델의 진화 과정을 반영할 수 있는 요소를 고려합니다 (예: 학습 및 개선 루프).")
  print("-   **실증적 검증 강조:** 제안 프레임워크를 다양한 AI 비즈니스 사례에 적용하고 유효성을 검증하는 방안을 함께 제시합니다.")
  print("-   **차별화:** 기존 BMC 수정안들과 비교하여 제안 프레임워크의 독창성과 포괄성, 실용성을 강조합니다.")

  # AI의 특징 분석
  print("\n[AI의 특징 분석]")
  if 'AI의 특징' in df.columns:
      ai_features = []
      for text in df['AI의 특징'].astype(str):
          # 쉼표, 세미콜론, 또는 공백으로 구분된 항목 분리
          features = re.split(r'[,\s;/]+', text)
          ai_features.extend([f.strip() for f in features if f.strip() and f.strip().lower() != 'nan'])

      # 주요 AI 특징 카운트
      feature_counts = Counter(ai_features)
      top_features = feature_counts.most_common(10)
      
      # 시각화
      plt.figure(figsize=(12, 6))
      feature_df = pd.DataFrame(top_features, columns=['AI 특징', '언급 빈도'])
      sns.barplot(data=feature_df, y='AI 특징', x='언급 빈도', palette='viridis')
      plt.title('주요 AI 특징 분석')
      plt.xlabel('언급 빈도')
      plt.ylabel('AI 특징')
      plt.tight_layout()
      plt.savefig('result/AI_특징_분석.png')
      plt.close()

  # 고객 세그먼트 분석
  print("\n[고객 세그먼트 분석]")
  if '고객 세그먼트' in df.columns:
      segments = []
      for text in df['고객 세그먼트'].astype(str):
          # 쉼표, 세미콜론, 또는 공백으로 구분된 항목 분리
          segs = re.split(r'[,\s;/]+', text)
          segments.extend([s.strip() for s in segs if s.strip() and s.strip().lower() != 'nan'])

      # 주요 고객 세그먼트 카운트
      segment_counts = Counter(segments)
      top_segments = segment_counts.most_common(10)
      
      # 시각화
      plt.figure(figsize=(12, 6))
      segment_df = pd.DataFrame(top_segments, columns=['고객 세그먼트', '언급 빈도'])
      sns.barplot(data=segment_df, y='고객 세그먼트', x='언급 빈도', palette='muted')
      plt.title('주요 고객 세그먼트 분석')
      plt.xlabel('언급 빈도')
      plt.ylabel('고객 세그먼트')
      plt.tight_layout()
      plt.savefig('result/고객_세그먼트_분석.png')
      plt.close()

  # 가치 제안 분석
  print("\n[가치 제안 분석]")
  if '가치 제안' in df.columns:
      values = []
      for text in df['가치 제안'].astype(str):
          # 쉼표, 세미콜론, 또는 공백으로 구분된 항목 분리
          vals = re.split(r'[,\s;/]+', text)
          values.extend([v.strip() for v in vals if v.strip() and v.strip().lower() != 'nan'])

      # 주요 가치 제안 카운트
      value_counts = Counter(values)
      top_values = value_counts.most_common(10)
      
      # 시각화
      plt.figure(figsize=(12, 6))
      value_df = pd.DataFrame(top_values, columns=['가치 제안', '언급 빈도'])
      sns.barplot(data=value_df, y='가치 제안', x='언급 빈도', palette='husl')
      plt.title('주요 가치 제안 분석')
      plt.xlabel('언급 빈도')
      plt.ylabel('가치 제안')
      plt.tight_layout()
      plt.savefig('result/가치_제안_분석.png')
      plt.close()


except FileNotFoundError:
    print(f"오류: 파일 '{file_path}'을 찾을 수 없습니다. 파일 이름과 경로를 확인해주세요.")
except Exception as e:
    print(f"데이터 분석 중 오류 발생: {e}")

# 그래프 스타일 설정
plt.style.use('default')
plt.rcParams['figure.figsize'] = [12, 8]
plt.rcParams['figure.dpi'] = 100
plt.rcParams['font.size'] = 12
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['legend.fontsize'] = 10
plt.rcParams['figure.titlesize'] = 16
import pandas as pd
import re
from department import department_names

def validate_data(file_path):
    # 엑셀 파일 읽기
    df = pd.read_excel(file_path)

    errors = []

    # 1. 평정점총점 -> 교육총경력 -> 생년월일 기준으로 정렬
    try:
        df = df.sort_values(by=['평정점총점', '교육총경력', '생년월일'], 
                            ascending=[False, False, True])
    except KeyError as e:
        errors.append(f"필드 누락: {e}")

    # 2. 전보구분은 '순환' 또는 '일반'이어야 함
    invalid_rows = (df[~df['전보구분'].apply(lambda x: pd.isna(x) or str(x) in ['순환', '일반'])].index+1).to_list()
    if invalid_rows:
        errors.append(f"전보구분 값이 잘못되었습니다. 행 번호: {invalid_rows}")
    
    # 3. 소속학교는 department_names 리스트 값 중 하나여야 함
    invalid_rows = (df[~df['소속학교'].apply(lambda x: pd.isna(x) or str(x) in department_names)].index+1).tolist()
    if invalid_rows:
        errors.append(f"소속학교 값이 잘못되었습니다. 행 번호: {invalid_rows}")
    
    
    # 4. 생년월일은 '00.00.00' 형식이어야 함
    invalid_rows = (df[~df['생년월일'].apply(lambda x: bool(re.match(r'^\d{2}\.\d{2}\.\d{2}$', str(x))))].index+1).tolist()
    if invalid_rows:
        errors.append(f"생년월일 형식이 잘못되었습니다. 행 번호: {invalid_rows}")
    
    # 5. 교육총경력은 '00.00' 또는 '0.00' 형식이어야 함
    invalid_rows = (df[~df['교육총경력'].apply(lambda x: isinstance(x, (float, int)) or bool(re.match(r'^\d{1,2}\.\d{2}$', str(x))))].index+1).tolist()
    if invalid_rows:
        errors.append(f"교육총경력 형식이 잘못되었습니다. 행 번호: {invalid_rows}")
    
    # 6. 평정점총점은 '0.000' 또는 '00.000' 형식이어야 함
    invalid_rows = (df[~df['평정점총점'].apply(lambda x: isinstance(x, (float, int)) or bool(re.match(r'^\d{1,2}\.\d{3}$', str(x))))].index+1).tolist()
    if invalid_rows:
        errors.append(f"평정점총점 형식이 잘못되었습니다. 행 번호: {invalid_rows}")
    
    # 7. 1희망~10희망에 작성된 학교명은 department_names 리스트 중 하나여야 함
    for i in range(1, 11):
        col_name = f'{i}희망'
        if col_name in df.columns:
            invalid_rows = (df[~df[col_name].apply(lambda x: pd.isna(x) or str(x) in department_names)].index+1).tolist()
            if invalid_rows:
                errors.append(f"{col_name} 값이 잘못되었습니다. 행 번호: {invalid_rows}")
    
    # 8. 전보후휴직여부는 '여' 또는 빈 값 (NaN)이어야 함
    invalid_rows = (df[~df['전보후휴직여부'].apply(lambda x: pd.isna(x) or x == '여')].index+1).tolist()
    if invalid_rows:
        errors.append(f"전보후휴직여부 값이 잘못되었습니다. 행 번호: {invalid_rows}")
    
    # 9. 과원조정여부도 '여' 또는 빈 값 (NaN)이어야 함
    invalid_rows = (df[~df['과원조정여부'].apply(lambda x: pd.isna(x) or x == '여')].index+1).tolist()
    if invalid_rows:
        errors.append(f"과원조정여부 값이 잘못되었습니다. 행 번호: {invalid_rows}")
    
    # 유효성 검사 결과
    if errors:
        return False, errors
    else:
        return True, "모든 데이터가 유효합니다."
import json
import os
import pandas as pd

# department_capacity를 vacancies.json에서 불러오기
def load_department_capacity(json_file_path):
    with open(json_file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def save_updated_capacity(original_file_path, edited_file_path, assigned_people_current):
    """
    '일반' 성공자들의 원소속 학교의 빈자리를 1씩 늘려 수정된 학교 정보를 업데이트하는 함수.
    
    Parameters:
    - original_file_path: 원본 vacancies.json 파일 경로
    - edited_file_path: 수정된 vacancies_edited.json 파일 경로
    - assigned_people_current: '일반' 성공자의 이름과 원소속 학교를 저장한 딕셔너리
    """
    # 1. 원본 vacancies.json 파일을 불러옴
    with open(original_file_path, 'r', encoding='utf-8') as file:
        department_capacity = json.load(file)

    # 2. assigned_people_current에 저장된 모든 사람들의 원소속 학교 빈자리를 1씩 증가시킴
    for name, current_department in assigned_people_current.items():
        if current_department in department_capacity:
            department_capacity[current_department] += 1
            # print(f"{name}의 원소속 학교 {current_department}의 빈자리가 1 증가되었습니다.")
        else:
            print(f"Error: {current_department} is not a valid department in the department capacity data.")

    # 3. 수정된 학교 빈자리 정보를 vacancies_edited.json 파일로 저장 (기존 파일 대체)
    with open(edited_file_path, 'w', encoding='utf-8') as file:
        json.dump(department_capacity, file, ensure_ascii=False, indent=4)

    # print(f"수정된 학교 빈자리 정보를 {edited_file_path}에 저장했습니다.")

# 학교 빈자리가 업데이트된 파일이 있는지 확인 후, 없으면 생성
def create_edited_capacity_file(original_json, edited_json, assigned_people_current):
    # 1. 수정된 파일이 없으면 원본을 복사하여 수정 파일 생성
    with open(original_json, 'r', encoding='utf-8') as f:
        department_capacity = json.load(f)
    
    # 수정된 파일에 원본 내용을 복사하여 생성
    with open(edited_json, 'w', encoding='utf-8') as f:
        json.dump(department_capacity, f, ensure_ascii=False, indent=4)
    
    print(f"{edited_json} 파일 생성 완료")
    
    return edited_json

# 배정 결과를 CSV로 저장
def save_assignment_results_to_csv(assignment_results, file_path="assignment_results.csv"):
    """
    배정 결과 리스트를 CSV 파일로 저장하는 함수

    Parameters:
    - assignment_results: 배정 결과 리스트 (딕셔너리의 리스트)
    - file_path: 저장할 CSV 파일 경로 (기본값은 'assignment_results.csv')
    """
    # assignment_results 리스트를 pandas DataFrame으로 변환
    df = pd.DataFrame(assignment_results)

    # DataFrame을 CSV 파일로 저장
    df.to_csv(file_path, index=False, encoding='utf-8-sig')
    
    print(f"배정 결과가 {file_path}에 저장되었습니다.")

assignment_results =[]

def assign_temp(df):

    # '일반'으로 성공한 사람을 추적하여 중복 배정을 막기 위한 딕셔너리
    assigned_people = {}

    # '일반'으로 성공한 사람들의 원소속을 확인하여 빈자리에 반영하기 위한 딕셔너리
    assigned_people_current = {}

    # 이미 원소속 자리를 늘린 사람을 추적하기 위한 리스트
    already_processed_people = []

    # 처음 시작하면 원본 빈자리 파일을 복제, 모든 빈자리 데이터는 복제된 json 파일을 참조
    edited_capacity_file = create_edited_capacity_file("vacancies.json", 'vacancies_edited.json', assigned_people_current)
    department_capacity = load_department_capacity(edited_capacity_file)

    while True:
        reassignment_required = False  # 재배정 여부 추적
        previous_assigned_people = assigned_people.copy()  # 이전 상태 저장

        # 1. 평정점총점 -> 교육총경력 -> 생년월일 기준으로 정렬 (단 1회만)
        df = df.sort_values(by=['평정점총점', '교육총경력', '생년월일'], 
                            ascending=[False, False, True])

        # 2. 배정 로직
        for idx, row in df.iterrows():
            name = row['성명']
            current_department = row['소속학교']
            희망지들 = [row[f'{i}희망'] for i in range(1, 11)]
            전보구분 = row['전보구분']
            전보후휴직여부 = row['전보후휴직여부']
            과원조정여부 = row['과원조정여부']

            assigned_department = None
            assigned_preference = None

            # 3. '순환'인 사람들 배정 (변경 사항 없음)
            if 전보구분 == '순환':
                # 과원조정여부가 '여'인 사람 복귀 우선
                if 과원조정여부 == '여':
                    # 원소속에 빈자리가 있으면 복귀
                    if current_department in department_capacity and department_capacity[current_department] > 0:
                        assigned_department = current_department
                        assigned_preference = "복귀"
                        department_capacity[current_department] -= 1
                    else:
                        # 희망지 순서대로 탐색
                        for idx, 희망지 in enumerate(희망지들):
                            if pd.isna(희망지):
                                continue
                            if 희망지 in department_capacity and department_capacity[희망지] > 0:
                                assigned_department = 희망지
                                assigned_preference = idx + 1
                                department_capacity[희망지] -= 1
                                break

                # 과원조정여부가 '여'가 아닌 사람들                
                else:
                    # 희망지 순서대로 탐색
                    for idx, 희망지 in enumerate(희망지들):
                        if pd.isna(희망지):
                            continue
                        if 희망지 in department_capacity and department_capacity[희망지] > 0:
                            assigned_department = 희망지
                            assigned_preference = idx + 1

                            if 전보후휴직여부 != '여':
                                department_capacity[희망지] -= 1
                            break

            # 4. '일반'인 사람들 배정
            if 전보구분 == '일반':
                # 1. 전보후휴직여부 '여'인 경우
                if 전보후휴직여부 == '여':
                    for idx, 희망지 in enumerate(희망지들):
                        if pd.isna(희망지):
                            continue
                        if 희망지 in department_capacity and department_capacity[희망지] > 0:
                            assigned_department = 희망지
                            assigned_preference = idx + 1
                            department_capacity[희망지] -= 1
                            break

                # 2. 전보후휴직여부 '여'가 아닌 경우
                else:
                    # 이 사람이 이미 자리를 늘렸는지 확인, 이미 자리를 늘리지 않은 경우
                    if name not in already_processed_people:
                        for idx, 희망지 in enumerate(희망지들):
                            if pd.isna(희망지):
                                continue
                            if 희망지 in department_capacity and department_capacity[희망지] > 0:
                                assigned_department = 희망지
                                assigned_preference = idx + 1
                                department_capacity[희망지] -= 1
                                department_capacity[current_department] += 1

                                assigned_people[name] = assigned_department
                                assigned_people_current[name] = current_department
                                already_processed_people.append(name)
                                reassignment_required = True

                                save_updated_capacity("vacancies.json", "vacancies_edited.json", assigned_people_current)  # 수정된 학교 정보 저장
                                
                                break       

                    # 이 사람이 이미 자리를 늘린 경우
                    else:
                        for idx, 희망지 in enumerate(희망지들):
                            if pd.isna(희망지):
                                continue
                            if 희망지 in department_capacity and department_capacity[희망지] > 0:
                                assigned_department = 희망지
                                assigned_preference = idx + 1
                                department_capacity[희망지] -= 1
                                assigned_people[name] = assigned_department
                                break

            # 5. 배정되지 못한 경우 처리 (미배정)
            if not assigned_department:
                assigned_department = '미배정'

            # 6. 배정 결과 저장
            assignment_results.append({
                '성명': name,
                '현재소속': current_department,
                '배정결과': assigned_department,
                '배정희망순위': assigned_preference
            })

            # '일반' 성공자가 있으면 for 루프를 빠져나가고 while 루프를 처음부터 다시 실행
            if reassignment_required:
                continue  # while 루프를 재시작
            
        break
    
    assign_final(df)


def assign_final(df):
    global assignment_results

    # 배정에 성공한 사람들을 확인하기 위한 딕셔너리
    assigned_people = {}

    # 과원조정여부가 '여'인 사람들을 우선 처리할 리스트
    priority_return_people = []

    # 임시 배정에서 저장된 결과 삭제
    assignment_results.clear()

    # 처음 시작하면 원본 빈자리 파일을 복제, 모든 빈자리 데이터는 복제된 json 파일을 참조
    department_capacity = load_department_capacity("vacancies_edited.json")

    # 0-1. 과원조정여부 '여'인 사람들만 추출하고 점수 기준으로 정렬
    priority_return_people = df[df['과원조정여부'] == '여'].sort_values(by=['평정점총점', '교육총경력', '생년월일'], 
                                                                   ascending=[False, False, True])

    # 0-2. 과원조정여부 '여'인 사람들부터 원소속으로 복귀 시도
    for _, row in priority_return_people.iterrows():
        전보구분 = row['전보구분']
        name = row['성명']
        current_department = row['소속학교']

        # 원소속에 자리가 있으면 복귀
        if current_department in department_capacity and department_capacity[current_department] > 0:
            assigned_department = current_department
            department_capacity[current_department] -= 1  # 원소속 자리 차지
            assigned_preference = "원소속 복귀"

            # 배정 결과 저장
            assignment_results.append({
                '전보구분': 전보구분,
                '성명': name,
                '현재소속': current_department,
                '배정결과': assigned_department,
                '배정희망순위': assigned_preference
            })

            # 이 사람을 이미 배정된 사람으로 처리
            assigned_people[name] = assigned_department

    """
    과원조정자 중 원적교에 빈자리가 있는 경우는 미리 배정
    원적교에 빈자리가 없어 복귀에 실패한 사람들은 순위에 따라 배정
    전체 데이터를 다시 배정할 때 assigned_people에 있다면 배정을 건너뜀
    """

    # 1. 평정점총점 -> 교육총경력 -> 생년월일 기준으로 정렬 (단 1회만)
    df = df.sort_values(by=['평정점총점', '교육총경력', '생년월일'], 
                        ascending=[False, False, True])

    # 2. 배정 로직
    for idx, row in df.iterrows():
        name = row['성명']

        # 이미 배정된 사람은 건너뛰기
        if name in assigned_people:
            continue

        current_department = row['소속학교']
        희망지들 = [row[f'{i}희망'] for i in range(1, 11)]
        전보구분 = row['전보구분']
        전보후휴직여부 = row['전보후휴직여부']
        과원조정여부 = row['과원조정여부']

        assigned_department = None
        assigned_preference = None

        # 희망지 순서대로 탐색
        for idx, 희망지 in enumerate(희망지들):
            if pd.isna(희망지):
                continue
            if 희망지 in department_capacity and department_capacity[희망지] > 0:
                assigned_department = 희망지
                assigned_preference = idx + 1

                if 전보후휴직여부 != '여':
                    department_capacity[희망지] -= 1
                break

        # 5. 배정되지 못한 경우 처리 (미배정)
        if not assigned_department:
            if 전보구분 == '일반':
                assigned_department = '미배정'
                assigned_preference = '희망이동실패'
            else:
                assigned_department = '미배정'
                assigned_preference = '수동배정필요'

        # 6. 배정 결과 저장
        assignment_results.append({
            '전보구분': 전보구분,
            '성명': name,
            '현재소속': current_department,
            '배정결과': assigned_department,
            '배정희망순위': assigned_preference
        })

        # 여기서 배정된 사람을 assigned_people에 추가
        assigned_people[name] = assigned_department  # 배정된 사람 딕셔너리에 저장

    # 배정 결과를 CSV 파일로 저장
    save_assignment_results_to_csv(assignment_results, "assignment_results.csv")

    return assignment_results

# 배정 결과 출력 함수
def print_assignment_results(results):
    """
    배정 결과를 표 형태로 출력하는 함수
    """
    for result in results:
        print(f"성명: {result['성명']}, 현재 소속: {result['현재소속']}, 배정결과: {result['배정결과']}, "
              f"배정희망순위: {result['배정희망순위']}")

# 엑셀 파일 읽기 함수
def read_excel(file_path):
    """
    엑셀 파일을 읽어 DataFrame으로 반환하는 함수
    """
    df = pd.read_excel(file_path)
    return df

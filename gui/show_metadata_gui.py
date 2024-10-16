from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QVBoxLayout, QDialog, QPushButton, QHeaderView, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog, QMessageBox
import pandas as pd
import json, csv

class ShowMetadataWindow(QDialog):
    def __init__(self, df):
        super().__init__()
        self.df = df  # df를 받아서 저장
        
        # 창의 제목과 크기 설정
        self.setWindowTitle('배정 결과')
        self.setGeometry(300, 300, 1000, 600)  # 모달 창 크기 설정
        
        # 메인 레이아웃 (세로 방향)
        layout = QVBoxLayout(self)

        # 테이블 위젯 생성
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(6)  # 학교명, 배정전, 배정후, 증감, 최종배정인원, 추가배정필요인원
        self.table_widget.setHorizontalHeaderLabels(['학교명', '빈자리(배정전)', '빈자리(배정후)', '증감', '최종배정인원', '추가배정필요인원'])

        # 테이블 크기 설정
        self.table_widget.setMinimumWidth(950)  # 창에 맞춰 최소 가로 크기 설정
        self.table_widget.setMinimumHeight(550)  # 창에 맞춰 최소 세로 크기 설정

        # 헤더 크기를 창 크기에 맞게 확장
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)  # 가로 크기 조정

        # 테이블에 데이터 채우기
        self.metadata_table()

        # 테이블을 가로로 중앙에 배치하기 위한 QHBoxLayout 사용
        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.table_widget)
        hbox.addStretch(1)

        # 레이아웃에 QHBoxLayout 추가
        layout.addLayout(hbox)
    
        # '메타데이터 다운로드' 버튼을 테이블 아래에 추가
        self.download_button = QPushButton('메타데이터 다운로드')
        self.download_button.clicked.connect(self.download_metadata)  # 버튼 클릭 시 엑셀로 다운로드
        layout.addWidget(self.download_button)  # 버튼을 마지막에 추가하여 아래로 배치

    def metadata_table(self):
        # vacancies.json (배정 전) 파일 불러오기
        with open('vacancies.json', 'r', encoding='utf-8') as file:
            initial_vacancies = json.load(file)

        # vacancies_edited.json (배정 후) 파일 불러오기
        with open('vacancies_edited.json', 'r', encoding='utf-8') as file:
            edited_vacancies = json.load(file)

        # assignment_results.csv 파일에서 배정 인원 및 전보후휴직여부 '여'인 인원 계산
        assignment_counts, leave_people_counts = self.calculate_assignments_by_department('assignment_results.csv', self.df)

        # 학교명에 대해 배정 전/후 데이터를 비교
        department_names = initial_vacancies.keys()
        self.table_widget.setRowCount(len(department_names))

        for row_idx, department in enumerate(department_names):
            initial_vacancy = initial_vacancies.get(department, 0)
            edited_vacancy = edited_vacancies.get(department, 0)
            assigned_people_count = assignment_counts.get(department, 0)  # 배정된 인원 수
            leave_count = leave_people_counts.get(department, 0) # 전보후휴직여부 '여' 인원 수
            actual_occupancy = assigned_people_count - leave_count  # 실제 배정인원 (휴직자 제외)

            # 추가 배정 필요 인원 계산
            additional_required = max(0, edited_vacancy - actual_occupancy)

            # 증감 계산
            vacancy_change = edited_vacancy - initial_vacancy

            # 테이블에 데이터 삽입
            self.table_widget.setItem(row_idx, 0, QTableWidgetItem(department))  # 학교명
            self.table_widget.setItem(row_idx, 1, QTableWidgetItem(str(initial_vacancy)))  # 배정전 빈자리
            self.table_widget.setItem(row_idx, 2, QTableWidgetItem(str(edited_vacancy)))   # 배정후 빈자리
            self.table_widget.setItem(row_idx, 3, QTableWidgetItem(str(vacancy_change)))   # 증감
            self.table_widget.setItem(row_idx, 4, QTableWidgetItem(str(assigned_people_count)))  # 배정인원
            self.table_widget.setItem(row_idx, 5, QTableWidgetItem(str(additional_required)))  # 추가 배정 필요 인원

        # 내용에 맞게 열 크기를 조정
        self.table_widget.resizeColumnsToContents()

    # assignment_results.csv에서 데이터를 읽고 df에서 전보후휴직여부 필드 가져오기
    def calculate_assignments_by_department(self, csv_file_path, df):
        # 학교별로 배정된 인원을 저장하는 딕셔너리
        assignment_counts = {}

        # 학교별 전보후휴직여부 '여'인 인원을 저장하는 딕셔너리
        leave_people_counts = {}

        # CSV 파일 읽기
        with open(csv_file_path, newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                department = row['배정결과']
                name = row['성명']
                
                # 전보후휴직여부 필드 가져오기, 예외 처리 추가
                try:
                    leave_status = df.loc[df['성명'] == name, '전보후휴직여부'].values[0]  # 해당 이름의 전보후휴직여부 가져오기
                except IndexError:
                    leave_status = None  # 이름이 없을 경우 None 처리

                # 배정된 인원 수 계산
                if department in assignment_counts:
                    assignment_counts[department] += 1
                else:
                    assignment_counts[department] = 1

                # 전보후휴직여부가 '여'인 인원 수 계산
                if leave_status == '여':
                    if department in leave_people_counts:
                        leave_people_counts[department] += 1
                    else:
                        leave_people_counts[department] = 1

        return assignment_counts, leave_people_counts
    
    def download_metadata(self):
        # 저장할 파일 경로 선택 대화 상자 열기
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_path, _ = QFileDialog.getSaveFileName(self, 
                                                "메타데이터 파일 저장", 
                                                "메타데이터.xlsx",  # 기본 파일명
                                                "Excel Files (*.xlsx);;All Files (*)", 
                                                options=options)
        if file_path:
            try:
                # 메타데이터 표 데이터를 DataFrame으로 변환
                data = []
                for row in range(self.table_widget.rowCount()):
                    row_data = []
                    for column in range(self.table_widget.columnCount()):
                        item = self.table_widget.item(row, column)
                        row_data.append(item.text() if item is not None else "")
                    data.append(row_data)

                # 열 제목(헤더) 가져오기
                headers = [self.table_widget.horizontalHeaderItem(i).text() for i in range(self.table_widget.columnCount())]

                # DataFrame 생성
                df = pd.DataFrame(data, columns=headers)

                # DataFrame을 엑셀 파일로 저장
                df.to_excel(file_path, index=False)
                QMessageBox.information(self, "성공", "메타데이터가 성공적으로 저장되었습니다.")

            except Exception as e:
                QMessageBox.critical(self, "오류", f"파일 저장 중 오류가 발생했습니다: {str(e)}")
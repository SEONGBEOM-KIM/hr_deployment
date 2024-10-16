import sys
import os
import csv
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QFileDialog, QVBoxLayout, QLineEdit, QMessageBox, QTableWidget, QTableWidgetItem
import pandas as pd
import json

# 현재 파일의 경로를 기준으로 상위 폴더를 sys.path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.append(parent_dir)

from data_validation import validate_data  # data_validation.py에서 validate_data 불러오기
from assignment_logic import assign_temp
from gui.assignment_results_gui import AssignmentResultWindow
from gui.show_metadata_gui import ShowMetadataWindow


class AssignmentProcessor(QWidget):
    def __init__(self):
        super().__init__()
        
        # 윈도우 제목과 크기 설정
        self.setWindowTitle('인사이동 작업 실행')
        self.setGeometry(300, 300, 400, 200)
        self.df = None  # 엑셀 파일에서 읽어온 데이터를 저장할 변수 추가
        self.department_capacity = None  # 학교 정원을 저장할 변수 추가
        
        # 유효성 검사 결과 저장할 변수
        self.validation_passed = False
        self.validation_errors = []

        # 레이아웃 설정
        layout = QVBoxLayout()
        
        # 레이아웃의 여백을 0으로 설정 (위, 아래, 왼쪽, 오른쪽 여백)
        layout.setContentsMargins(0, 0, 0, 0)

        # 위젯 간의 간격을 줄임 (예: 5px)
        layout.setSpacing(10)

        # 파일 선택 레이블
        self.label = QLabel('엑셀 파일을 선택하세요:')
        layout.addWidget(self.label)
        
        # 파일 선택 버튼
        self.btn_select_file = QPushButton('파일 선택', self)
        self.btn_select_file.clicked.connect(self.select_file)
        layout.addWidget(self.btn_select_file)
        
        # 파일 경로를 표시할 텍스트박스
        self.file_path_box = QLineEdit(self)
        self.file_path_box.setReadOnly(True)
        layout.addWidget(self.file_path_box)
                
        # 파일 경로와 파일 업로드 버튼 사이에 공간 추가
        layout.addSpacing(20)

        # 파일 업로드 버튼
        self.btn_upload = QPushButton('파일 업로드 및 데이터 유효성 검사', self)
        self.btn_upload.clicked.connect(self.upload_file)
        layout.addWidget(self.btn_upload)

        # '배정 작업 시작하기' 버튼 추가
        self.btn_start_assignment = QPushButton('배정 작업 시작하기', self)
        self.btn_start_assignment.clicked.connect(self.start_assignment)
        layout.addWidget(self.btn_start_assignment)
        
        # 배정 시작 버튼과 배정 결과 확인하기 버튼 사이에 공간 추가
        layout.addSpacing(20)

        # '배정 결과 확인하기' 버튼 추가
        self.btn_show_results = QPushButton('결과 확인하기', self)
        self.btn_show_results.clicked.connect(self.show_results)
        layout.addWidget(self.btn_show_results)

        # '메타데이터 확인하기' 버튼 추가
        self.btn_show_metadata = QPushButton('메타데이터 확인하기', self)
        self.btn_show_metadata.clicked.connect(self.show_metadata)
        layout.addWidget(self.btn_show_metadata)

        # 창에 레이아웃 적용
        self.setLayout(layout)
    
    # 파일 선택 창 열기
    def select_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "엑셀 파일 선택", "", "Excel Files (*.xlsx *.xls *.xlsm);;All Files (*)", options=options)
        if file_path:
            self.file_path_box.setText(file_path)

    # vacancies.json 파일에서 학교 정원 불러오기
    def load_department_capacity(self):
        try:
            with open("vacancies.json", 'r', encoding='utf-8') as file:
                self.department_capacity = json.load(file)
        except FileNotFoundError:
            QMessageBox.critical(self, "에러", "vacancies.json 파일을 찾을 수 없습니다.")
            self.department_capacity = None

    # 파일 업로드 처리 및 유효성 검사
    def upload_file(self):
        file_path = self.file_path_box.text()
        if not file_path:
            QMessageBox.warning(self, "경고", "파일을 먼저 선택하세요.")
            return
        
        try:
            # 엑셀 파일 읽기
            self.df = pd.read_excel(file_path)
            QMessageBox.information(self, "성공", "파일이 성공적으로 업로드되었습니다.")

            # 학교 정원 정보 불러오기
            self.load_department_capacity()

            # 데이터 유효성 검사 처리
            self.validation_passed, result = validate_data(file_path)
            
            if self.validation_passed:
                QMessageBox.information(self, "유효성 검사 통과", "모든 데이터가 유효합니다.")
                self.validation_errors = []  # 오류가 없으므로 오류 리스트 초기화
            else:
                error_message = "\n".join(result)
                QMessageBox.warning(self, "유효성 검사 실패", f"유효성 검사에서 오류가 발생했습니다:\n{error_message}")
                self.validation_errors = result  # 오류 메시지를 저장

        except Exception as e:
            QMessageBox.critical(self, "에러", f"파일을 처리하는 중 오류가 발생했습니다: {str(e)}")
            self.validation_passed = False  # 오류가 발생하면 유효성 검사를 실패로 처리
    
    # 배정 작업 시작 처리
    def start_assignment(self):
        if self.validation_passed:
            # 유효성 검사가 통과된 경우 배정 작업을 진행
            QMessageBox.information(self, "배정 작업 시작", "배정 작업을 시작합니다.")
            # 실제 배정 로직을 호출할 부분을 여기에 추가
            self.assign_positions()

        else:
            # 유효성 검사에서 오류가 있을 경우
            error_message = "\n".join(self.validation_errors)
            QMessageBox.warning(self, "배정 작업 실패", f"유효성 검사를 먼저 실행하세요.\n{error_message}")
    
    # 배정 작업 로직
    def assign_positions(self):
        if self.df is not None:
            assign_temp(self.df)  # 읽어온 df와 department_capacity_file을 assign 함수로 전달
            QMessageBox.information(self, "배정 작업 완료", "배정 작업이 완료되었습니다.")

        else:
            QMessageBox.warning(self, "에러", "배정할 데이터 또는 학교 정원 정보가 없습니다. 파일을 먼저 업로드하세요.")

    # 배정 결과 확인
    def show_results(self):
        results_csv_file = 'assignment_results.csv'

        if os.path.exists(results_csv_file):
            # CSV 파일을 읽어옴
            assignment_results = self.read_assignment_results(results_csv_file)

            # 결과 창을 팝업으로 띄움
            dialog = AssignmentResultWindow(assignment_results)
            dialog.exec_()  # 모달 창으로 실행
        else:
            QMessageBox.warning(self, "에러", "배정 결과가 없습니다.")

    # CSV 데이터 읽어오기
    def read_assignment_results(self, csv_file_path):
        assignment_results = []

        # CSV 파일에서 데이터를 읽어옴
        with open(csv_file_path, newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)  # DictReader로 딕셔너리 형태로 읽음
            for row in reader:
                assignment_results.append({
                    '전보구분': row['전보구분'],
                    '성명': row['성명'],
                    '현재소속': row['현재소속'],
                    '배정결과': row['배정결과'],
                    '배정희망순위': row['배정희망순위']
                })

        return assignment_results

    # 메타데이터 확인
    def show_metadata(self):
        if self.df is not None:
            dialog = ShowMetadataWindow(self.df)
            dialog.exec_()

        else:
            QMessageBox.warning(self, "에러", "데이터가 없습니다. 유효성 검사와 배정 작업을 먼저 실행하세요.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AssignmentProcessor()
    window.show()
    sys.exit(app.exec_())
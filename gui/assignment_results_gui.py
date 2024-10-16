from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QVBoxLayout, QDialog, QPushButton, QHeaderView, QHBoxLayout
from PyQt5.QtCore import Qt

from PyQt5.QtWidgets import QFileDialog, QMessageBox
import pandas as pd

class AssignmentResultWindow(QDialog):
    def __init__(self, assignment_results):
        super().__init__()
        
        # 창의 제목과 크기 설정
        self.setWindowTitle('배정 결과')
        self.setGeometry(300, 300, 1000, 600)  # 모달 창 크기 설정
        
        # 메인 레이아웃 (세로 방향)
        layout = QVBoxLayout(self)

        # 테이블 위젯 생성
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(5)  # 구분, 성명, 현재소속, 배정결과, 배정희망순위
        self.table_widget.setHorizontalHeaderLabels(['전보구분', '성명', '현재소속', '배정결과', '배정희망순위'])

        # 테이블 크기 설정
        self.table_widget.setMinimumWidth(950)  # 창에 맞춰 최소 가로 크기 설정
        self.table_widget.setMinimumHeight(550)  # 창에 맞춰 최소 세로 크기 설정

        # 헤더 크기를 창 크기에 맞게 확장
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)  # 가로 크기 조정

        # 테이블에 데이터 채우기
        self.populate_table(assignment_results)

        # 테이블을 가로로 중앙에 배치하기 위한 QHBoxLayout 사용
        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.table_widget)
        hbox.addStretch(1)

        # 레이아웃에 QHBoxLayout 추가
        layout.addLayout(hbox)

        # '배정 결과 다운로드' 버튼을 테이블 아래에 추가
        self.download_button = QPushButton('배정 결과 다운로드')
        self.download_button.clicked.connect(self.download_assignment_results)  # 버튼 클릭 시 엑셀로 다운로드
        layout.addWidget(self.download_button)  # 버튼을 마지막에 추가하여 아래로 배치
    
    def populate_table(self, assignment_results):
        self.table_widget.setRowCount(len(assignment_results))  # 배정된 인원의 수만큼 행 생성
        
        for row_idx, result in enumerate(assignment_results):
            # 각 열에 데이터를 넣음
            self.table_widget.setItem(row_idx, 0, QTableWidgetItem(result['전보구분']))
            self.table_widget.setItem(row_idx, 1, QTableWidgetItem(result['성명']))
            self.table_widget.setItem(row_idx, 2, QTableWidgetItem(result['현재소속']))
            self.table_widget.setItem(row_idx, 3, QTableWidgetItem(result['배정결과']))
            self.table_widget.setItem(row_idx, 4, QTableWidgetItem(result['배정희망순위']))

        # 내용에 맞게 열 크기를 조정
        self.table_widget.resizeColumnsToContents()
    
    # '배정 결과 다운로드' 버튼의 클릭 이벤트 함수
    def download_assignment_results(self):
        # 기본 파일명 설정
        default_filename = "배정_결과.xlsx"

        # 사용자가 파일 저장할 경로를 선택하는 파일 대화상자
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "엑셀 파일로 저장", default_filename, "Excel Files (*.xlsx);;All Files (*)", options=options)
        
        if file_path:
            try:
                # assignment_results.csv 파일을 엑셀 형식으로 변환하여 저장
                df = pd.read_csv('assignment_results.csv')  # CSV 파일을 읽기
                df.to_excel(file_path, index=False)  # 선택한 경로에 엑셀 파일로 저장
                QMessageBox.information(self, "성공", "배정 결과가 엑셀 파일로 저장되었습니다.")
            except Exception as e:
                QMessageBox.critical(self, "에러", f"엑셀 파일로 저장하는 중 오류가 발생했습니다: {str(e)}")
import sys
import os
import json
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QGridLayout, QPushButton, QMessageBox
from PyQt5.QtCore import Qt

# 현재 파일의 경로를 기준으로 상위 폴더를 sys.path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.append(parent_dir)

from department import department_names  # department.py에서 학교명 리스트 불러오기
from gui.data_uploader_gui import AssignmentProcessor

# JSON 파일 경로
JSON_FILE_PATH = 'vacancies.json'

# JSON 파일에서 데이터를 불러오는 함수
def load_from_json():
    if os.path.exists(JSON_FILE_PATH):
        with open(JSON_FILE_PATH, 'r', encoding='utf-8') as file:
            try:
                return json.load(file)  # JSON 데이터를 딕셔너리로 반환
            except json.JSONDecodeError:
                return {}
    return {}

# 입력한 데이터를 JSON 파일로 저장하는 함수
def save_to_json(vacancies):
    with open(JSON_FILE_PATH, 'w', encoding='utf-8') as file:
        json.dump(vacancies, file, ensure_ascii=False, indent=4)  # JSON 파일로 저장
    QMessageBox.information(None, "저장 완료", "빈자리 정보가 JSON 파일로 저장되었습니다.")


class VacancyInputGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('학교별 빈자리 입력')
        self.setGeometry(100, 100, 800, 600)

        # 그리드 레이아웃 설정
        layout = QGridLayout()

        # 빈자리 입력 필드 저장할 딕셔너리
        self.entry_fields = {}

        # JSON 파일에서 데이터 로드
        saved_vacancies = load_from_json()

        # department_names 리스트 사용
        for idx, department in enumerate(department_names):
            row = idx % 10
            col = idx // 10

            # 학교 앞에 번호를 붙여 표시
            label = QLabel(f"{idx+1}. {department}")
            entry = QLineEdit()

            # 텍스트박스의 가로 길이 조정 (100px로 설정)
            entry.setFixedWidth(80)

            # JSON에서 로드된 값이 있으면 입력 필드에 미리 채워넣음
            if department in saved_vacancies:
                entry.setText(str(saved_vacancies[department]))

            # 텍스트박스가 왼쪽으로 정렬되도록 설정
            entry.setAlignment(Qt.AlignCenter)

            layout.addWidget(label, row, col * 2)
            layout.addWidget(entry, row, col * 2 + 1)
            self.entry_fields[department] = entry

        # 제출 버튼
        submit_button = QPushButton('학교별 빈자리 저장하기')
        submit_button.clicked.connect(self.on_submit)
        layout.addWidget(submit_button, 10, 0, 1, 12)

        self.setLayout(layout)

    # 제출 버튼 클릭 시 처리
    def on_submit(self):
        vacancies = {}
        for department, entry in self.entry_fields.items():
            vacancy = entry.text()
            if vacancy == "":
                vacancy = 0  # 빈 입력 필드는 0으로 처리
            try:
                vacancies[department] = int(vacancy)
            except ValueError:
                QMessageBox.warning(self, "입력 오류", f"{department}의 빈자리 수는 숫자여야 합니다!")
                return

        # 제출 완료 메시지
        QMessageBox.information(self, "제출 완료", "빈자리 정보가 성공적으로 입력되었습니다.")
        
        # JSON으로 저장
        save_to_json(vacancies)

        # 새로운 창을 열기 전에 인스턴스 변수로 저장하여 창이 닫히지 않도록 함
        self.data_uploader = AssignmentProcessor()
        self.data_uploader.show()

        # 현재 창 닫기
        self.close()

def show_vacancies():
    app = QApplication(sys.argv)
    vacancy_window = VacancyInputGUI()
    vacancy_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    show_vacancies()
import sys
import os

# 현재 파일의 경로를 기준으로 상위 폴더를 sys.path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.append(parent_dir)

from gui.vacancy_input_gui import show_vacancies

show_vacancies()
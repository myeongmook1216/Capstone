import sys
import csv
import os
import re
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QLineEdit, QMessageBox, QListWidget, QTextEdit
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QProcess
import subprocess
import signal  # 프로세스 종료에 사용
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl
import requests

#------ 전역 변수 선언
eye_select_mode = None
# 0 왼 눈 , 1 오른 눈 2 양눈

# 자연 정렬을 위한 함수
def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]


# 메인 창
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('SST Application')
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()
        background_label = QLabel(self)
        pixmap = QPixmap('./image/sst.jpg').scaled(800, 600, Qt.KeepAspectRatio) 
        background_label.setPixmap(pixmap)

        button_layout = QVBoxLayout()
        button_record = QPushButton('기록')
        button_treat = QPushButton('치료')
        button_settings = QPushButton('사용법')
        button_exit = QPushButton('나가기')

        button_record.setFixedSize(250, 80)
        button_treat.setFixedSize(250, 80)
        button_settings.setFixedSize(250, 80)
        button_exit.setFixedSize(250, 80)

        button_record.clicked.connect(self.open_record_page)
        button_treat.clicked.connect(self.open_treat_page)
        button_settings.clicked.connect(self.open_settings_page)
        button_exit.clicked.connect(QApplication.quit)

        button_layout.addWidget(button_record, alignment=Qt.AlignCenter)
        button_layout.addWidget(button_treat, alignment=Qt.AlignCenter)
        button_layout.addWidget(button_settings, alignment=Qt.AlignCenter)
        button_layout.addWidget(button_exit, alignment=Qt.AlignCenter)

        layout.addWidget(background_label)
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def open_record_page(self):
        self.record_page = RecordPage()
        self.record_page.show()
        self.close()

    def open_treat_page(self):
        self.treat_window = TreatPage()
        self.treat_window.show()
        self.close()

    def open_settings_page(self):
        self.settings_window = GuideWindow()
        self.settings_window.show()
        self.close()

# 기록 페이지
class RecordPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('기록 페이지')
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()
        self.record_list = QListWidget()

        # 기록 예시
        records = ["기록 1: 사용자가 낱말 카드를 사용", "기록 2: 그림 책을 탐색"]
        self.record_list.addItems(records)

        layout.addWidget(self.record_list)

        back_button = QPushButton('← 메인으로')
        back_button.clicked.connect(self.go_back_to_main)
        layout.addWidget(back_button, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def go_back_to_main(self):
        self.main_window = MainWindow()
        self.main_window.show()
        self.close()

#환경설정
class GuideWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('사용법')
        self.setGeometry(100, 100, 1000, 600)

        layout = QVBoxLayout()

        # 버튼 추가
        button_layout = QHBoxLayout()
        record_button = QPushButton("캘리브레이션 튜토리얼")
        treatment_button = QPushButton("pdf 다운로드")
        calibration_button = QPushButton("카메라 캘리브레이션")

        record_button.setFixedSize(250, 80)
        treatment_button.setFixedSize(250, 80)
        calibration_button.setFixedSize(250, 80)

        record_button.clicked.connect(self.show_tutorial)
        treatment_button.clicked.connect(self.download_checkerboard)
        calibration_button.clicked.connect(self.do_camera_calibration)

        button_layout.addWidget(record_button)
        button_layout.addWidget(treatment_button)
        button_layout.addWidget(calibration_button)

        # 프로세스 출력 표시할 QTextEdit 생성
        self.process_output = QTextEdit()
        self.process_output.setReadOnly(True)  # 읽기 전용으로 설정
        layout.addWidget(self.process_output)

        main_button = QPushButton('← 메인으로')
        main_button.clicked.connect(self.go_back_to_main)
        button_layout.addWidget(main_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        # QProcess 객체 초기화
        self.process = None

    def show_tutorial(self):
        """기록 설명 페이지 표시"""
        record_guide_text = """
        <div style="text-align: center;">
        <h2><b>1단계: 카메라 캘리브레이션 수행</b></h2>
        <h3><b>1-1 체커보드 다운로드 및 준비</b></h3>
        <p>아래 <b>PDF 다운로드</b> 버튼을 클릭해 체커보드 이미지를 다운로드한 후, 인쇄합니다.<br>
        출력한 체커보드는 <b>평평한 표면에 고정</b>하여 사용합니다 (종이가 휘지 않도록 주의).</p>

        <h3><b>1-2 캘리브레이션 수행</b></h3>
        <p>카메라 캘리브레이션 버튼을 클릭합니다.<br>
        체커보드 이미지를 <b>다양한 각도와 거리</b>에서 카메라로 촬영합니다.<br>
        총 <b>15장의 이미지</b>를 촬영하여 캘리브레이션을 완료합니다.</p>

        <h3><b>캘리브레이션의 목적</b></h3>
        <p>이 과정은 <b>시선 추적의 정확도</b>를 높이기 위한 것입니다.<br>
        만약 이 과정을 건너뛴다면, 프로그램은 기본 설정값을 사용합니다.</p>

        <hr>

        <h2><b>2단계: 독서 및 한글 카드 읽기</b></h2>
        <h3><b>모드 선택</b></h3>
        <p>원하는 모드를 선택합니다:</p>
        <ul>
            <li><b>한 눈 모드</b></li>
            <li><b>양 눈 모드</b></li>
        </ul>

        <h3><b>활동 수행</b></h3>
        <p>낱말 카드 읽기 또는 동화책 읽기 활동을 시작합니다.</p><br><br><br>
        """
        self.process_output.setHtml(record_guide_text)  # QTextEdit에 텍스트 설정

    def download_checkerboard(self):
        """PDF 다운로드 메서드"""
        url = "https://drive.google.com/uc?export=download&id=1auBGMOv8Si5Zhj2pb6We0oz-PpPYlX75"
        local_filename = "체커보드_패턴.pdf"

        try:
            # PDF 다운로드 시작
            response = requests.get(url, stream=True)
            response.raise_for_status()  # 에러 발생 시 예외 처리

            # PDF 파일 저장
            with open(local_filename, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            # 다운로드 완료 메시지 출력
            self.process_output.append(f"{local_filename} 다운로드 완료.")
            QMessageBox.information(self, "완료", f"{local_filename}이(가) 다운로드되었습니다.")

        except requests.exceptions.RequestException as e:
            # 다운로드 실패 메시지 출력
            self.process_output.append("다운로드 실패.")
            QMessageBox.critical(self, "오류", f"PDF 다운로드 중 오류가 발생했습니다: {str(e)}")

    def do_camera_calibration(self):
        """카메라 캘리브레이션 진행"""
        try:
            self.process = QProcess(self)
            self.process.setProcessChannelMode(QProcess.MergedChannels)  # 표준 출력과 에러를 하나로 병합
            self.process.readyRead.connect(self.handle_stdout)  # 주기적으로 출력 읽기
            self.process.finished.connect(self.process_finished)

            command = (
                'source /Users/jeon-yewon/miniforge3/bin/activate mpii && '
                'python tools/get_calib_matrix.py'
            )

            # QProcess 시작
            self.process.start('bash', ['-c', command])

            self.process_pid = self.process.processId()
            self.process_output.append(f"프로세스가 시작되었습니다. (PID: {self.process_pid})")

        except Exception as e:
            self.process_output.append(f"Error: {e}")

    def handle_stdout(self):
        """표준 출력 처리"""
        data = self.process.readAllStandardOutput().data().decode('utf-8').strip()
        if data:
            self.process_output.append(data)
            self.process_output.ensureCursorVisible()

    def terminate_process(self):
        """프로세스 강제 종료"""
        if self.process and self.process.state() != QProcess.NotRunning:
            try:
                self.process.kill()
                self.process_output.append(f"프로세스가 종료되었습니다.")
            except Exception as e:
                self.process_output.append(f"프로세스 종료 오류: {e}")

    def process_finished(self):
        """프로세스 종료 시 호출"""
        self.process_output.append("[캘리브레이션 종료]")
        self.process = None

    def go_back_to_main(self):
        """메인 페이지로 이동"""
        self.main_window = MainWindow()
        self.main_window.show()
        if hasattr(self, 'image_page'):
            self.image_page.close()
        self.close()

class SubGuideWindow(QWidget):
    def __init__(self, title, description):
        super().__init__()

        self.setWindowTitle(title)
        self.setGeometry(100, 100, 1000, 600)

        layout = QVBoxLayout()

        # 메인 레이아웃: 왼쪽 설명 및 오른쪽 비디오
        main_layout = QHBoxLayout()

        # 왼쪽 레이아웃: 설명 텍스트와 튜토리얼 박스
        left_layout = QVBoxLayout()

        tutorial_label = QLabel("Tutorial (안내영상)")
        tutorial_label.setStyleSheet(
            "font-size: 20px; font-weight: bold; background-color: #FFEBB5;"
            "padding: 10px; border-radius: 10px; border: 2px solid black;"
        )
        tutorial_label.setAlignment(Qt.AlignCenter)
        tutorial_label.setFixedSize(300, 50)

        description_label = QLabel(description)
        description_label.setWordWrap(True)
        description_label.setAlignment(Qt.AlignCenter)
        description_label.setStyleSheet("font-size: 16px; padding: 20px;")

        # 위와 아래에 여유 공간 추가하여 중앙 정렬
        left_layout.addStretch()  
        left_layout.addWidget(tutorial_label, alignment=Qt.AlignCenter)
        left_layout.addWidget(description_label, alignment=Qt.AlignCenter)
        left_layout.addStretch()  

        # 오른쪽 레이아웃: 비디오 재생 위젯
        right_layout = QVBoxLayout()

        video_widget = QVideoWidget()
        self.player = QMediaPlayer()
        self.player.setVideoOutput(video_widget)

        video_path = QUrl.fromLocalFile('./이미지/test.mp4')
        self.player.setMedia(QMediaContent(video_path))

        right_layout.addWidget(video_widget)

        play_button = QPushButton('Play Video')
        play_button.setStyleSheet("font-size: 18px; padding: 5px;")
        play_button.clicked.connect(self.player.play)
        right_layout.addWidget(play_button, alignment=Qt.AlignCenter)

        # 메인 레이아웃 구성
        main_layout.addLayout(left_layout, stretch=1)
        main_layout.addLayout(right_layout, stretch=2)

        layout.addLayout(main_layout)

        # 하단 네비게이션 버튼
        nav_layout = QHBoxLayout()
        back_button = QPushButton("← 설명으로")
        back_button.setFixedSize(120, 40)
        back_button.clicked.connect(self.go_back_to_guide)

        main_button = QPushButton("← 메인으로")
        main_button.setFixedSize(120, 40)
        main_button.clicked.connect(self.go_back_to_main)

        nav_layout.addStretch()  
        nav_layout.addWidget(back_button)
        nav_layout.addWidget(main_button)
        nav_layout.addStretch()

        layout.addLayout(nav_layout)

        self.setLayout(layout)

    def go_back_to_guide(self):
        """사용법 메인 페이지로 돌아가기"""
        self.guide_window = GuideWindow()
        self.guide_window.show()
        self.close()

    def go_back_to_main(self):
        """메인 페이지로 돌아가기"""
        self.main_window = MainWindow()
        self.main_window.show()
        self.close()

# 치료 페이지
class TreatPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('치료 선택')
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        # 이미지와 버튼을 담는 위젯 생성
        overlay_widget = QWidget()
        overlay_layout = QVBoxLayout(overlay_widget)

        button_layout = QHBoxLayout()  # 버튼과 이미지를 정렬할 레이아웃

        # '왼쪽 눈' 버튼과 이미지
        left_eye_label = QLabel(self)
        left_eye_pixmap = QPixmap('./이미지/left_eye.png')  # 왼쪽 눈 이미지 경로 설정
        left_eye_label.setPixmap(left_eye_pixmap.scaled(150, 150, Qt.KeepAspectRatio))

        left_eye_button = QPushButton('왼쪽 눈')
        left_eye_button.setStyleSheet("font-size: 20px;")
        left_eye_button.setFixedSize(200, 80)
        left_eye_button.clicked.connect(self.open_left_eye_selection)  # 수정된 부분

        # '오른쪽 눈' 버튼과 이미지
        right_eye_label = QLabel(self)
        right_eye_pixmap = QPixmap('./이미지/right_eye.png')  # 오른쪽 눈 이미지 경로 설정
        right_eye_label.setPixmap(right_eye_pixmap.scaled(150, 150, Qt.KeepAspectRatio))

        right_eye_button = QPushButton('오른쪽 눈')
        right_eye_button.setStyleSheet("font-size: 20px;")
        right_eye_button.setFixedSize(200, 80)
        right_eye_button.clicked.connect(self.open_right_eye_selection)  # 수정된 부분

        # '양쪽 눈' 버튼과 이미지
        both_eyes_label = QLabel(self)
        both_eyes_pixmap = QPixmap('./이미지/both_eyes.png')  # 양쪽 눈 이미지 경로 설정
        both_eyes_label.setPixmap(both_eyes_pixmap.scaled(150, 150, Qt.KeepAspectRatio))

        both_eyes_button = QPushButton('양쪽 눈')
        both_eyes_button.setStyleSheet("font-size: 20px;")
        both_eyes_button.setFixedSize(200, 80)
        both_eyes_button.clicked.connect(self.open_both_eyes_selection)

        # 버튼과 이미지를 레이아웃에 추가
        button_layout.addWidget(left_eye_label)
        button_layout.addWidget(left_eye_button)
        button_layout.addWidget(right_eye_label)
        button_layout.addWidget(right_eye_button)
        button_layout.addWidget(both_eyes_label)
        button_layout.addWidget(both_eyes_button)

        # '이전으로', '메인으로' 버튼 추가
        navigation_layout = QHBoxLayout()
        back_button = QPushButton('← 이전으로')
        back_button.setStyleSheet("font-size: 18px;")
        back_button.clicked.connect(self.go_back_to_main)

        main_button = QPushButton('← 메인으로')
        main_button.setStyleSheet("font-size: 18px;")
        main_button.clicked.connect(self.go_back_to_main)

        navigation_layout.addWidget(back_button)
        navigation_layout.addWidget(main_button)

        # 레이아웃 구성
        overlay_layout.addStretch()
        overlay_layout.addLayout(button_layout)
        overlay_layout.addLayout(navigation_layout)
        overlay_layout.addStretch()

        layout.addWidget(overlay_widget)
        self.setLayout(layout)

    def open_left_eye_selection(self):
        """왼쪽 눈 선택 시 실행"""
        global eye_select_mode
        eye_select_mode = 0
        self.selection_page = SelectionPage('왼쪽 눈')
        self.selection_page.show()
        self.close()

    def open_right_eye_selection(self):
        """오른쪽 눈 선택 시 실행"""
        global eye_select_mode
        eye_select_mode = 1
        self.selection_page = SelectionPage('오른쪽 눈')
        self.selection_page.show()
        self.close()

    def open_both_eyes_selection(self):
        """양쪽 눈 선택 시 실행"""
        global eye_select_mode
        eye_select_mode = 2
        self.selection_page = SelectionPage('양쪽 눈')
        self.selection_page.show()
        self.close()

    def go_back_to_main(self):
        """메인 페이지로 이동"""
        self.main_window = MainWindow()
        self.main_window.show()
        self.close()

# 눈 개수 선택 후 낱말/그림
class SelectionPage(QWidget):
    def __init__(self, eye_type):
        super().__init__()
        self.eye_type = eye_type
        self.setWindowTitle(f'{self.eye_type} - 낱말/그림 선택')
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()
        word_button = QPushButton('낱말 카드')
        picture_button = QPushButton('그림 카드')

        word_button.setFixedSize(200, 80)
        picture_button.setFixedSize(200, 80)

        word_button.clicked.connect(self.open_word_card_page)
        picture_button.clicked.connect(self.open_picture_book_page)

        layout.addWidget(word_button, alignment=Qt.AlignCenter)
        layout.addWidget(picture_button, alignment=Qt.AlignCenter)

        # '이전으로', '메인으로' 버튼 추가
        button_layout = QHBoxLayout()
        back_button = QPushButton('← 이전으로')
        back_button.clicked.connect(self.go_back_to_treat)
        button_layout.addWidget(back_button)

        main_button = QPushButton('← 메인으로')
        main_button.clicked.connect(self.go_back_to_main)
        button_layout.addWidget(main_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def open_word_card_page(self):
        self.card_selection_page = CardSelectionPage(self.eye_type)
        self.card_selection_page.show()
        self.close()

    def open_picture_book_page(self):
        self.picture_book_page = PicturebookPage(self.eye_type)
        self.picture_book_page.show()
        self.close()

    def go_back_to_treat(self):
        """치료 페이지로 이동"""
        self.treat_page = TreatPage()
        self.treat_page.show()
        self.close()

    def go_back_to_main(self):
        """메인 페이지로 이동"""
        self.main_window = MainWindow()
        self.main_window.show()
        self.close()

# 이미지 페이지
class ImagePage(QWidget):
    def __init__(self, folder_path):
        super().__init__()
        self.setWindowTitle("동화책 이미지")
        self.setGeometry(100, 100, 800, 600)

        self.folder_path = folder_path
        self.image_files = sorted(
            [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))],
            key=natural_sort_key
        )
        self.image_index = 0

        layout = QVBoxLayout()

        # 이미지 표시용 QLabel 생성
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.load_image(self.image_index)

        # 이전/다음 버튼 및 메인 메뉴로 이동 버튼
        prev_button = QPushButton("이전 그림")
        prev_button.clicked.connect(self.prev_image)

        next_button = QPushButton("다음 그림")
        next_button.clicked.connect(self.next_image)

        back_button = QPushButton("← 메인메뉴로")
        back_button.clicked.connect(self.go_back_to_main)

        # 버튼 정렬
        button_layout = QHBoxLayout()
        button_layout.addWidget(prev_button)
        button_layout.addWidget(back_button)
        button_layout.addWidget(next_button)

        layout.addWidget(self.image_label)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def load_image(self, index):
        """지정된 인덱스의 이미지를 로드"""
        if 0 <= index < len(self.image_files):
            pixmap = QPixmap(os.path.join(self.folder_path, self.image_files[index]))
            self.image_label.setPixmap(pixmap)
            self.image_label.setScaledContents(True)

    def next_image(self):
        """다음 이미지로 이동"""
        if self.image_index < len(self.image_files) - 1:
            self.image_index += 1
            self.load_image(self.image_index)

    def prev_image(self):
        """이전 이미지로 이동"""
        if self.image_index > 0:
            self.image_index -= 1
            self.load_image(self.image_index)

    def go_back_to_main(self):
        """메인 페이지로 이동"""
        self.main_window = MainWindow()
        self.main_window.show()
        self.close()

#동화책
class PicturebookPage(QWidget):
    def __init__(self, eye_type):
        super().__init__()
        self.setWindowTitle(f'{eye_type} - 동화책 선택')
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        # 폴더 목록 표시할 QListWidget 생성
        folder_path = "./books"
        self.folder_list = QListWidget()

        if os.path.exists(folder_path):
            subfolders = [f.name for f in os.scandir(folder_path) if f.is_dir()]
            self.folder_list.addItems(subfolders)
        else:
            self.folder_list.addItem("폴더를 찾을 수 없습니다.")

        # 폴더 선택 시 이벤트 연결
        self.folder_list.itemDoubleClicked.connect(self.folder_selected)
        layout.addWidget(self.folder_list)

        # 프로세스 출력 표시용 QTextEdit 초기화
        self.process_output = QTextEdit()
        self.process_output.setReadOnly(True)  # 읽기 전용으로 설정
        layout.addWidget(self.process_output)

        # 버튼 생성 및 배치
        button_layout = QHBoxLayout()

        back_button = QPushButton('← 이전으로')
        back_button.clicked.connect(self.go_back_to_selection)
        button_layout.addWidget(back_button)

        main_button = QPushButton('← 메인으로')
        main_button.clicked.connect(self.go_back_to_main)
        button_layout.addWidget(main_button)


        layout.addLayout(button_layout)
        self.setLayout(layout)

        # 프로세스 객체 초기화
        self.process = None

    def folder_selected(self):
        """선택된 폴더에 따라 프로세스 실행"""
        selected_folder = self.folder_list.currentItem().text()

        folder_mapping = {
            'hand': 'hand',
            'imhere': 'imhere',
            'moon': 'moon',
            'shoes': 'shoes',
            'smile': 'smile',
            'ssak': 'ssak'
        }

        custom_param_value = folder_mapping.get(selected_folder)

        if not custom_param_value:
            self.process_output.append("Invalid folder selected.")
            return

        # 프로세스 시작
        self.start_process(custom_param_value)

    def start_process(self, custom_param_value):
        """프로세스 시작"""
        try:
            self.process = QProcess(self)
            self.process.readyReadStandardOutput.connect(self.handle_stdout)
            self.process.readyReadStandardError.connect(self.handle_stderr)
            self.process.finished.connect(self.process_finished)

            command = (
                'source /Users/jeon-yewon/miniforge3/bin/activate mpii && '
                f'python point_2_screen_mac.py --config configs/demo_mpiigaze_resnet.yaml --demo 1 '
                f'--custom_param {custom_param_value} '
                f'--eye_select_mode {eye_select_mode}'
            )
            self.process.start('bash', ['-c', command])

            self.process_pid = self.process.processId()
            self.process_output.append(f"프로세스가 시작되었습니다. (PID: {self.process_pid})")

        except Exception as e:
            self.process_output.append(f"Error executing script: {e}")

    def terminate_process(self):
        """프로세스 강제 종료"""
        if hasattr(self, 'process_pid') and self.process_pid:
            try:
                os.kill(self.process_pid, signal.SIGKILL)
                self.process_output.append(f"프로세스 (PID: {self.process_pid})가 종료되었습니다.")
                self.process_pid = None
            except Exception as e:
                self.process_output.append(f"프로세스 종료 오류: {e}")
        else:
            self.process_output.append("실행 중인 프로세스가 없습니다.")

    def handle_stdout(self):
        """표준 출력 처리"""
        data = self.process.readAllStandardOutput().data().decode()
        self.process_output.append(data)

    def handle_stderr(self):
        """표준 에러 처리"""
        data = self.process.readAllStandardError().data().decode()
        self.process_output.append(f"Error: {data}")

    def process_finished(self):
        """프로세스 종료 시 호출"""
        self.process_output.append("[프로세스 종료]")
        self.process = None

    def go_back_to_selection(self):
        """이전 선택 페이지로 이동"""
        self.selection_page = SelectionPage('한쪽 눈' if '한쪽' in self.windowTitle() else '양쪽 눈')
        self.selection_page.show()
        self.close()

    def go_back_to_main(self):
        """메인 페이지로 이동"""
        self.main_window = MainWindow()
        self.main_window.show()
        self.close()

    def go_back_to_treat(self):
        """치료 페이지로 이동"""
        self.treat_window = TreatPage()
        self.treat_window.show()
        self.close()

# 낱말카드
class CardSelectionPage(QWidget):
    def __init__(self, eye_type):
        super().__init__()
        self.setWindowTitle(f'{eye_type} - 한글 카드 선택')
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        self.card_list = QListWidget()

        # 폴더 목록 표시할 QListWidget 생성
        folder_path = "./cards"
        self.folder_list = QListWidget()

        if os.path.exists(folder_path):
            subfolders = [f.name for f in os.scandir(folder_path) if f.is_dir()]
            self.folder_list.addItems(subfolders)
        else:
            self.folder_list.addItem("폴더를 찾을 수 없습니다.")

        # 폴더 더블 클릭 시 이벤트 연결
        self.folder_list.itemDoubleClicked.connect(self.folder_selected)
        layout.addWidget(self.folder_list)

        # 프로세스 출력 표시할 QTextEdit 생성
        self.process_output = QTextEdit()
        self.process_output.setReadOnly(True)  # 읽기 전용으로 설정
        layout.addWidget(self.process_output)

        # 이전으로 / 메인으로 버튼 생성
        button_layout = QHBoxLayout()

        back_button = QPushButton('← 이전으로')
        back_button.clicked.connect(self.go_back_to_treat)
        button_layout.addWidget(back_button)

        main_button = QPushButton('← 메인으로')
        main_button.clicked.connect(self.go_back_to_main)
        button_layout.addWidget(main_button)


        layout.addLayout(button_layout)
        self.setLayout(layout)

        # 프로세스 객체 초기화
        self.process = None

    def open_image_page(self, folder_path):
        """선택한 카드의 이미지 페이지를 여는 메소드"""
        self.image_page = QWidget()
        self.image_page.setWindowTitle("낱말 카드 이미지")
        self.image_page.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        # 해당 폴더의 이미지 파일 로딩
        image_files = [
            f for f in os.listdir(folder_path) 
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))
        ]
        self.image_index = 0

        # 두 개의 이미지 라벨 생성
        self.left_image_label = QLabel(self.image_page)
        self.right_image_label = QLabel(self.image_page)
        self.left_image_label.setAlignment(Qt.AlignCenter)
        self.right_image_label.setAlignment(Qt.AlignCenter)

        self.load_images(folder_path, self.image_index, image_files)

        # 이전/다음 및 메인 메뉴 버튼 생성
        prev_button = QPushButton("이전 그림")
        prev_button.clicked.connect(lambda: self.prev_images(folder_path, image_files))

        next_button = QPushButton("다음 그림")
        next_button.clicked.connect(lambda: self.next_images(folder_path, image_files))

        back_button = QPushButton("← 메인으로")
        back_button.clicked.connect(self.go_back_to_main)

        # 버튼 레이아웃 설정
        button_layout = QHBoxLayout()
        button_layout.addWidget(prev_button)
        button_layout.addWidget(back_button)
        button_layout.addWidget(next_button)

        # 이미지 및 버튼 레이아웃 구성
        image_layout = QHBoxLayout()
        image_layout.addWidget(self.left_image_label)
        image_layout.addWidget(self.right_image_label)

        layout.addLayout(image_layout)
        layout.addLayout(button_layout)

        self.image_page.setLayout(layout)
        self.image_page.showFullScreen()
        self.close()

    def load_images(self, folder_path, index, image_files):
        """지정된 인덱스에 해당하는 이미지를 로드하는 메소드"""
        screen_geometry = QApplication.primaryScreen().geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        if 0 <= index < len(image_files):
            left_pixmap = QPixmap(os.path.join(folder_path, image_files[index]))
            scaled_left_pixmap = left_pixmap.scaled(screen_width * 0.42, screen_height * 0.85, Qt.KeepAspectRatio)
            self.left_image_label.setPixmap(scaled_left_pixmap)

        if index + 1 < len(image_files):
            right_pixmap = QPixmap(os.path.join(folder_path, image_files[index + 1]))
            scaled_right_pixmap = right_pixmap.scaled(screen_width * 0.42, screen_height * 0.85, Qt.KeepAspectRatio)
            self.right_image_label.setPixmap(scaled_right_pixmap)
        else:
            self.right_image_label.clear()

    def next_images(self, folder_path, image_files):
        """다음 두 개의 이미지를 로드"""
        if self.image_index < len(image_files) - 2:
            self.image_index += 2
            self.load_images(folder_path, self.image_index, image_files)

    def prev_images(self, folder_path, image_files):
        """이전 두 개의 이미지를 로드"""
        if self.image_index > 0:
            self.image_index -= 2
            self.load_images(folder_path, self.image_index, image_files)

    def go_back_to_selection(self):
        """이전 선택 페이지로 돌아가기"""
        self.selection_page = SelectionPage('한쪽 눈' if '한쪽' in self.windowTitle() else '양쪽 눈')
        self.selection_page.show()
        self.close()

    def go_back_to_main(self):
        """메인 페이지로 이동"""
        self.main_window = MainWindow()
        self.main_window.show()
        if hasattr(self, 'image_page'):
            self.image_page.close()
        self.close()

    def folder_selected(self):
        selected_folder = self.folder_list.currentItem().text()

        if selected_folder == 'animal':
            custom_param_value = 'animal'
        elif selected_folder == 'job':
            custom_param_value = 'job'
        elif selected_folder == 'vegitable':
            custom_param_value = 'vegitable'
        elif selected_folder == 'vehicle':
            custom_param_value = 'vehicle'

        else:
            self.process_output.append("Invalid folder selected.")
            return  # 유효하지 않은 폴더가 선택된 경우 종료

        # 프로세스 시작 함수 호출
        self.start_process(custom_param_value)

    def start_process(self, custom_param_value):
        try:
            # QProcess를 사용해 스크립트를 애플리케이션 내부에서 실행
            self.process = QProcess(self)
            self.process.readyReadStandardOutput.connect(self.handle_stdout)
            self.process.readyReadStandardError.connect(self.handle_stderr)
            self.process.finished.connect(self.process_finished)

            command = (
                'source /Users/jeon-yewon/miniforge3/bin/activate mpii && '
                f'python point_2_screen_mac.py --config configs/demo_mpiigaze_resnet.yaml --demo 1 '
                f'--custom_param {custom_param_value} '
                f'--eye_select_mode {eye_select_mode}'
            )

            self.process.start('bash', ['-c', command])

            # PID 추적
            self.process_pid = self.process.processId()
            self.process_output.append(f"프로세스가 시작되었습니다. (PID: {self.process_pid})")

        except Exception as e:
            self.process_output.append(f"Error executing script: {e}")
        

    def terminate_process(self):
        """서브프로세스 강제 종료 메소드"""
        if hasattr(self, 'process_pid') and self.process_pid:
            try:
                os.kill(self.process_pid, signal.SIGKILL)  # 프로세스 강제 종료
                self.process_output.append(f"프로세스 (PID: {self.process_pid})가 종료되었습니다.")
                self.process_pid = None  # PID 초기화
            except Exception as e:
                self.process_output.append(f"프로세스 종료 오류: {e}")
        else:
            self.process_output.append("실행 중인 프로세스가 없습니다.")

    def handle_stdout(self):
        """표준 출력 처리"""
        data = self.process.readAllStandardOutput().data().decode()
        self.process_output.append(data)

    def handle_stderr(self):
        """표준 에러 처리"""
        data = self.process.readAllStandardError().data().decode()
        self.process_output.append(f"Error: {data}")

    def process_finished(self):
        """프로세스 종료 시 호출"""
        self.process_output.append("[프로세스 종료]")
        self.process = None  # 종료된 프로세스 객체 초기화

    def show_images(self, folder_path):
        """폴더 내 이미지 표시하는 메소드"""
        pass  # 필요에 따라 기존 show_images 코드 사용

    def go_back_to_main(self):
        """메인 페이지로 이동"""
        self.main_window = MainWindow()
        self.main_window.show()
        self.close()

    def go_back_to_treat(self):
        """치료 페이지로 이동"""
        self.treat_window = TreatPage()
        self.treat_window.show()
        self.close()

# 애플리케이션 실행
if __name__ == '__main__':
    app = QApplication(sys.argv)

    main_window = MainWindow()
    main_window.show()

    '''
    login_window = LoginWindow()
    login_window.show()
    '''

    sys.exit(app.exec_())

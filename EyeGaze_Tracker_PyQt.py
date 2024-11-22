from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel,
    QLineEdit, QMessageBox, QScrollArea, QListWidget, QStackedWidget, QGridLayout, QApplication
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt, QProcess
import csv
import requests
import os
import re
import sys


#------ 전역 변수 선언
eye_select_mode = None
# 0 왼 눈 , 1 오른 눈 2 양눈

# 자연 정렬을 위한 함수
def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

def download_file(filename, output_widget):
    """파일을 다운로드하고 결과를 QTextEdit 위젯에 출력하는 함수"""
    url = "https://drive.google.com/uc?export=download&id=1auBGMOv8Si5Zhj2pb6We0oz-PpPYlX75"
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # 다운로드 중 오류 발생 시 예외 처리
        with open(filename, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        output_widget.append(f"{filename} 다운로드 완료.")
    except requests.RequestException as e:
        output_widget.append(f"다운로드 실패: {e}")

# 로그인 / 회원가입
class LoginWindow(QWidget):
    """Login Window for the SST Application."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle('SST Application - 로그인')
        self.setGeometry(100, 100, 300, 200)

        layout = QVBoxLayout()

        self.label_id = QLabel('ID:')
        self.input_id = QLineEdit()
        layout.addWidget(self.label_id)
        layout.addWidget(self.input_id)

        self.label_pw = QLabel('PW:')
        self.input_pw = QLineEdit()
        self.input_pw.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.label_pw)
        layout.addWidget(self.input_pw)

        self.button_login = QPushButton('로그인')
        self.button_login.clicked.connect(self.check_login)
        layout.addWidget(self.button_login)

        self.button_signup = QPushButton('회원가입')
        self.button_signup.clicked.connect(self.open_signup_window)
        layout.addWidget(self.button_signup)

        self.setLayout(layout)

    def check_login(self):
        """Verify user credentials and handle login."""
        user_id = self.input_id.text()
        user_pw = self.input_pw.text()
        user_found = False

        try:
            with open('./users.csv', mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['ID'] == user_id and row['PW'] == user_pw:
                        user_found = True
                        if row['tutorial_shown'] == 'False':
                            self.open_tutorial_window(user_id)
                        else:
                            self.open_main_window()
                        return
            if not user_found:
                QMessageBox.warning(self, '로그인 실패', 'ID 또는 PW가 일치하지 않습니다.')
        except FileNotFoundError:
            QMessageBox.warning(self, '오류', '사용자 파일을 찾을 수 없습니다.')

    def open_signup_window(self):
        """Open the Signup Window."""
        self.signup_window = SignupWindow()
        self.signup_window.show()

    def open_main_window(self):
        """Open the Main Application Window."""
        self.main_window = MainWindow()
        self.main_window.show()
        self.close()

    def open_tutorial_window(self, user_id):
        """Open the Tutorial Window and mark it as shown."""
        self.tutorial_window = TutorialWindow()
        self.tutorial_window.show()
        self.update_tutorial_shown(user_id)
        self.close()

    def update_tutorial_shown(self, user_id):
        """Mark the tutorial as shown for the user in `users.csv`."""
        rows = []
        with open('./users.csv', mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['ID'] == user_id:
                    row['tutorial_shown'] = 'True'
                rows.append(row)
        with open('./users.csv', mode='w', newline='') as file:
            fieldnames = ['ID', 'PW', 'tutorial_shown']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

class SignupWindow(QWidget):
    """Signup Window for new users."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("회원가입")
        self.setGeometry(100, 100, 300, 200)

        layout = QVBoxLayout()

        self.label_id = QLabel("ID:")
        self.input_id = QLineEdit()
        layout.addWidget(self.label_id)
        layout.addWidget(self.input_id)

        self.label_pw = QLabel("PW:")
        self.input_pw = QLineEdit()
        self.input_pw.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.label_pw)
        layout.addWidget(self.input_pw)

        self.button_signup = QPushButton("회원가입")
        self.button_signup.clicked.connect(self.signup)
        layout.addWidget(self.button_signup)

        self.setLayout(layout)

    def signup(self):
        """Register a new user."""
        user_id = self.input_id.text()
        user_pw = self.input_pw.text()

        try:
            with open('./users.csv', mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([user_id, user_pw, "False"])
            QMessageBox.information(self, "회원가입 성공", "회원가입이 완료되었습니다!")
            self.close()
        except Exception as e:
            QMessageBox.warning(self, "오류", f"회원가입 중 오류가 발생했습니다: {e}")


# 튜토리얼
class TutorialWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SST 튜토리얼")
        self.setGeometry(100, 100, 1000, 600)
        self.setStyleSheet("background-color: white;")

        # 메인 레이아웃
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # 상단 고정 영역 (안내 메시지 및 건너뛰기 버튼)
        self.setup_top_section(main_layout)

        # 스크롤 가능한 튜토리얼 콘텐츠 영역
        self.setup_content_section(main_layout)

        # 하단 고정 영역 (이전, 다음 버튼)
        self.setup_bottom_section(main_layout)

        # 튜토리얼 단계 정보 및 초기 화면 설정
        self.steps = self.get_tutorial_steps()
        self.current_step = 0
        self.update_step()

    def setup_top_section(self, layout):
        """상단 안내 메시지 및 건너뛰기 버튼 설정"""
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)

        label = QLabel("SST에 오신 것을 환영합니다! 사용법을 안내해드립니다.")
        label.setFont(QFont("Arial", 22, QFont.Bold))
        label.setAlignment(Qt.AlignCenter)
        top_layout.addWidget(label)

        skip_button = QPushButton("건너뛰기")
        skip_button.setFixedSize(100, 40)
        skip_button.setStyleSheet("font-size: 14px; padding: 5px; background-color: #4CAF50; color: white;")
        skip_button.clicked.connect(self.skip_tutorial)
        top_layout.addWidget(skip_button, alignment=Qt.AlignCenter)

        layout.addWidget(top_widget)

    def setup_content_section(self, layout):
        """스크롤 가능한 튜토리얼 콘텐츠 설정"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        content_widget = QWidget()
        scroll_area.setWidget(content_widget)

        self.content_layout = QVBoxLayout(content_widget)

        # 이미지 및 텍스트 라벨 설정
        self.single_image_label = QLabel(alignment=Qt.AlignCenter)
        self.image_label_1 = QLabel(alignment=Qt.AlignCenter)
        self.image_label_2 = QLabel(alignment=Qt.AlignCenter)
        
        self.image_layout = QHBoxLayout()
        self.image_layout.addWidget(self.image_label_1)
        self.image_layout.addWidget(self.image_label_2)
        
        self.text_label = QLabel(alignment=Qt.AlignCenter)
        self.text_label.setFont(QFont("Arial", 20))

        # 콘텐츠 레이아웃에 이미지 및 설명 추가
        self.content_layout.addWidget(self.single_image_label)
        self.content_layout.addLayout(self.image_layout)
        self.content_layout.addWidget(self.text_label)

        layout.addWidget(scroll_area)

    def setup_bottom_section(self, layout):
        """하단 이전, 다음 버튼 설정"""
        bottom_widget = QWidget()
        bottom_layout = QHBoxLayout(bottom_widget)

        self.prev_button = QPushButton("이전으로")
        self.prev_button.clicked.connect(self.go_prev)

        self.next_button = QPushButton("다음으로")
        self.next_button.clicked.connect(self.go_next)

        bottom_layout.addWidget(self.prev_button)
        bottom_layout.addWidget(self.next_button)
        layout.addWidget(bottom_widget)

    def get_tutorial_steps(self):
        """튜토리얼 단계 정보 정의"""
        return [
            {"image": "./image/그림1.png", "text": "1. 처음 접속할 때 보게 될 페이지입니다."},
            {"image": "./image/그림2.png", "text": "2. 우선 시선을 추적하는 정확도를 향상시키기 위해 '캘리브레이션' 버튼을 선택해주세요.(선택사항)"},
            {"images": ["./image/그림4-1.png", "./image/그림4-2.png"], "text": "3. 캘리브레이션 진행을 위해 '캘리브레이션 설명' 버튼을 클릭하고, 안내를 확인해 주세요.\n 이후 PDF 다운 버튼을 클릭하여 이미지를 저장해줍니다."},
            {"images": ["./image/그림5-1.png", "./image/그림5-2.png"], "text": "4. 안내사항을 참고하여 카메라 캘리브레이션을 진행해 주세요."},
            {"image": "./image/그림6.png", "text": "5. 이제 메인 페이지로 돌아가 '치료' 버튼을 클릭해 주세요."},
            {"images": ["./image/그림7-1.png", "./image/그림7-2.png"], "text": "6. 원하는 안구와 테마를 선택해 주세요."},
            {"images": ["./image/그림8-1.png", "./image/그림8-2.png"], "text": "7. 주제를 더블 클릭하면 치료가 시작됩니다."},
            {"images": ["./image/그림9-1.png", "./image/그림9-2.png"], "text": "8. 표시되어 있는 네모박스 안에 빨간점(시선값)이 들어가게 되면, 다음 박스가 생성됩니다."},
            {"images": ["./image/그림10-1.png", "./image/그림10-2.png"], "text": "9. 페이지의 마지막 네모박스로 도달하게 되면 다음 페이지로 넘어가게 됩니다."},
            {"images": ["./image/그림11-1.png", "./image/그림11-2.png"], "text": "10. 마지막 페이지, 마지막 네모박스에 도달하면 메인 페이지로 되돌아갑니다. <br><font color='blue'><b>이제 치료를 시작해 보세요!</b></font>"}
        ]

    def update_step(self):
        """현재 단계에 맞는 이미지와 텍스트 업데이트"""
        step = self.steps[self.current_step]
        is_double_image = "images" in step

        if is_double_image:
            size = (400, 250) if self.current_step in [7, 8] else (500, 300)
            pixmap1 = QPixmap(step["images"][0]).scaled(*size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            pixmap2 = QPixmap(step["images"][1]).scaled(*size, Qt.KeepAspectRatio, Qt.SmoothTransformation)

            self.image_label_1.setPixmap(pixmap1)
            self.image_label_2.setPixmap(pixmap2)
            self.single_image_label.hide()
            self.image_label_1.show()
            self.image_label_2.show()
        else:
            pixmap = QPixmap(step["image"]).scaled(500, 350, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.single_image_label.setPixmap(pixmap)
            self.image_label_1.hide()
            self.image_label_2.hide()
            self.single_image_label.show()

        self.text_label.setText(step["text"])
        self.prev_button.setEnabled(self.current_step > 0)
        self.next_button.setText("시작하기" if self.current_step == len(self.steps) - 1 else "다음으로")

    def go_next(self):
        """다음 단계로 이동"""
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self.update_step()
        elif self.current_step == len(self.steps) - 1:
            self.start_app()

    def go_prev(self):
        """이전 단계로 이동"""
        if self.current_step > 0:
            self.current_step -= 1
            self.update_step()

    def start_app(self):
        """튜토리얼 종료 후 메인 페이지로 이동"""
        from sst_main_window import MainWindow
        self.main_window = MainWindow()
        self.main_window.show()
        self.close()

    def skip_tutorial(self):
        """튜토리얼 건너뛰기"""
        self.start_app()


# 메인 창
class MainWindow(QWidget):
    """Main Application Window."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle('SST Application')
        self.setGeometry(100, 100, 1000, 600)

        self.setStyleSheet("background-color: white;")

        main_layout = QVBoxLayout(self)

        background_label = QLabel(self)
        pixmap = QPixmap('./image/sst.jpg')  # Background image path
        background_label.setPixmap(pixmap.scaled(600, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        background_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(background_label)

        button_style = """
            QPushButton {
                background-color: transparent;
                color: black;
                font-weight: bold;
                font-size: 16px;
                border: 2px solid black;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """

        button_calibration = QPushButton('캘리브레이션')
        button_calibration.setFixedSize(150, 50)
        button_calibration.setStyleSheet(button_style)
        button_calibration.clicked.connect(self.open_settings_page)

        button_treat = QPushButton('치료')
        button_treat.setFixedSize(150, 50)
        button_treat.setStyleSheet(button_style)
        button_treat.clicked.connect(self.open_treat_page)

        button_tutorial = QPushButton('튜토리얼 다시 보기')
        button_tutorial.setFixedSize(150, 50)
        button_tutorial.setStyleSheet(button_style)
        button_tutorial.clicked.connect(self.open_tutorial_window)

        button_exit = QPushButton('나가기')
        button_exit.setFixedSize(150, 50)
        button_exit.setStyleSheet(button_style)
        button_exit.clicked.connect(QApplication.quit)

        button_grid = QGridLayout()
        button_grid.setSpacing(20)
        button_grid.addWidget(button_treat, 0, 0)
        button_grid.addWidget(button_calibration, 0, 1)
        button_grid.addWidget(button_tutorial, 1, 0)
        button_grid.addWidget(button_exit, 1, 1)

        button_widget = QWidget(self)
        button_widget.setLayout(button_grid)
        main_layout.addWidget(button_widget)
        main_layout.setAlignment(Qt.AlignCenter)

    def open_treat_page(self):
        """Open the treatment page."""
        self.treat_window = TreatPage()
        self.treat_window.show()
        self.close()

    def open_settings_page(self):
        """Open the settings page."""
        self.settings_window = GuideWindow()
        self.settings_window.show()
        self.close()

    def open_tutorial_window(self):
        """Reopen the tutorial window."""
        self.tutorial_window = TutorialWindow()
        self.tutorial_window.show()


#환경설정
class GuideWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Window 기본 설정
        self.setWindowTitle('사용법')
        self.setGeometry(100, 100, 1000, 600)
        self.setStyleSheet("background-color: white;")  # 전체 배경 흰색

        # 메인 레이아웃
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        self.setLayout(layout)

        # 타이틀 라벨
        title_label = QLabel("캘리브레이션 튜토리얼")
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        title_label.setStyleSheet("color: #333333;")  # 글꼴 색상 설정
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # 버튼 스타일 설정
        button_style = """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: 2px solid #4CAF50;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: #45A049;
            }
        """

        # 버튼 레이아웃
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)

        # 캘리브레이션 튜토리얼 버튼
        record_button = QPushButton("캘리브레이션 설명")
        record_button.setStyleSheet(button_style)
        record_button.setIcon(QIcon("path/to/icon_tutorial.png"))  # 이미지 경로 확인
        record_button.clicked.connect(self.show_tutorial)

        # PDF 다운로드 버튼
        download_button = QPushButton("PDF 다운로드")
        download_button.setStyleSheet(button_style)
        download_button.setIcon(QIcon("path/to/icon_download.png"))  # 이미지 경로 확인
        download_button.clicked.connect(self.download_checkerboard)

        # 카메라 캘리브레이션 버튼
        calibration_button = QPushButton("카메라 캘리브레이션")
        calibration_button.setStyleSheet(button_style)
        calibration_button.setIcon(QIcon("path/to/icon_camera.png"))  # 이미지 경로 확인
        calibration_button.clicked.connect(self.do_camera_calibration)

        button_layout.addWidget(record_button)
        button_layout.addWidget(download_button)
        button_layout.addWidget(calibration_button)

        # 프로세스 출력 텍스트 표시 영역
        self.process_output = QTextEdit()
        self.process_output.setReadOnly(True)
        self.process_output.setStyleSheet("border: 1px solid #CCCCCC; background-color: #FAFAFA; padding: 10px;")
        self.process_output.setFixedHeight(400)  # 높이 고정
        layout.addWidget(self.process_output)

        # '메인으로' 버튼 설정 및 추가
        navigation_layout = QHBoxLayout()
        back_button = QPushButton("← 메인으로")
        back_button.clicked.connect(self.go_back_to_main)
        back_button.setStyleSheet("font-size: 18px;")
        navigation_layout.addWidget(back_button)

        # 레이아웃에 구성 요소 추가
        layout.addLayout(button_layout)
        layout.addLayout(navigation_layout)

    # 캘리브레이션 설명
    def show_tutorial(self):
        record_guide_text = """
        <hr>

        <div style="text-align: center;">
        <h2><b>카메라 캘리브레이션</b></h2>
        <h3><b>1-1 체커보드 다운로드 및 준비</b></h3>
        <p>아래 <b>PDF 다운로드</b> 버튼을 눌러 체커보드 이미지를 다운로드하고 인쇄합니다.<br>
        인쇄한 체커보드는 <b>평평한 곳에 고정</b>해 주세요. (종이가 휘지 않도록 주의)</p>

        <h3><b>1-2 캘리브레이션 수행</b></h3>
        <p>‘카메라 캘리브레이션’ 버튼을 눌러 캘리브레이션을 시작합니다.<br>
        체커보드 이미지를 <b>여러 각도와 거리</b>에서 카메라로 촬영합니다.<br>
        <b>총 15장의 사진</b>을 찍으면 완료됩니다.</p>

        <h3><b>* 캘리브레이션의 목적 *</b></h3>
        <p>이 과정은 <b>시선 추적의 정확도</b>를 높이기 위한 것입니다.<br>
        만약 이 과정을 건너뛰면 프로그램은 기본 설정으로 작동합니다.</p>

        <hr>
        """
        self.process_output.setHtml(record_guide_text)  # QTextEdit에 텍스트 설정

    # 체커보드 다운로드
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

    # 카메라 캘리브레이션
    def do_camera_calibration(self):
        try:
            self.process = QProcess(self)
            self.process.setProcessChannelMode(QProcess.MergedChannels)
            self.process.readyRead.connect(self.handle_stdout)
            self.process.finished.connect(self.process_finished)
            command = 'source /Users/jeon-yewon/miniforge3/bin/activate mpii && python tools/get_calib_matrix.py'
            self.process.start('bash', ['-c', command])
            self.process_pid = self.process.processId()
            self.process_output.append(f"프로세스가 시작되었습니다. (PID: {self.process_pid})")
        except Exception as e:
            self.process_output.append(f"Error: {e}")

    # 프로세스 출력
    def handle_stdout(self):
        data = self.process.readAllStandardOutput().data().decode('utf-8').strip()
        if data:
            self.process_output.append(data)

    # 프로세스 종료
    def process_finished(self):
        self.process_output.append("[캘리브레이션 종료]")
        self.process = None

    def go_back_to_main(self):
        from sst_main_window import MainWindow
        self.main_window = MainWindow()
        self.main_window.show()
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

eye_select_mode = 0

class SidebarButton(QPushButton):
    """사이드바에 사용되는 버튼. 클릭 시 선택 상태를 유지하고 강조."""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setStyleSheet("""
            QPushButton {
                background-color: #e0f7e0;
                border: 2px solid #4CAF50;
                border-radius: 10px;
                padding: 10px;
                font-size: 16px;
                font-weight: bold;
                color: #333333;
            }
            QPushButton:checked {
                background-color: #4CAF50;
                color: white;
            }
            QPushButton:hover {
                background-color: #c8e6c9;
            }
        """)
        self.setFixedWidth(150)

class TreatPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('치료 선택')
        self.setGeometry(100, 100, 1000, 600)
        self.setStyleSheet("background-color: white;")

        main_layout = QVBoxLayout()
        
        # 상단에 현재 선택 상태를 표시하는 라벨
        self.selection_label = QLabel("안구와 치료 방안을 선택하세요.", alignment=Qt.AlignCenter)
        font = QFont("Arial", 18, QFont.Bold)
        self.selection_label.setFont(font)
        # self.selection_label.setFont(QFont("Arial", 16, QFont.Bold)) 
        main_layout.addWidget(self.selection_label)
        
        content_layout = QHBoxLayout()
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setAlignment(Qt.AlignTop)

        # 안구 선택 섹션
        eye_section_label = QLabel("안구 선택", alignment=Qt.AlignCenter)
        eye_section_label.setFont(QFont("Arial", 16, QFont.Bold))
        sidebar_layout.addWidget(eye_section_label)

        self.eye_buttons = []
        eye_options = ["왼쪽 눈", "오른쪽 눈", "양쪽 눈"]
        for i, option in enumerate(eye_options):
            button = SidebarButton(option)
            button.clicked.connect(lambda _, index=i: self.select_eye(index))
            sidebar_layout.addWidget(button)
            self.eye_buttons.append(button)

        # 치료 방안 섹션
        treatment_section_label = QLabel("치료 방안", alignment=Qt.AlignCenter)
        treatment_section_label.setFont(QFont("Arial", 16, QFont.Bold))
        sidebar_layout.addWidget(treatment_section_label)

        self.treatment_buttons = []
        treatment_options = ["낱말 카드", "동화책"]
        for i, option in enumerate(treatment_options):
            button = SidebarButton(option)
            button.clicked.connect(lambda _, index=i: self.select_treatment(index))
            sidebar_layout.addWidget(button)
            self.treatment_buttons.append(button)

        # 콘텐츠 디스플레이 영역
        self.content_stack = QStackedWidget()
        content_layout.addLayout(sidebar_layout)
        content_layout.addWidget(self.content_stack, stretch=1)

        # 각 선택 조합에 따른 콘텐츠 페이지 생성
        self.content_pages = {
            (0, 0): CardSelectionPage("왼쪽 눈"),
            (0, 1): PicturebookPage("왼쪽 눈"),
            (1, 0): CardSelectionPage("오른쪽 눈"),
            (1, 1): PicturebookPage("오른쪽 눈"),
            (2, 0): CardSelectionPage("양쪽 눈"),
            (2, 1): PicturebookPage("양쪽 눈"),
        }

        for page in self.content_pages.values():
            self.content_stack.addWidget(page)

        # 초기 선택 상태
        self.selected_eye = None
        self.selected_treatment = None

        # '메인으로' 버튼 추가
        navigation_layout = QHBoxLayout()

        main_button = QPushButton('← 메인으로')
        main_button.setStyleSheet("font-size: 18px;")
        main_button.clicked.connect(self.go_back_to_main)

        navigation_layout.addWidget(main_button)

        main_layout.addLayout(content_layout)
        main_layout.addLayout(navigation_layout)
        self.setLayout(main_layout)

    def select_eye(self, index):
        """안구 선택 시 실행"""
        global eye_select_mode
        eye_select_mode = index  # eye_select_mode 업데이트
        self.selected_eye = index
        for i, button in enumerate(self.eye_buttons):
            button.setChecked(i == index)
        self.update_selection_label()
        self.update_content_display()

    def select_treatment(self, index):
        """치료 방안 선택 시 실행"""
        self.selected_treatment = index
        for i, button in enumerate(self.treatment_buttons):
            button.setChecked(i == index)
        self.update_selection_label()
        self.update_content_display()

    def update_selection_label(self):
        """선택된 안구와 치료 방안을 상단 라벨에 표시."""
        eye_text = ["왼쪽 눈", "오른쪽 눈", "양쪽 눈"][self.selected_eye] if self.selected_eye is not None else "미선택"
        treatment_text = ["낱말 카드", "동화책"][self.selected_treatment] if self.selected_treatment is not None else "미선택"
        self.selection_label.setText(f"선택: {eye_text} - {treatment_text}")

        font = QFont("Arial", 18, QFont.Bold)
        self.selection_label.setFont(font)

    def update_content_display(self):
        """선택된 안구와 치료 방안에 따라 콘텐츠를 업데이트."""
        if self.selected_eye is not None and self.selected_treatment is not None:
            page_key = (self.selected_eye, self.selected_treatment)
            self.content_stack.setCurrentWidget(self.content_pages[page_key])

    def go_back(self):
        """이전 페이지로 이동"""
        pass

    def go_back_to_main(self):
        """메인 페이지로 돌아가는 기능"""
        from sst_main_window import MainWindow
        self.main_window = MainWindow()
        self.main_window.show()
        self.close()


#동화책
class PicturebookPage(QWidget):
    def __init__(self, eye_type):
        super().__init__()
        self.setWindowTitle(f'{eye_type} - 동화책 선택')
        self.setGeometry(100, 100, 1000, 600)

        layout = QVBoxLayout()

        # 폴더 목록 표시할 QListWidget 생성
        folder_path = "./books"
        self.folder_list = QListWidget()
        self.folder_list.setStyleSheet("font-size: 18px;")

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


    def go_back_to_treat(self):
        """치료 페이지로 이동"""
        self.treat_window = TreatPage()
        self.treat_window.show()
        self.close()

# 낱말카드
# 낱말카드
class CardSelectionPage(QWidget):
    def __init__(self, eye_type):
        super().__init__()
        self.setWindowTitle(f'{eye_type} - 한글 카드 선택')
        self.setGeometry(100, 100, 1000, 600)

        layout = QVBoxLayout()

        self.card_list = QListWidget()

        # 폴더 목록 표시할 QListWidget 생성
        folder_path = "./cards"
        self.folder_list = QListWidget()
        self.folder_list.setStyleSheet("font-size: 18px;")

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
        from sst_main_window import MainWindow
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
        from sst_main_window import MainWindow
        self.main_window = MainWindow()
        self.main_window.show()
        self.close()

    def go_back_to_treat(self):
        """치료 페이지로 이동"""
        self.treat_window = TreatPage()
        self.treat_window.show()
        self.close()

# 애플리케이션 실행
if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())

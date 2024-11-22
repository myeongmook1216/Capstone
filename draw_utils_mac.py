# drawing utils
import cv2
import time
import numpy as np
import pdb
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from screen_conf import *

#################################################################################  add start
import os
import random
import easyocr
from PIL import Image, ImageDraw, ImageFont

# EasyOCR 객체 생성
reader = easyocr.Reader(['ko', 'en'])

# 현재 이미지 인덱스 설정
current_index = 0
current_word_index = 0
#################################################################################  add end

focus = 0
rng_pos = (0,0)
# cur_pos = (W_px//2, adj_H//2) #pyautogui.position()
#CANV_MODE = 'STABILITY' #'LEFTRIGHT' # 'UPDOWN'

def draw_grid(img, line_color=(0, 255, 0), thickness=1, type_=cv2.LINE_AA, pxstep=50):
	'''(ndarray, 3-tuple, int, int) -> void
	draw gridlines on img
	line_color:
		BGR representation of colour
	thickness:
		line thickness
	type:
		8, 4 or cv2.LINE_AA
	pxstep:
		grid line frequency in pixels
	'''
	x = pxstep
	y = pxstep
	while x < img.shape[1]:
		cv2.line(img, (x, 0), (x, img.shape[0]), color=line_color, lineType=type_, thickness=thickness)
		x += pxstep

	while y < img.shape[0]:
		cv2.line(img, (0, y), (img.shape[1], y), color=line_color, lineType=type_, thickness=thickness)
		y += pxstep
	return img

def color_grid(img, pos, paint = BLUE, pxstep=50):
	#pdb.set_trace()
	x = pos[0]//pxstep*pxstep
	# y = (pos[1]-bottom_line//2)
	y = (pos[1]-bottom_line//2)//pxstep*pxstep 
	w, h = pxstep, pxstep 
	img = cv2.rectangle(img, (x, y), (x + w, y + h), paint, -1)
	return img

####################################################################### function start

def color_grid_2(img, pos, paint=(0, 0, 255), pxstep=50):
    x = pos[0] // pxstep * pxstep
    y = (pos[1] - bottom_line // 2) // pxstep * pxstep
    w, h = pxstep, pxstep
    img = cv2.circle(img, (x, y), 5, paint, -1)  # 빨간색 원으로 표시
    return img

####################################################################### function end

def demo_sequence(img):
	'''
	# Test-01
	Demo sequence moving the points from mid of the screen, 
										then to the upper side,
										then to the right most corner,
										and from there to the bottom,
	side of the screen
	'''
	global focus, rng_pos
	focus += 1
	# print(focus)
	if focus < 90:
		rng_pos = (W_px//2, adj_H//2+GRID_STEP)
		#img = color_grid(img, rng_pos, paint = RED, pxstep=GRID_STEP)
	if focus >= 120:
		# CENTER TOP
		rng_pos = (W_px//2, 0+GRID_STEP*2)
	if focus >= 150:
		# RIGHT TOP CORNER
		rng_pos = (W_px-GRID_STEP, 0+GRID_STEP*2)
	if focus >= 180:
		# RIGHT CENTER EDGE
		rng_pos = (W_px-GRID_STEP, adj_H//2+GRID_STEP)
	if focus >= 210:
		# RIGHT BOTTOM CORNER
		rng_pos = (W_px-GRID_STEP, adj_H)
	if focus > 260:
		# RESTART THE SEQUENCE
		focus = 0
	img = color_grid(img, rng_pos, paint = RED, pxstep=GRID_STEP)
	return rng_pos

def demo_updown(img):
	'''
	# Test-02
	Demo sequence moving the points from upper side of the screen 
	to the lower side of the screen
	'''
	global focus, rng_pos
	focus += 1
	# print(focus)
	if focus < 90:
		rng_pos = (W_px//2, adj_H//2+GRID_STEP)
		#img = color_grid(img, rng_pos, paint = RED, pxstep=GRID_STEP)
	if focus >= 90 and focus < 120:
		# CENTER TOP
		rng_pos = (W_px//2, adj_H//2-GRID_STEP)
	if focus >= 120 and focus < 150:
		# RIGHT TOP CORNER
		rng_pos = (W_px//2, adj_H//2-GRID_STEP*3)
	if focus >= 150 and focus < 180:
		# RIGHT CENTER EDGE
		rng_pos = (W_px//2, 0+GRID_STEP*2)
	if focus >= 180 and focus < 210:
		# RIGHT TOP CORNER
		rng_pos = (W_px//2, adj_H//2-GRID_STEP*3)
	if focus >= 210 and focus < 240:
		# RIGHT TOP CORNER
		rng_pos = (W_px//2, adj_H//2-GRID_STEP)
	if focus >= 240 and focus < 270:
		# RIGHT TOP CORNER
		rng_pos = (W_px//2, adj_H//2+GRID_STEP*2)
	if focus >= 270 and focus < 300:
		# RIGHT TOP CORNER
		rng_pos = (W_px//2, adj_H//2+GRID_STEP*4)
	if focus >= 300 and focus < 330:
		# RIGHT TOP CORNER
		rng_pos = (W_px//2, adj_H//2+GRID_STEP*6)
	if focus > 330:
		# RIGHT BOTTOM CORNER
		rng_pos = (W_px//2, adj_H)
	if focus > 380:
		# RESTART THE SEQUENCE
		focus = 0
	img = color_grid(img, rng_pos, paint = RED, pxstep=GRID_STEP)
	return rng_pos

def demo_leftright(img):
	'''
	Test-03
	Demo sequence moving the points from left side of the screen 
	to the right side of the screen
	'''
	global focus, rng_pos
	focus += 1
	# print(focus)
	if focus < 90:
		rng_pos = (W_px//2, adj_H//2+GRID_STEP)
		#img = color_grid(img, rng_pos, paint = RED, pxstep=GRID_STEP)
	if focus >= 90 and focus < 120:
		# CENTER TOP
		rng_pos = (W_px//2+GRID_STEP*3, adj_H//2+GRID_STEP)
	if focus >= 120 and focus < 150:
		# RIGHT TOP CORNER
		rng_pos = (W_px//2+GRID_STEP*6, adj_H//2+GRID_STEP)
	if focus >= 150 and focus < 180:
		# RIGHT CENTER EDGE
		rng_pos = (W_px//2+GRID_STEP*9, adj_H//2+GRID_STEP)
	if focus >= 180 and focus < 210:
		# RIGHT TOP CORNER
		rng_pos = (W_px//2+GRID_STEP*12, adj_H//2+GRID_STEP)
	if focus >= 210 and focus < 240:
		# RIGHT TOP CORNER
		rng_pos = (W_px//2+GRID_STEP*9, adj_H//2+GRID_STEP)
	if focus >= 240 and focus < 270:
		# RIGHT TOP CORNER
		rng_pos = (W_px//2+GRID_STEP*6, adj_H//2+GRID_STEP)
	if focus >= 270 and focus < 300:
		# RIGHT TOP CORNER
		rng_pos = (W_px//2+GRID_STEP*3, adj_H//2+GRID_STEP)
	if focus >= 300 and focus < 330:
		# RIGHT TOP CORNER
		rng_pos = (W_px//2-GRID_STEP, adj_H//2+GRID_STEP)
	if focus >= 330 and focus < 370:
		# RIGHT TOP CORNER
		rng_pos = (W_px//2-GRID_STEP*3, adj_H//2+GRID_STEP)
	if focus >= 370 and focus < 400:
		# RIGHT TOP CORNER
		rng_pos = (W_px//2-GRID_STEP*6, adj_H//2+GRID_STEP)
	if focus >= 400 and focus < 430:
		# RIGHT BOTTOM CORNER
		rng_pos = (W_px//2-GRID_STEP*9, adj_H//2+GRID_STEP)
	if focus > 430:
		rng_pos = (W_px//2-GRID_STEP*12, adj_H//2+GRID_STEP)
	if focus > 500:
		# RESTART THE SEQUENCE
		focus = 0
	img = color_grid(img, rng_pos, paint = RED, pxstep=GRID_STEP)
	return rng_pos

def demo_stability(img):
	'''
	# Test-04, Test-05, Test-06
	# first case is to move towards the camera while focusing at the same point (20cm)
	# second case is moving away from the camera (20cm)
	# third case indian nodding
	'''
	global focus, rng_pos
	#focus += 1
	#print(focus)
	# FOCUS POINT - currently center:
	rng_pos = (W_px//2, adj_H//2+GRID_STEP)
	img = color_grid(img, rng_pos, paint = RED, pxstep=GRID_STEP)
	return rng_pos

def random_sequence(img):
# def random_sequence(img, cur_pos):
	'''
	# Random Sequence - display random spot on the screen which the person can try to aim at!
	'''
	global focus, rng_pos
	if focus <= 80: # 100 - 4 seonds
		# KEEP OLD POSITION
		focus += 1
	else:
		# generate new ranom spot
		rng_pos = (np.random.randint(0, W_px),np.random.randint(0, H_px))
		#img = color_grid(img, rng_pos, paint = RED, pxstep=GRID_STEP)
		focus = 0
	return rng_pos


def plot_pts(pts, name, MAE = None, save_path = None):
	rng_pos = np.array([list(y) for y in [x[0] for x in pts]])
	cur_pos = np.array([list(y) for y in [x[1] for x in pts]])
	
	str_name = name #.split('/')[1].split('.')[0]
	if MAE:
		plt.title('Results of {}, MAE: '.format(str_name, MAE))
	else:
		plt.title('Results of {}'.format(str_name))
	plt.plot(rng_pos[:,0], rng_pos[:,1], 'r.', markersize = 20, label = 'target point')
	plt.plot(cur_pos[:,0], cur_pos[:,1], 'bo', label = 'gaze point', mfc='none')
	plt.gca().invert_yaxis()
	plt.grid()
	plt.legend()
	if save_path:
		plt.savefig(save_path+str_name+'.png')
	else:
		plt.savefig(str_name+'.png')
	plt.close()

def accuracy_measure(pts):
	'''
	if sum(cur_pos) == 0:
		return
	else:
		pdb.set_trace()
	'''
	# input is all the points
	# separate the rng_pos and cur_pos
	# remove values at indexes where cur_pos == 0
	rng_pos = [x[0] for x in pts] # TUPLES
	cur_pos = [x[1] for x in pts] # TUPS
	# TUPS TO LIST:
	rng_pos = [list(elem) for elem in rng_pos]
	cur_pos = [list(elem) for elem in cur_pos]
	# INDEX OF 0 cur pos:
	if 0:
		indices = [sum(item) for item in cur_pos if sum(item) == 0]

	pdb.set_trace()

def display_canv(CANV_MODE, cur_pos=None):
	# THIS FN returns RNG_POS and CUR_POS as TUPLES
	# RETURN FORMAT: (TRUE_POS, CUR_POS) ..  RNG == TRUE
	global focus, rng_pos              # focus 초점 상태/ rng_pos 랜덤 목표 위치를 설정
	img = np.zeros((adj_H, W_px,3))

	img = draw_grid(img, pxstep= GRID_STEP)   # grid를 그림
	
	if CANV_MODE == 'RNG':
		#cv2.putText(img, str_pos, (cur_pos[0]+5, cur_pos[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, WHITE, 1)
		#rng_pos = random_sequence(img, cur_pos)
		rng_pos = random_sequence(img)        # rng_pos 랜덤 좌표 설정
	if CANV_MODE == 'SEQ':
		rng_pos = demo_sequence(img)
	if CANV_MODE == 'UPDOWN':
		rng_pos = demo_updown(img)
	if CANV_MODE == 'LEFTRIGHT':
		rng_pos = demo_leftright(img)
	if CANV_MODE == 'STABILITY':
		rng_pos = demo_stability(img)

	img = color_grid(img, rng_pos, paint = RED, pxstep=GRID_STEP)    # rng_pos 랜덤 좌표를 RED로 표시
	if cur_pos:
		#cur_pos = mid_point
		# accuracy_measure(cur_pos, rng_pos)
		str_pos = str(cur_pos)
		img = color_grid(img, cur_pos, paint=BLUE, pxstep=GRID_STEP)   # cur_pos 현재 좌표를 BLUE로 표시
		xy_cur = (cur_pos[0]//GRID_STEP*GRID_STEP,(cur_pos[1]-bottom_line//2)//GRID_STEP*GRID_STEP )
		xy_rng = (rng_pos[0]//GRID_STEP*GRID_STEP,(rng_pos[1]-bottom_line//2)//GRID_STEP*GRID_STEP )
		# IF RANDOM SPOT EQUALS THE ESTIMATED FOCUS SPOT COLOR IT GREEN!
		if xy_cur == xy_rng:
			img = color_grid(img, rng_pos, paint = GREEN, pxstep=GRID_STEP)
	else:
		cur_pos = (0,0)

	# SHOW IMG
	cv2.imshow('black_canv', img)
	cv2.moveWindow("black_canv", 0,0)
	return (rng_pos, cur_pos)


################################################################################################## function start

def display_canv(CANV_MODE, cur_pos=None):
	# THIS FN returns RNG_POS and CUR_POS as TUPLES
	# RETURN FORMAT: (TRUE_POS, CUR_POS) ..  RNG == TRUE
	global focus, rng_pos              # focus 초점 상태/ rng_pos 랜덤 목표 위치를 설정
	img = np.zeros((adj_H, W_px,3))

	img = draw_grid(img, pxstep= GRID_STEP)   # grid를 그림
	
	if CANV_MODE == 'RNG':
		#cv2.putText(img, str_pos, (cur_pos[0]+5, cur_pos[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, WHITE, 1)
		#rng_pos = random_sequence(img, cur_pos)
		rng_pos = random_sequence(img)        # rng_pos 랜덤 좌표 설정
	if CANV_MODE == 'SEQ':
		rng_pos = demo_sequence(img)
	if CANV_MODE == 'UPDOWN':
		rng_pos = demo_updown(img)
	if CANV_MODE == 'LEFTRIGHT':
		rng_pos = demo_leftright(img)
	if CANV_MODE == 'STABILITY':
		rng_pos = demo_stability(img)

	img = color_grid(img, rng_pos, paint = RED, pxstep=GRID_STEP)    # rng_pos 랜덤 좌표를 RED로 표시
	if cur_pos:
		#cur_pos = mid_point
		# accuracy_measure(cur_pos, rng_pos)
		str_pos = str(cur_pos)
		img = color_grid(img, cur_pos, paint=BLUE, pxstep=GRID_STEP)   # cur_pos 현재 좌표를 BLUE로 표시
		xy_cur = (cur_pos[0]//GRID_STEP*GRID_STEP,(cur_pos[1]-bottom_line//2)//GRID_STEP*GRID_STEP )
		xy_rng = (rng_pos[0]//GRID_STEP*GRID_STEP,(rng_pos[1]-bottom_line//2)//GRID_STEP*GRID_STEP )
		# IF RANDOM SPOT EQUALS THE ESTIMATED FOCUS SPOT COLOR IT GREEN!
		if xy_cur == xy_rng:
			img = color_grid(img, rng_pos, paint = GREEN, pxstep=GRID_STEP)
	else:
		cur_pos = (0,0)

	# SHOW IMG
	cv2.imshow('black_canv', img)
	cv2.moveWindow("black_canv", 0,0)
	return (rng_pos, cur_pos)

def on_click(event):
    global current_index, current_word_index

    # 클릭 좌표 정보 가져오기
    img_width = plt.gca().get_xlim()[1]
    img_height = plt.gca().get_ylim()[0]

    # 클릭 좌표가 왼쪽 화살표 영역에 있는지 확인
    if event.xdata is not None and event.ydata is not None:
        if -100 < event.xdata < 50 and img_height / 4 < event.ydata < img_height * 3 / 4:
            # 이전 이미지로 이동
            current_index = max(0, current_index - 1)
            current_word_index = 0  # 단어 인덱스를 초기화
            print("이전 이미지로 이동")

        # 클릭 좌표가 오른쪽 화살표 영역에 있는지 확인
        elif img_width - 50 < event.xdata < img_width + 100 and img_height / 4 < event.ydata < img_height * 3 / 4:
            # 다음 이미지로 이동
            current_index = min(len(image_files) - 1, current_index + 1)
            current_word_index = 0  # 단어 인덱스를 초기화
            print("다음 이미지로 이동")

        # 클릭으로 인해 이미지가 변경되었을 때, 새 이미지 로드 및 표시
        display_easyocr_canv('RNG')


def detect_text_bounding_box(image, current_word_index):
    # EasyOCR을 사용하여 텍스트 감지
    result = reader.readtext(image)

    # PIL 이미지를 생성하여 바운딩 박스를 그릴 준비
    image_pil = Image.fromarray(image)
    draw = ImageDraw.Draw(image_pil)

    words_boxes = []  # 각 음절의 바운딩 박스 저장 리스트
    current_box = None  # 현재 음절의 바운딩 박스

    # 텍스트 감지 결과에서 각 단어를 순차적으로 처리
    for i, detection in enumerate(result):
        box = detection[0]  # 바운딩 박스 좌표 (4개의 점)
        text = detection[1]  # 감지된 텍스트

        # 텍스트를 음절 단위로 분리 (각 음절을 개별적으로 처리)
        syllables = list(text)  # 문자열을 음절(각각의 글자)로 나눔

        # 바운딩 박스의 좌상단과 우하단 좌표 추출
        (x_min, y_min) = box[0]  # 좌상단 좌표
        (x_max, y_max) = box[2]  # 우하단 좌표

        # 각 음절의 상대적인 위치를 계산하여 바운딩 박스를 설정
        total_len = len([syllable for syllable in syllables if syllable != " "])  # 공백을 제외한 음절 개수
        syllable_start_x = x_min  # 음절의 시작 위치

        for j, syllable in enumerate(syllables):
            if syllable == " ":  # 공백일 경우 바운딩 박스를 생략
                continue

            syllable_box_width = (x_max - x_min) / total_len  # 각 음절의 폭을 계산
            syllable_box_x_max = syllable_start_x + syllable_box_width  # 음절의 우하단 X 좌표

            # 현재 음절에 대한 바운딩 박스를 그림
            if current_word_index == len(words_boxes):
                draw.rectangle([(syllable_start_x, y_min), (syllable_box_x_max, y_max)], outline="green", width=2)
                current_box = ((syllable_start_x, y_min), (syllable_box_x_max, y_max))  # 현재 음절의 바운딩 박스 저장

            # 음절의 바운딩 박스를 저장
            words_boxes.append(((syllable_start_x, y_min), (syllable_box_x_max, y_max)))
            syllable_start_x = syllable_box_x_max + 2  # 음절 간 간격

    total_words = len(words_boxes)  # 감지된 음절의 총 개수 계산

    # 바운딩 박스가 그려진 이미지를 반환, 감지된 음절 개수 추가 반환
    return np.array(image_pil), current_box, total_words


# 시선 궤적을 저장하기 위한 리스트
trail_positions = []
MAX_TRAIL_LENGTH = 5  # 잔상의 최대 길이 (잔상의 길이를 조정할 수 있습니다)


kalman = cv2.KalmanFilter(4, 2)
kalman.measurementMatrix = np.array([[1, 0, 0, 0], [0, 1, 0, 0]], np.float32)
kalman.transitionMatrix = np.array([[1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0], [0, 0, 0, 1]], np.float32)
kalman.processNoiseCov = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0.03, 0], [0, 0, 0, 0.03]], np.float32)

def display_laser_easyocr_canv(CANV_MODE, cur_pos=None, custom_param=None):
    global focus, current_index, current_word_index
    global GRID_STEP, bottom_line, trail_positions

    if cur_pos is not None:
        measurement = np.array([[np.float32(cur_pos[0])], [np.float32(cur_pos[1])]])
        kalman.correct(measurement)
        pred = kalman.predict()
        cur_pos = (int(pred[0]), int(pred[1]))  # 괄호 수정

    # 디렉토리 설정 및 이미지 파일 목록 가져오기
    if custom_param == "hand":
        directory = "./books/hand/"
    elif custom_param == "imhere":
        directory = "./books/imhere/"
    elif custom_param == "moon":
        directory = "./books/moon/"
    elif custom_param == "shoes":
        directory = "./books/shoes/"
    elif custom_param == "smile":
        directory = "./books/smile/"
    elif custom_param == "ssak":
        directory = "./books/ssak/"
    elif custom_param == "animal":
        directory = "./cards/animal/"
    elif custom_param == "job":
        directory = "./cards/job/"
    elif custom_param == "vegitable":
        directory = "./cards/vegitable/"
    elif custom_param == "vehicle":
        directory = "./cards/vehicle/"
    else:
        print("유효하지 않은 custom_param입니다.")
        return

    image_files = sorted([f for f in os.listdir(directory) if f.endswith(".jpg")])
    img = np.zeros((adj_H, W_px, 3), dtype=np.uint8)

    image_path = os.path.join(directory, image_files[current_index])
    image = cv2.imread(image_path)
    if image is None:
        print(f"이미지를 불러올 수 없습니다: {image_files[current_index]}")
        current_index += 1
        current_word_index = 0
        return

    image = cv2.resize(image, (W_px, adj_H))
    img[:adj_H, :W_px] = image

    if CANV_MODE == 'RNG':
        image_with_boxes, current_box, total_words = detect_text_bounding_box(image, current_word_index)
        img = np.array(image_with_boxes)

        if current_box:
            x_min, y_min = current_box[0]
            x_max, y_max = current_box[1]

            if cur_pos:
                trail_positions.append(cur_pos)
                if len(trail_positions) > MAX_TRAIL_LENGTH:
                    trail_positions.pop(0)

                for i in range(1, len(trail_positions)):
                    cv2.line(img, trail_positions[i - 1], trail_positions[i], (0, 0, 255), 2)

                xy_cur = (cur_pos[0], cur_pos[1])
                if x_min <= xy_cur[0] <= x_max and y_min <= xy_cur[1] <= y_max:
                    for _ in range(2):
                        img_blink = img.copy()
                        cv2.rectangle(img_blink, (int(x_min), int(y_min)), (int(x_max), int(y_max)), (0, 255, 0), 2)
                        cv2.imshow('canvas', img_blink)
                        cv2.waitKey(100)
                        cv2.imshow('canvas', img)
                        cv2.waitKey(100)

                    current_word_index += 1
                    display_laser_easyocr_canv.rng_pos_set = False

            if current_word_index >= total_words:
                current_index += 1
                current_word_index = 0
                display_laser_easyocr_canv.rng_pos_set = False

    cv2.imshow('canvas', img)
    return cur_pos

################################################################################################## function end

def plot_eye_XYZ(pts, name, save_path):

	X_arr = np.array([x[0] for x in pts])
	Y_arr = np.array([x[1] for x in pts])
	Z_arr = np.array([x[2] for x in pts])

	fig, ((ax1, ax2, ax3)) = plt.subplots(nrows=3, ncols=1, sharex=False, sharey=False, figsize=(10,8))
	fig.suptitle('Scenario: ' + name)

	ax1.plot(X_arr, label = 'X coords')
	ax2.plot(Y_arr, label = 'Y coords')
	ax3.plot(Z_arr, label = 'Z coords')
	plt.legend()
	ax1.grid()
	ax2.grid()
	ax3.grid()
	# plt.show()
	if save_path:
		plt.savefig(save_path+name+'.pdf')
	else:
		plt.savefig(name+'.pdf')
	plt.close()

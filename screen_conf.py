# # CANVAS PARAMTERS
# from screenSize import get_screenWH
# #------------------------------------------------
# # PARAMS OF THE MACBOOK PRO 13 
# # H_px = 900 # WITH IN PIX
# # W_px = 1440
# W_px, H_px = get_screenWH()
# # FOLLOWING PARAMS must be self defined!
# H_m = 0.185 #  SCREEN HEIGHT IN M, measured with ruler
# W_m = 0.285 #  SCREEN WIDTH IN M, measured with ruler
# top_dist = 0.008 # DISTANCE FROM CAMERA SENSOR CENTER TO SCREEN 1cm or 0.8 cm
# bottom_line = 120
# adj_H = H_px - bottom_line
# GRID_STEP = 50 # TRY 50
# IMG_SCALE = 1 #0.3

# # COLORS
# #------------------------------------------------
# RED = (0,0,255)
# WHITE = (255,255,255)
# BLUE = (255, 0, 0)
# GREEN = (0, 255, 0)
# BLACK = (0, 0, 0)

# # FOR VIDEO
# #------------------------------------------------
# FPS = 20.0
# VID_H = 720
# VID_W = 1280
 
########################################################

# CANVAS PARAMETERS
from screenSize import get_screenWH
#------------------------------------------------
# PARAMS OF THE MACBOOK AIR M2
# H_px = 1664 # HEIGHT IN PIXELS
# W_px = 2560 # WIDTH IN PIXELS
W_px, H_px = get_screenWH()
# FOLLOWING PARAMS must be self defined!
H_m = 0.171 # SCREEN HEIGHT IN METERS, measured with ruler (approx 17.7 cm)
W_m = 0.291 # SCREEN WIDTH IN METERS, measured with ruler (approx 29.5 cm)
top_dist = 0.008 # DISTANCE FROM CAMERA SENSOR CENTER TO SCREEN (8mm or 0.8 cm)
bottom_line = 150
adj_H = H_px - bottom_line
GRID_STEP = 20 # TRY 50
IMG_SCALE = 1 # Set to 1 for full-scale images

# COLORS
#------------------------------------------------
RED = (0, 0, 255)
WHITE = (255, 255, 255)
BLUE = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# FOR VIDEO
#------------------------------------------------
FPS = 20.0
VID_H = 720
VID_W = 1280

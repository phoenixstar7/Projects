import sys
import pdb
import cv2
import pandas as pd

def print_usage():
    """
    Prints usage.
    """
    print("ERROR in usage")
    print("\nUSAGE:")
    print("python3 run_tracker.py <vid> <pos> <method>")
    print("\t <vid>    = Full path to video")
    print("\t <pos>    = Rectangle coordinates 'x,y,w,h'")
    print("\t\t    '0,0,0,0' = Interactive selection of roi")
    print("\t <method> = Tracking method to use (integer)")
    print("\t\t    0 = normalized cross correlation (nxcorr)")
    print("\t\t    1 = nxcorr (or) 0 with continuous update")


def get_swin_coords(roi, fr_size):
    """
    Returns search windows coordinates (x,y,w,h) calculated
    based on roi coordinates

    Search window has each direction expanded by half of roi
    size. That is to say along width the search window is
    expaned by w, w/2 along left and right.
    """
    # Frame size
    nrows = fr_size[0]
    ncols = fr_size[1]

    # Roi
    x = roi[0]
    y = roi[1]
    w = roi[2]
    h = roi[3]

    # Search window
    sw_x1 = max(0, round(x - w))
    sw_y1 = max(0, round(y - h))
    sw_x2 = min(ncols, round(x + w + w))
    sw_y2 = min(nrows, round(y + h + h))

    return (sw_x1,sw_y1) , (sw_x2, sw_y2)



# Execution starts here
if (len(sys.argv) != 4):
    print_usage()
    sys.exit(1)


# Extracting arguments
vpath = sys.argv[1]
roi   = list(map(int, sys.argv[2].split(",")))
meth  = sys.argv[3]


# Video loop
vidh        = cv2.VideoCapture(vpath)
fr_ret, fr  = vidh.read()
gfr = cv2.cvtColor(fr,cv2.COLOR_BGR2GRAY)

# Search window coordinates, top left and bottom right
swtl, swbr  = get_swin_coords(roi,fr.shape)
sw_w        = swbr[0] - swtl[0]
sw_h        = swbr[1] - swtl[1]

# Initial template
tmp         = gfr[ roi[1] : roi[1] + roi[3],
                  roi[0] : roi[0] + roi[2] ]

if(not(fr_ret)):
    print("ERROR reading video file")
    sys.exit(1)

nxcorr_vals = []
x_vals      = []
y_vals      = []
poc         = 0
pocs        = []

while(vidh.isOpened() and fr_ret):

    # Search window image
    sw_img  = gfr[ swtl[1] : swbr[1],
                   swtl[0] : swbr[0] ]

    # Performing template matching
    mat_res = cv2.matchTemplate(sw_img, tmp, 5)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(mat_res)

    # Best matching
    nxcorr_vals = nxcorr_vals + [max_val]
    bmtl        = (swtl[0] + max_loc[0], swtl[1] + max_loc[1])# best match top left
    bmbr        = (bmtl[0] + roi[2], bmtl[1] + roi[3]) # bottom right

    # Updating template
    tmp         = gfr[ bmtl[1] : bmbr[1],
                       bmtl[0] : bmbr[0] ]
    x_vals = x_vals + [bmtl[0]]
    y_vals = y_vals + [bmtl[1]]
    pocs   = pocs   + [poc]

    # Drawing rectangle
    cv2.rectangle(fr, bmtl, bmbr,(255,255,0),2)

    # Show video
    cv2.imshow(vpath,fr)
    cv2.imshow("Template", tmp)
    cv2.waitKey(1)

    # Read next frame
    fr_ret, fr = vidh.read()
    if fr_ret:
        gfr = cv2.cvtColor(fr,cv2.COLOR_BGR2GRAY)
        poc=poc+1
        #print(poc)

# Saving tracker output as csv
x    = x_vals
y    = y_vals
w    = [roi[2]]*len(pocs)
h    = [roi[3]]*len(pocs)
flag = [0]*len(pocs)
df   = pd.DataFrame(columns=['poc','x','y','w','h','flag'])
df['poc']  = pocs
df['x']    = x
df['y']    = y
df['w']    = w
df['h']    = h
df['flag'] = flag
#df.to_csv("nxcorr_ut.csv")

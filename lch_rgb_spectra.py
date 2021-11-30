import sys
import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import datetime
import os

resoultionMultiplier = 1

maxChroma = 132

lch2rgbMap = None

# create path if not existant
if not os.path.exists(os.path.expanduser('~/.lch_rgb')):
	os.makedirs(os.path.expanduser('~/.lch_rgb'))

# load saved mappings if available
if os.path.exists(os.path.expanduser('~/.lch_rgb/map-lch2rgb.pickle')):
	startDT = datetime.datetime.now()
	import pickle
	with open(os.path.expanduser('~/.lch_rgb/map-lch2rgb.pickle'), "rb") as fp:
		lch2rgbMap = pickle.load(fp)
	fp.close()
	print("loaded pickle in", datetime.datetime.now() - startDT)
else:
	startDT = datetime.datetime.now()
	# from colour import XYZ_to_sRGB, Lab_to_XYZ, LCHab_to_Lab
	import coloraide
	print("imported conversions in", datetime.datetime.now() - startDT)

def angleDist(a, b):
	return abs(((b - a) + 180) % 360 - 180)

def upscaleRGB(rgb):
	newRGB = []
	for component in rgb:
		newRGB.append(round(min(1,max(0,component))*255))
	return newRGB

def lch_to_rgb(lightness, chroma, hue):
	c = coloraide.Color('lch-d65', [lightness, chroma, hue]).convert('srgb')
	if c.in_gamut():
		return c
	return None

def rgb_to_lch(red, green, blue):
	c = coloraide.Color('srgb', [red/255, green/255, blue/255]).convert('lch-d65')
	if c.in_gamut():
		return c
	return None

def highestChromaColor(lightness, hue):
	for chroma in range(maxChroma, 0, -1):
		c = lch_to_rgb(lightness, chroma, hue)
		if not c is None:
			if chroma < maxChroma:
				return c
				# decaChroma = chroma + 0.9
				# while decaChroma >= chroma:
				# 	dc = lch_to_rgb(lightness, decaChroma, hue)
				# 	if not dc is None:
				# 		centiChroma = decaChroma + 0.09
				# 		while centiChroma >= decaChroma:
				# 			cc = lch_to_rgb(lightness, centiChroma, hue)
				# 			if not cc is None:
				# 				return cc
				# 			centiChroma -= 0.01
				# 	decaChroma -= 0.1
			else:
				return c

def gamutPixel(lightness, chroma, hue):
	c = coloraide.Color('lch-d65', [lightness, chroma, hue]).convert('srgb')
	if c.in_gamut():
		return upscaleRGB(c.coords())
	else:
		return [0,0,0]

# def showColor(rgb):
	# return np.full([101, 101, 3], [int(rgb.clamped_rgb_r*255), int(rgb.clamped_rgb_g*255), int(rgb.clamped_rgb_b*255)], dtype=np.uint8), [0, 100, 0, 100]

def findRGBGamut(lightness, chroma, hue):
	extent = []
	rgbMap = None
	if lightness and chroma:
		extent = [0, 360, 0, 101]
		rgbMap = np.zeros([101, 360, 3], dtype=np.uint8)
		for hue in range(0, 360):
			rgb = gamutPixel(lightness, chroma, hue)
			for y in range(0, 101):
				rgbMap[y, hue] = rgb
	elif lightness and hue:
		extent = [0, maxChroma+1, 0, 101]
		rgbMap = np.zeros([101, maxChroma+1, 3], dtype=np.uint8)
		for chroma in range(0, maxChroma+1):
			rgb = gamutPixel(lightness, chroma, hue)
			for y in range(0, 101):
				rgbMap[y, chroma] = rgb
	elif chroma and hue:
		extent = [0, 101, 0, 101]
		rgbMap = np.zeros([101, 101, 3], dtype=np.uint8)
		for lightness in range(0, 101):
			rgb = gamutPixel(lightness, chroma, hue)
			for y in range(0, 101):
				rgbMap[y, lightness] = rgb
	elif lightness:
		extent = [0, 360, 0, maxChroma+1]
		rgbMap = np.zeros([((maxChroma+1)*resoultionMultiplier), 360, 3], dtype=np.uint8)
		for chroma in np.arange(0, maxChroma+1, 1/resoultionMultiplier):
			for hue in range(0, 360):
				rgb = gamutPixel(lightness, chroma, hue)
				rgbMap[int(chroma*resoultionMultiplier), hue] = rgb
	elif chroma:
		extent = [0, 360, 0, 101]
		rgbMap = np.zeros([101, 360, 3], dtype=np.uint8)
		for lightness in range(0, 101):
			for hue in range(0, 360):
				rgb = gamutPixel(lightness, chroma, hue)
				rgbMap[lightness, hue] = rgb
	elif hue:
		extent = [0, maxChroma+1, 0, 101]
		rgbMap = np.zeros([101*resoultionMultiplier, ((maxChroma+1)*resoultionMultiplier), 3], dtype=np.uint8)
		for lightness in np.arange(0, 101, 1/resoultionMultiplier):
			for chroma in np.arange(0, maxChroma+1, 1/resoultionMultiplier):
				rgb = gamutPixel(lightness, chroma, hue)
				rgbMap[int(lightness*resoultionMultiplier), int(chroma*resoultionMultiplier)] = rgb
	else:
		return
	return rgbMap, extent

def gamutScatterPlot():
	gamutMap = {}
	Ls = []
	Cs = []
	Hs = []
	RGBs = []
	for lightness in range(100):
		for chroma in range(maxChroma):
			for hue in range(1, 360):
				address = '{} {} {}'.format(lightness, chroma, hue)
				# c = lchColor(lightness, chroma, hue, illuminant='D65')
				# rgb = convert_color(c, sRGBColor)
				c = [lightness, chroma, hue]
				colour.convert(c, 'LCHab', 'sRGB')
				if not outOfGamut(rgb) and lchTolerance(c, convert_color(rgb, lchColor)):
					gamutMap[address] = 1
					prevL = '{} {} {}'.format(lightness-1, chroma, hue)
					prevC = '{} {} {}'.format(lightness, chroma-1, hue)
					prevH = '{} {} {}'.format(lightness, chroma, hue-1)
					if gamutMap.get(prevL) == 0 or gamutMap.get(prevC) == 0 or gamutMap.get(prevH) == 0:
						Ls.append(lightness)
						Cs.append(chroma)
						Hs.append(hue)
						RGBs.append([rgb.clamped_rgb_r, rgb.clamped_rgb_g, rgb.clamped_rgb_b])
				else:
					gamutMap[address] = 0
	print(len(Ls))
	return Ls, Cs, Hs, RGBs

def measureHueDelta():
	rgbMap = np.zeros([101, 360, 3], dtype=np.uint8)
	deltas = []
	highestD = None
	lowestD = None
	lightness = 50
	chroma = 29
	for hue in range(1, 360):
		hueA = hue - 1
		if hueA == 0:
			hueA = 360
		hueB = hue + 1
		if hueB == 361:
			hueB = 1
		colorA = coloraide.Color('lch-d65', [lightness, chroma, hueA])
		colorB = coloraide.Color('lch-d65', [lightness, chroma, hueB])
		delta = colorA.delta_e(colorB, method='2000')
		deltas.append(delta)
		if lowestD == None or delta < lowestD:
			lowestD = delta
		if highestD == None or delta > highestD:
			highestD = delta
		print(hue, delta)
	deltaRange = highestD - lowestD
	deltaMult = 100 / deltaRange
	print(lowestD, highestD, deltaRange)
	extent = [0, 360, lowestD, highestD]
	h = 1
	for d in deltas:
		y = int((d - lowestD) * deltaMult)
		for n in range(0, 101):
			if n == y:
				c = coloraide.Color('lch-d65', [lightness, chroma, h]).convert('srgb')
				rgbMap[n, h] = upscaleRGB(c.coords())
			else:
				rgbMap[n, h] = [0,0,0]
		h = h + 1
	return rgbMap, extent

def measureHSVhueShift():
	rgbMap = np.zeros([101, 360, 3], dtype=np.uint8)
	deltas = []
	highestD = None
	lowestD = None
	for hue in range(1, 360):
		lowestHSVhue = None
		highestHSVhue = None
		for lightness in range(10, 91, 5):
			# c = highestChromaColor(lightness, hue)
			for chroma in range(5, 136, 5):
				c = coloraide.Color('lch-d65', [lightness, chroma, hue]).convert('srgb')
				if c.in_gamut():
					HSVhue = c.convert('hsv').h
					if lowestHSVhue == None or HSVhue < lowestHSVhue:
						lowestHSVhue = HSVhue
					if highestHSVhue == None or HSVhue > highestHSVhue:
						highestHSVhue = HSVhue
		delta = angleDist(lowestHSVhue, highestHSVhue)
		deltas.append(delta)
		if lowestD == None or delta < lowestD:
			lowestD = delta
		if highestD == None or delta > highestD:
			highestD = delta
		print(hue, delta)
	deltaRange = highestD - lowestD
	deltaMult = 100 / deltaRange
	print(lowestD, highestD, deltaRange)
	extent = [0, 360, lowestD, highestD]
	h = 1
	for d in deltas:
		y = int((d - lowestD) * deltaMult)
		for n in range(0, 101):
			if n == y:
				c = highestChromaColor(50, h)
				rgbMap[n, h] = upscaleRGB(c.coords())
			else:
				rgbMap[n, h] = [0,0,0]
		h = h + 1
	return rgbMap, extent

args = []
for arg in sys.argv[1:]:
	if arg.upper() == 'NONE':
		args.append(None)
	else:
		args.append(int(arg))

plt.style.use('dark_background')

startDT = datetime.datetime.now()
if len(args) == 3:
	aspect = 1
	rgbMap, extent = findRGBGamut(*args)
elif len(args) == 1:
	aspect = 150
	rgbMap, extent = measureHueDelta()
else:
	aspect = 6
	rgbMap, extent = measureHSVhueShift()
print('created image map in', datetime.datetime.now() - startDT)

fig, ax = plt.subplots()
im = ax.imshow(rgbMap, interpolation='nearest', cmap=None, origin='lower', extent=extent, aspect=aspect)

mng = plt.get_current_fig_manager()
mng.window.state('zoomed')
plt.show()
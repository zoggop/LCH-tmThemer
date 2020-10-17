from colormath.color_objects import sRGBColor, LCHabColor
from colormath.color_conversions import convert_color
import sys
# import matplotlib.pyplot as plt
from PIL import Image
import numpy as np

def tolerance(a, b, t):
	return abs(b - a) <= t

def LCHtolerance(a, b, t):
	return tolerance(a.lch_l, b.lch_l, t) and tolerance(a.lch_c, b.lch_c, t) and tolerance(a.lch_h, b.lch_h, t)

def outOfGamut(rgb):
	return rgb.clamped_rgb_r != rgb.rgb_r or rgb.clamped_rgb_g != rgb.rgb_g or rgb.clamped_rgb_b != rgb.rgb_b

def gamutPixel(lightness, chroma, hue, t, lightnessT):
	d = 0
	while d <= lightnessT:
		ls = [lightness + d]
		if d > 0:
			ls.append(lightness - d)
		for l in ls:
			c = LCHabColor(l, chroma, hue)
			rgb = convert_color(c, sRGBColor)
			if not outOfGamut(rgb):
				cc = convert_color(sRGBColor(rgb.clamped_rgb_r, rgb.clamped_rgb_g, rgb.clamped_rgb_b), LCHabColor)
				if LCHtolerance(c, cc, t):
					return [int(rgb.clamped_rgb_r*255), int(rgb.clamped_rgb_g*255), int(rgb.clamped_rgb_b*255)], rgb
		d += 1
	return [0, 0, 0], None

def showColor(rgb):
	rgbMap = np.full([101, 101, 3], [int(rgb.clamped_rgb_r*255), int(rgb.clamped_rgb_g*255), int(rgb.clamped_rgb_b*255)], dtype=np.uint8)
	img = Image.fromarray(rgbMap)
	img.show()

def findRGBGamut(lightness, chroma, hue, t, lightnessT):
	fig = ''
	ax = ''
	extent = []
	dupes = {}
	rgbMap = np.zeros([101, 361, 3], dtype=np.uint8)
	if lightness and chroma:
		extent = [0, 360, 0, 1]
		for hue in range(361):
			rgb, rgbColor = gamutPixel(lightness, chroma, hue, t, lightnessT)
			for y in range(101):
				rgbMap[y, hue] = rgb
	elif lightness and hue:
		extent = [0, 100, 0, 1]
		for chroma in range(101):
			rgb, rgbColor = gamutPixel(lightness, chroma, hue, t, lightnessT)
			for y in range(101):
				rgbMap[y, chroma] = rgb
	elif chroma and hue:
		extent = [0, 100, 0, 1]
		for lightness in range(101):
			rgb, rgbColor = gamutPixel(lightness, chroma, hue, t, lightnessT)
			for y in range(101):
				rgbMap[y, lightness] = rgb
	elif lightness:
		# fig = plt.figure(figsize=(8, 8))
		# ax = plt.subplot(1, 1, 1, projection='polar')
		extent = [0, 360, 0, 100]
		for chroma in range(101):
			for hue in range(361):
				rgb, rgbColor = gamutPixel(lightness, chroma, hue, t, lightnessT)
				rgbMap[chroma, hue] = rgb
				if not (rgb[0] == 0 and rgb[1] == 0 and rgb[2] == 0):
					if not dupes.get(str(rgb)):
						dupes[str(rgb)] = []
					dupes[str(rgb)].append([chroma, hue])
				# if rgbColor:
					# plt.polar(hue / 57.29578, chroma, color=rgbColor.get_rgb_hex(), marker='s', markersize=4)
		# for rgbs in dupes.keys():
			# chs = dupes.get(rgbs)
			# if len(chs) > 8:
				# print(rgbs, len(chs))
				# for ch in chs:
					# rgbMap[ch[0], ch[1]] = [255, 255, 255]

	elif chroma:
		# fig = plt.figure(figsize=(8, 8))
		# ax = plt.subplot(1, 1, 1, projection='polar')
		extent = [0, 360, 0, 100]
		for lightness in range(101):
			for hue in range(361):
				rgb, rgbColor = gamutPixel(lightness, chroma, hue, t, lightnessT)
				rgbMap[lightness, hue] = rgb
				# if rgbColor:
					# plt.polar(hue / 57.29578, lightness, color=rgbColor.get_rgb_hex(), marker='s', markersize=4)
	elif hue:
		extent = [0, 100, 0, 100]
		for lightness in range(101):
			for chroma in range(101):
				rgb, rgbColor = gamutPixel(lightness, chroma, hue, t, lightnessT)
				rgbMap[lightness, chroma] = rgb
	else:
		return
	# if (chroma or lightness) and not (chroma and lightness):
		# plt.show()
	# else:
	# fig, ax = plt.subplots()
	# im = ax.imshow(rgbMap, interpolation='nearest', cmap=None, origin='lower', extent=extent, aspect='auto')
	# plt.show()

	img = Image.fromarray(rgbMap)
	img.show()

args = []
# for i in range(1, len(args)):
	# arg = 
for arg in sys.argv[1:]:
	if arg.upper() == 'NONE':
		args.append(None)
	else:
		args.append(int(arg))

if len(args) == 3:
	rgb = gamutPixel(*args, 1000, 0)[1]
	if rgb:
		print(gamutPixel(*args, 1000, 0)[1].get_rgb_hex())
		showColor(rgb)
	else:
		print("out of sRGB gamut")
elif len(args) == 5:
	findRGBGamut(*args)
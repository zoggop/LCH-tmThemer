### BEGIN CONFIGURATION ###

# the top-level dictionary key is a name that doesn't necessarily define whether to set background or foreground
# whether to set background or foreground is determined by values within the group dict. if a value is an empty string, or if the group is a list, the palette name will be used, or in the case of settings keys, not needed
# group lists or dict keys can include both scopes and names of settings keys
# palette can be a list of hex strings (a static palette), or a list of parameters to pass to generatePalette
palettes = {
	'background' : {
		'palette' : {'lightness':74, 'chroma':40, 'startHue':80, 'wantedNumber':72},
		'groups' : [
			[],
		],
	},
	'foreground' : {
		# 'palette' : {'lightness':25, 'chroma':18, 'startHue':125},
		'palette' : {'lightness':9, 'chroma':10, 'startHue':125, 'wantedNumber':72},
		'groups' : [
			[],
		],
	},
	'highlight' : {
		'palette' : {'startHue':30, 'lightnessMin':51, 'wantedNumber':72},
		'groups' : [
			[],
		],
	},
}

### END CONFIGURATION ###
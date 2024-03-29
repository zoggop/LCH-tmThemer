### BEGIN CONFIGURATION ###

# the top-level dictionary key is a name that doesn't necessarily define whether to set background or foreground
# whether to set background or foreground is determined by values within the group dict. if a value is an empty string, or if the group is a list, the palette name will be used, or in the case of settings keys, not needed
# group lists or dict keys can include both scopes and names of settings keys
# palette can be a list of hex strings (a static palette), or a list of parameters to pass to generatePalette
palettes = {
	# 'comment' : {
	# 	'palette' : {'lightness':85, 'chroma':10, 'tolerance':5, 'lightnessWidth':0},
	# 	'groups' : [
	# 		{'comment':'foreground', 'findHighlight':''},
	# 		['variable, support.variable, meta.qualified-name, support.other.variable'],
	# 	],
	# },
	'grayscale' : {
		'palette' : {'chroma':0, 'hue':0, 'tolerance':1000, 'xMin':15, 'xMax':90, 'gamutCheck':False},
		'groups' : [
			['background', 'findHighlightForeGround', 'selectionBorder'],
			['selection', 'lineHighlight'],
			['stackGuide', 'invisibles'],
			['guide'],
			['activeGuide'],
			['foreground'],
			['caret'],
		],
	},
	'background' : {
		'palette' : {'lightness':15, 'chroma':39, 'tolerance':5, 'lightnessWidth':0},
		'groups' : [
			{'invalid':'foreground', 'invalid.deprecated':'foreground'},
			['entity.name.class', 'entity.name.function', 'entity.other.inherited-class'],
			['meta.arrayindex, meta.item-access.arguments'],
		]
	},
	'foreground' : {
		'palette' : {'lightness':75, 'chroma':40, 'tolerance':5, 'lightnessWidth':0},
		'groups' : [
			{'keyword':'', 'storage':'', 'entity.name.tag':'', 'invalid':'background'},
			{'variable.parameter':'', 'invalid.deprecated':'background'},
			{'string':''},
			['meta.function', 'variable.function', 'entity.other.attribute-name'], # 'meta.functioncall, meta.function-call'
			[],
			['storage.type', 'support.function', 'support.constant', 'support.class', 'support.type'],
			{'constant':''},
			# {'comment':'foreground', 'findHighlight':''},
			# ['variable, support.variable, meta.qualified-name, support.other.variable'],
		]
	},
	'comment' : {
		'palette' : {'lightness':65, 'chroma':20, 'tolerance':5, 'lightnessWidth':0},
		'groups' : [
			[],
			{'comment':'foreground', 'findHighlight':''},
			[],
			[],
			[],
			[],
		]
	}
}

fontStyles = {
	'variable.parameter' : 'italic',
	'support.type' : 'italic',
	'support.class' : 'italic',
	'storage.type' : 'italic',
	'entity.other.inherited-class' : 'italic underline',
	'entity.name.class' : 'underline',
	'invalid' : 'bold',
	'invalid.deprecated' : 'bold',
}

### END CONFIGURATION ###
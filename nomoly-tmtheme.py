### BEGIN CONFIGURATION ###

# the top-level dictionary key is a name that doesn't necessarily define whether to set background or foreground
# whether to set background or foreground is determined by values within the group dict. if a value is an empty string, or if the group is a list, the palette name will be used, or in the case of settings keys, not needed
# group lists or dict keys can include both scopes and names of settings keys
# palette can be a list of hex strings (a static palette), or a list of parameters to pass to generatePalette
palettes = {
	'comment' : {
		'palette' : ['#997A66'],
		'groups' : [
			{'comment':'foreground', 'findHighlight':''}
		],
	},
	'grayscale' : {
		# 'palette' : ['#ffffff', '#f1f1f1', '#d4d4d4', '#b9b9b9', '#777777', '#616161', '#303030'],
		'palette' : {'chroma':0, 'hue':0, 'tolerance':1000, 'xMin':20, 'gamutCheck':False},
		'groups' : [
			['caret'],
			['foreground'],
			['activeGuide'],
			['guide'],
			['stackGuide', 'invisibles'],
			['selection', 'lineHighlight'],
			['background', 'findHighlightForeGround', 'selectionBorder'],
		],
	},
	'background' : {
		'palette' : {'lightness':95, 'chroma':13, 'tolerance':10, 'lightnessWidth':0},
		'groups' : [
			{'string':'', 'invalid':'foreground', 'invalid.deprecated':'foreground'},
			['entity.name.class', 'entity.name.function', 'entity.other.inherited-class'],
			['meta.arrayindex, meta.item-access.arguments'],
		]
	},
	'foreground' : {
		'palette' : {'lightness':49, 'chroma':95, 'tolerance':11, 'lightnessWidth':6},
		'groups' : [
			{'keyword':'', 'storage':'', 'entity.name.tag':'', 'invalid':'background'},
			{'variable.parameter':'', 'invalid.deprecated':'background'},
			['meta.function', 'variable.function', 'entity.other.attribute-name'], # 'meta.functioncall, meta.function-call'
			['storage.type', 'support.function', 'support.constant', 'support.class', 'support.type'],
			{'constant':''},
			# ['variable, support.variable, meta.qualified-name, support.other.variable'],
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
	'variable.function' : 'bold',
	'invalid' : 'bold',
	'invalid.deprecated' : 'bold',
}

### END CONFIGURATION ###
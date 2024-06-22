### BEGIN CONFIGURATION ###

# the top-level dictionary key is a name that doesn't necessarily define whether to set background or foreground
# whether to set background or foreground is determined by values within the group dict. if a value is an empty string, or if the group is a list, the palette name will be used, or in the case of settings keys, not needed
# group lists or dict keys can include both scopes and names of settings keys
# palette can be a list of hex strings (a static palette), or a list of parameters to pass to generatePalette
palettes = {
	'grayscale' : {
		'palette' : {'chroma':0, 'hue':0, 'xMin':0.00, 'xMax':1.00},
		'groups' : [
			['caret', 'foreground', 'variable.parameter'],
			['activeGuide'],
			['guide'],
			['stackGuide', 'invisibles'],
			['selection', 'lineHighlight'],
			['background', 'findHighlightForeGround', 'selectionBorder'],
		],
	},
	'boldbackground' : {
		'palette' : ['#0000ff','#bc0000'],
		'groups' : [
			['meta.arrayindex, meta.item-access.arguments'],
			{'invalid':'foreground', 'invalid.deprecated':'foreground'},
		]
	},
	'background' : {
		'palette' : {'lightness':0.95, 'chroma':0.069},
		'groups' : [
			['string', 'markup.italic', 'markup.bold', 'markup.strike'], #yellow
			['meta.function', 'variable.function', 'entity.other.attribute-name'], # green
			['storage.type', 'support.function', 'support.constant', 'support.class', 'support.type', 'meta.separator', 'keyword.declaration'], # cyan
		]
	},
	'foreground' : {
		'palette' : ['#0000ff', '#a200a2', '#bc0000'], # blue, purple, red
		'groups' : [
			{'constant':''}, # blue
			{'keyword':'', 'storage':'', 'entity.name.tag':'', 'invalid':'background', 'markup.heading':''}, # purple
			{'variable.parameter':'', 'invalid.deprecated':'background'}, # red
		]
	},
	'comment' : {
		'palette' : {'hues':[60], 'chroma':0.1, 'lightness':0.45},
		'groups' : [
			{'comment':'foreground', 'findHighlight':''},
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
	'markup.heading' : 'underline',
	'markup.italic' : 'italic',
	'markup.bold' : 'bold',
}

### END CONFIGURATION ###
(function() {


var Inspector = function() {
	var self = {};

	var inspectorWindow = _.elem('div', {'class': 'inspector-window'}, '', document.body);

	var clearWindow = function() {
		inspectorWindow.innerHTML = '';
	};

	var setSymbol = function(symbol) {
		clearWindow();

		var list = _.elem('dl');
		_.elem('dt', {}, 'Text', list);
		_.elem('dd', {}, symbol.text, list);
		_.elem('dt', {}, 'Font ID', list);
		_.elem('dd', {}, symbol.font_id, list);
		_.elem('dt', {}, 'Bold', list);
		_.elem('dd', {}, symbol.bold, list);
		_.elem('dt', {}, 'Italic', list);
		_.elem('dd', {}, symbol.italic, list);
		_.elem('dt', {}, 'Monospace', list);
		_.elem('dd', {}, symbol.monospace, list);
		_.elem('dt', {}, 'Serif', list);
		_.elem('dd', {}, symbol.serif, list);
		_.elem('dt', {}, 'Size', list);
		_.elem('dd', {}, symbol.pointsize, list);

		inspectorWindow.appendChild(list);
	};

	self.show = function() {
		inspectorWindow.style.display = 'block';
	};

	self.hide = function() {
		inspectorWindow.style.display = 'none';
	};

	self.setSymbol = function(symbol) {
		setSymbol(symbol);
	};

	self.hide();

	return self;
};


var Page = function(pageElement) {
	var self = {};
	self.onSymbolEntered = undefined;
	self.onSymbolReleased = undefined;

	var currentSymbol;

	var onSymbolHover = function(element) {
		if (currentSymbol !== undefined) {
			_.unbindEvent(currentSymbol, 'mouseout', onSymbolOut);
			currentSymbol = undefined;
		}
		currentSymbol = element;
		_.bindEvent(currentSymbol, 'mouseout', onSymbolOut);

		var symbolData = {
			text: currentSymbol.textContent,
			font_id: _.getData(currentSymbol, 'fontId'),
			bold: _.getData(currentSymbol, 'fontBold'),
			italic: _.getData(currentSymbol, 'fontItalic'),
			monospace: _.getData(currentSymbol, 'fontMonospace'),
			serif: _.getData(currentSymbol, 'fontSerif'),
			pointsize: _.getData(currentSymbol, 'fontPointsize')
		};
		if (self.onSymbolEntered !== undefined) {
			self.onSymbolEntered(symbolData);
		}
	};

	var onSymbolOut = function() {
		if (self.onSymbolReleased !== undefined) {
			self.onSymbolReleased();
		}
	};

	var symbols = pageElement.getElementsByClassName('symbol');
	_.forEach(symbols, function(symbol) {
		_.bindEvent(symbol, 'mouseover', function() { onSymbolHover(symbol); });
	});

	return self;
};


var inspectorWindow = Inspector();
var page = Page(document.getElementsByClassName('page')[0]);
page.onSymbolEntered = function(symbol) {
	inspectorWindow.setSymbol(symbol);
	inspectorWindow.show();
};
page.onSymbolReleased = function() {
	inspectorWindow.hide();
};


}());

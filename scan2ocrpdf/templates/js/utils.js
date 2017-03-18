
(function() {
	var has = function(array, key) {
		return Object.prototype.hasOwnProperty.call(array, key);
	};

	var forEach = function(collection, fn) {
		Array.prototype.forEach.call(collection, fn);
	};

	var bindEvent = function(element, name, fn) {
		element.addEventListener(name, fn, false);
	};

	var unbindEvent = function(element, name, fn) {
		element.removeEventListener(name, fn, false);
	};

	var getData = function(element, name) {
		return element.dataset[name];
	};

	var setData = function(element, name, value) {
		element.dataset[name] = value;
	};

	var elem = function(elementName, attrs, content, parent) {
		var element = document.createElement(elementName);
		if (attrs !== undefined) {
			for (var attrName in attrs) {
				if (has(attrs, attrName)) {
					element.setAttribute(attrName, attrs[attrName]);
				}
			}
		}

		if (content !== undefined) {
			element.appendChild(document.createTextNode(content));
		}
		if (parent !== undefined) {
			parent.appendChild(element);
		}
		return element;
	};

	window._ = {};
	window._.has = has;
	window._.forEach = forEach;
	window._.bindEvent = bindEvent;
	window._.unbindEvent = unbindEvent;
	window._.getData = getData;
	window._.setData = setData;
	window._.elem = elem;
}());

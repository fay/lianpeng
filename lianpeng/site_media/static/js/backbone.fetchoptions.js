(function (global) {

	'use strict';

	var Backbone	= global.Backbone
		, _					= global._;
	
	function deepDefaults(obj) {
		_.each(Array.prototype.slice.call(arguments, 1), function (source) {
			for (var prop in source) {
				if (source.hasOwnProperty(prop)) {
					if (_.isObject(obj[prop]) && _.isObject(source[prop])) {
						deepDefaults(obj[prop], source[prop]);
					} else if (typeof(obj[prop]) === 'undefined') {
						obj[prop] = source[prop];
					}
				}
			}
		});
		return obj;
	}
	
	function attach (proto) {
		
		var fetchReference = proto.fetch || function () {};
		
		proto.setFetchOptions = function (options) {
			if (!this._fetchOptions) this._fetchOptions = [];
			if (!_.isArray(this._fetchOptions)) this._fetchOptions = [ this._fetchOptions ];
			this._fetchOptions.unshift(options); // Place at first of array to give precedence over previous entries
		};
		
		proto.fetch = function (options, bypassOptions) {
			var self = this;
			if (this._fetchOptions && !bypassOptions) {
				options = options || {};
				if (_.isArray(this._fetchOptions)) {
					_.each(this._fetchOptions, function (optionSet) {
						deepDefaults(options, _.isFunction(optionSet) ? optionSet.call(self) : optionSet);
					});
				} else {
					deepDefaults(options, _.isFunction(this._fetchOptions)
						? this._fetchOptions.call(self)
						: this._fetchOptions);
				}
			}
			fetchReference.call(this, options);
		}
		
	}
	
	attach(Backbone.Collection.prototype);
	attach(Backbone.Model.prototype);
	
})(this);
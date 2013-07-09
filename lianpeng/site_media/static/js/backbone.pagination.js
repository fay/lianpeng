/* 
 * backbone.pagination.js v0.9
 * Copyright (C) 2012 Philipp Nolte
 * backbone.pagination.js may be freely distributed under the MIT license.
 */

(function(window) {
  "use strict";

  // Alias backbone, underscore and jQuery.
  var Backbone = window.Backbone,
      _        = window._,
      $        = window.$;

  // Define the pagination enale method under the Pagination namespace.
  Backbone.Pagination = {

    // Called when enabling pagination on a Backbone.Collection.
    enable: function(collection, config) {
      _.extend(collection, Backbone.Pagination.Paginator)
      
      if (config) {
        collection.paginationConfig = config;
        _.defaults(collection.paginationConfig, Backbone.Pagination.Paginator.paginationConfig);
      }
    }
  };

  // Define all the pagination methods available.
  Backbone.Pagination.Paginator = {

    // The current page displayed -- defaults to page 1.
    currentPage: 1,

    // Pagination configuration can be overwritten anytime.
    paginationConfig: {
      pretty:       false,  // enable pretty urls url/page/2/ipp/20
      ipp:          20,     // items per page
      page_attr:    'page',
      ipp_attr:     'ipp',  // will result in a query like page=4&ipp=20
      fetchOptions: {}      // any options handed over to the fetch method
    },

    // Load the page number given.
    loadPage: function(page) {
      this.currentPage = (page > 0) ? page : 1;
      this.fetch(this.paginationConfig.fetchOptions);
    },

    // Load the next page.
    nextPage: function() {
      this.loadPage(this.currentPage +1);
    },

    // Load the previous page.
    previousPage: function() {
      this.loadPage(this.currentPage -1);
    },

    // The url function will append the page and ipp attribute to the result
    // of an baseUrl property or function (if it exists). Note, that
    // this url function will override any previous defined url function.
    url: function() {

      // Generate the preceding base of the url.
      var base = "";
      if (typeof this.baseUrl === 'function') {
        base += this.baseUrl();
      } else if (typeof this.baseUrl !== 'undefined') {
        base += this.baseUrl;
      }

      if (this.paginationConfig.pretty) {
        return base + '/'
          + this.paginationConfig.page_attr + '/' + this.currentPage + '/'
          + this.paginationConfig.ipp_attr + '/' + this.paginationConfig.ipp;
      }

      // Add the pagination params to the url.
      var params = {};
      params[this.paginationConfig.page_attr] = (this.currentPage - 1) * this.paginationConfig.ipp;
      params[this.paginationConfig.ipp_attr]  = this.paginationConfig.ipp;
      return base + ((base.indexOf('?') === -1) ? '?' : '&') + $.param(params);
    }

  }

  // Provide a PaginatedCollection constructor that extends Backbone.Collection.
  Backbone.PaginatedCollection = Backbone.Collection.extend(Backbone.Pagination.Paginator);

})(this);

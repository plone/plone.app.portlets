define([
  'jquery',
  'mockup-patterns-base',
  'pat-registry',
  'mockup-utils',
  'mockup-patterns-modal',
  'translate',
  'jquery.form'
], function ($, Base, Registry, utils, Modal, _t) {
  'use strict';
  var ManagePortlets = Base.extend({
    name: 'manage-portlets',
    trigger: '.pat-manage-portlets',
    messageTimeout: 0,
    isModal: false,
    dirty: false,
    init: function(){
      var that = this;
      var $modal = that.$el.parents('.plone-modal');
      if($modal.size() === 1){
        this.isModal = true;
        /* want to do something on exit from modal now */
        var modal = $modal.data('pattern-plone-modal');
        modal.on('hide', function(){
          if(that.dirty){
            window.location.reload();
          }
        });
      }
      that.bind();
    },
    bind: function(){
      var that = this;
      that.setupAddDropdown();
      that.setupSavePortletsSettings();
      that.setupPortletEdit();
    },
    rebind: function($el){
      this.$el.replaceWith($el);
      this.$el = $el;
      this.bind();
      this.statusMessage();
      this.dirty = true;
    },
    statusMessage: function(msg){
      if(msg === undefined){
        msg = _t("Portlet changes saved");
      }
      var that = this;

      var $message = $('#portlet-message');
      if($message.size() === 0){
        $message = $('<div class="portalMessage info" id="portlet-message" style="display:none"></div>');
        if(that.isModal){
          $('.plone-modal-body:visible').prepend($message);
        }else{
          $('#content-core').prepend($message);
        }
      }
      $message.html('<strong>' + _t("Info") + '</strong>' + msg);
      clearTimeout(that.messageTimeout);
      if(!$message.is(':visible')){
        $message.fadeIn();
      }
      that.messageTimeout = setTimeout(function(){
        $message.fadeOut();
      }, 3000);
    },
    showEditPortlet: function(url){
      var that = this;
      var $a = $('<a/>');
      $('body').append($a);
      var pattern = new Modal($a, {
        ajaxUrl: url,
        actionOptions: {
          displayInModal: false,
          reloadWindowOnClose: false,
          isForm: true,
          onSuccess: function(modal, html){
            pattern.hide();
            var $body = $(utils.parseBodyTag(html));
            that.rebind($('#' + that.$el.attr('id'), $body));
            that.statusMessage(_t('Portlet added'));
          }
        }
      });
      pattern.on('after-render', function(){
        var $el = $('#' + that.$el.attr('id'), pattern.$raw);
        /* this is a check that the add form doesn't just automatically
           create the portlet without an actual form.
           If element is found here, we can short circuit and
           continue on. */
        if($el.size() === 1){
          /* hacky, trying to prevent modal parts from flickering here */
          $el = $el.clone();
          pattern.on('shown', function(){
            pattern.hide();
          });
          that.rebind($el);
          that.statusMessage(_t('Portlet added'));
        }
      });
      pattern.show();
    },
    setupPortletEdit: function(){
      var that = this;
      $('.managedPortlet .portletHeader > a', that.$el).click(function(e){
        e.preventDefault();
        that.showEditPortlet($(this).attr('href'));
      });
    },
    setupAddDropdown: function(){
      var that = this;
      $('.add-portlet', that.$el).change(function(e){
        e.preventDefault();
        var $select = $(this);
        var $form = $select.parents('form');
        var contextUrl = $select.attr('data-context-url');
        var url = contextUrl + $select.val() +
          '?_authenticator=' + $('[name="_authenticator"]').val() +
          '&referer=' + $('[name="referer"]', $form).val();
        that.showEditPortlet(url);
      });
    },
    setupSavePortletsSettings: function(){
      var that = this;
      $('.portlets-settings,form.portlet-action', that.$el).ajaxForm(function(html){
        var $body = $(utils.parseBodyTag(html));
        that.rebind($('#' + that.$el.attr('id'), $body));
      });
      $('.portlets-settings select', that.$el).change(function(){
        $('.portlets-settings', that.$el).submit();
      });
    }
  });

  return ManagePortlets;
});
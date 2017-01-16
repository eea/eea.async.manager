if(window.toggleSelect === undefined){
    var toggleSelect = function (elem, selector) {
      var checkboxes = [].slice.call(document.querySelectorAll('input[type=checkbox][name="' + selector + '"]'));
      checkboxes.forEach(function(checkbox){
         checkbox.checked = elem.checked;
      });
    };
}

if(window.EEA === undefined){
  var EEA = {
    who: 'eea.async.manager',
    version: '1.0'
  };
}

EEA.AsyncManagerJob = function (context, options) {
  var self = this;
  self.context = context;
  self.settings = {};

  if(options){
    jQuery.extend(self.settings, options);
  }

  self.initialize();
};

EEA.AsyncManagerJob.prototype = {
  initialize: function(){
    var self = this;

    self.context.click(function(){
      self.contextClick();
    });

    self.context.click();
  },

  contextClick: function () {
      var self = this;
      self.context.find(".job-details").toggle();
  }
};


jQuery.fn.EEAsyncManagerJob = function(options){
  return this.each(function(){
    var context = jQuery(this);
    var adapter = new EEA.AsyncManagerJob(context, options);
    context.data('EEAsyncManagerJob', adapter);
  });
};

jQuery(document).ready(function() {
    // Select all
    jQuery('.select-all').click(function(){
        toggleSelect(this, 'ids:list');
    });

    // Job Results details
    var jobs = jQuery('.async-manager-jobs tr');
    if(jobs.length){
        jobs.EEAsyncManagerJob();
    }
});

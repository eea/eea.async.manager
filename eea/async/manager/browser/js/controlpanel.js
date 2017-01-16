if(window.EEA === undefined){
  var EEA = {
    who: 'eea.async.manager',
    version: '1.0'
  };
}

/* 
** Async Manager Job  
*/

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
      self.toggleSummary();
      self.toggleDetails();
    });

    self.toggleDetails();
  },

  toggleDetails: function () {
      var self = this;
      self.context.find(".job-details").toggle();
  },
  
  toggleSummary: function() {
    var self = this;
    self.context.find(".job-summary").toggle();
  }
};

// jQuery plugin for Job
jQuery.fn.EEAsyncManagerJob = function(options){
  return this.each(function(){
    var context = jQuery(this);
    var adapter = new EEA.AsyncManagerJob(context, options);
    context.data('EEAsyncManagerJob', adapter);
  });
};


/* 
** Async Manager Table
*/
EEA.AsyncManagerTable = function(context, options){
  var self = this;
  self.context = context;
  self.settings = {};

  if(options){
    jQuery.extend(self.settings, options);
  }

  self.initialize();
};

EEA.AsyncManagerTable.prototype = {
  initialize: function(){
    var self = this;
    
    self.context.find('.select-all').click(function(){
      self.toggleSelect(this);
    });
  },
  
  toggleSelect: function(elem){
    var self = this;
    self.context.find(self.settings.selector).each(function(){
      if(!this.disabled){
        this.checked = elem.checked;
      }
    });
  }
};

// jQuery plugin for Table
jQuery.fn.EEAsyncManagerTable= function(options){
  return this.each(function(){
    var context = jQuery(this);
    var adapter = new EEA.AsyncManagerTable(context, options);
    context.data('EEAsyncManagerTable', adapter);
  });
};


/*
** Init 
*/
jQuery(document).ready(function() {

    // Table
    var table = jQuery('.async-manager-table');
    if(table.length){
      table.EEAsyncManagerTable({selector: "[name='ids:list']"});
    }

    // Job Results details
    var jobs = jQuery('.async-manager-jobs tr');
    if(jobs.length){
        jobs.EEAsyncManagerJob();
    }
});

(function () {

var
  V = envision;

// Only markers for the first serie
var series_drawn;
var series_number;


// Custom data processor
function processData (options) {
    
  return;

  var
    resolution = options.resolution;

  options.preprocessor
    .bound(options.min, options.max)
    .subsampleMinMax(resolution + Math.round(resolution / 3));
}

function getDefaultsMarkersSummary (option, markers, dates) {
    var mark = "";
    for (var i=0; i<markers.date.length; i++) {
        if (markers.date[i] == dates[option.index]) {
            mark = markers.marks[i];
        }
    }
    return mark;
}

// Only show markers with the first graph
function getDefaultsMarkers (option, markers, dates) {
    var mark = "";
    for (var i=0; i<markers.date.length; i++) {
        if (markers.date[i] == dates[option.index]) {
            mark = markers.marks[i];
            if (series_drawn != 0) mark="";
            // Last mark?
            if (i == markers.date.length-1) {
                series_drawn++;
                // Last series? Reset initial status
                if (series_drawn == series_number) {
                    series_drawn = 0;
                }
            }
        }
    }
    return mark;
}

function getDefaults (markers, dates) {
    var defaults_colors = ['#ffa500', '#ffff00', '#00ff00', '#4DA74D', '#9440ED'];
  return {
    commits : {
      name : 'milestone0-scm-commits',
      config : {
        colors: defaults_colors,
        'lite-lines' : {          
          lineWidth : 1,
          show : true,
          fill : true,
          fillOpacity : 0.5,
          /* color: '#ffa500',
          fillColor: '#ffa500' */
        },               
        'markers': {
            show: true,
            position: 'ct',
            labelFormatter: function (o) {
                return getDefaultsMarkers (o, markers, dates);
            }
          },
        mouse : {
          track: true,
          trackY: false,
          trackDecimals: 4,
          position: 'ne'
        },
        yaxis : {
          show: true,
          autoscale : true,
          autoscaleMargin : 0.05,
          noTicks : 3,
          showLabels : true,
          min : 0
        },
        legend : {
            show: false,
            position : 'nw',
            noColumns : 1,
            backgroundColor : '#FFFFFF', // A light blue background color
            backgroundOpacity: 0,

        },
      },
      processData : processData
    },
    files : {
        name : 'milestone0-scm-files',
        config : {
            colors: defaults_colors,
          'lite-lines' : {
            lineWidth : 1,
            show : true,
            fill : true,
            fillOpacity : 0.2
          },
          mouse : {
            track: true,
            trackY: false,
            trackAll: true,
            sensibility: 1,
            trackDecimals: 4,
            position: 'ne'
          },
          yaxis : { 
            autoscale : true,
            autoscaleMargin : 0.05,
          }
        },
        processData : processData
      },
      branches : {
          name : 'milestone0-scm-branches',
          config : {
            colors: defaults_colors,
            'lite-lines' : {
              lineWidth : 1,
              show : true,
              fill : true,
              fillOpacity : 0.2,
            },
            mouse : {
              track: true,
              trackY: false,
              trackAll: true,
            },
            yaxis : { 
              autoscale : true,
              autoscaleMargin : 0.05,
              min : 0
            }
          },
          processData : processData
      },
      committers : {
        name : 'milestone0-scm-committers',
        config : {
            colors: defaults_colors,
            whiskers : {
              show : true,
              lineWidth : 2
        },
        mouse: {
          track: true,
          trackY: false,
          trackAll: true
        },
        yaxis : {
          autoscale : true,
          autoscaleMargin : 0.5 
        }
      },
      processData : processData
    },
    repositories : {
        name : 'milestone0-scm-repositories',
        config : {
          colors: defaults_colors,
          whiskers : {
            show : true,
            lineWidth : 2
          },
          mouse: {
            track: true,
            trackY: false,
            trackAll: true
          },
          yaxis : {
            autoscale : true,
            autoscaleMargin : 0.5 
          },
        },
        processData : processData
      },    
    summary : {
      name : 'milestone0-scm-summary',
      config : {
        colors: defaults_colors,
        'lite-lines' : {
          show : true,
          lineWidth : 1,
          fill : true,
          fillOpacity : 0.2,
          fillBorder : true
        },
        xaxis : {
          noTicks: 10,
          showLabels : true,
        },
        yaxis : {
          autoscale : true,
          autoscaleMargin : 0.1
        },
        handles : {
          show : true
        },
        selection : {
          mode : 'x'
        },
        grid : {
          verticalLines : false
        },
        'markers': {
            show: true,
            position: 'cm',
            labelFormatter: function (o) {
                return getDefaultsMarkersSummary (o, markers, dates);
            }
          },
      },      
    },
    connection : {
      name : 'milestone0-scm-connection',
      adapterConstructor : V.components.QuadraticDrawing
    }
  };
}

function SCM_Milestone0 (options) {

  var
    data = options.data,
    defaults = getDefaults(data.markers, data.dates),
    vis = new V.Visualization({
        name : 'milestone0-scm',
        }),
    selection = new V.Interaction(),
    hit = new V.Interaction(),
    commits, committers, connection, summary, 
    files, branches, repositories, markers ;

  if (options.defaults) {
    defaults = Flotr.merge(options.defaults, defaults);
  }

  // Data for plotting the graphs
  // Legend won't show correctly inside Allura
  /* defaults.branches.data = [{label:"branches",data:data.branches}];
  defaults.commits.data = [{label:"commits", data: data.commits}];
  defaults.committers.data = [{label:"committers",data:data.committers}];
  defaults.files.data = [{label:"files",data:data.files}];
  defaults.repositories.data = [{label:"repositories",data:data.repositories}]; */
  
  defaults.branches.data = data.branches;
  defaults.commits.data = data.commits;
  defaults.committers.data = data.committers;
  defaults.files.data = data.files;
  defaults.repositories.data = data.repositories;

  
  defaults.summary.data = data.summary;
  series_number = defaults.commits.data.length;
  series_drawn = 0;

  
  defaults.commits.config.mouse.trackFormatter = options.trackFormatter;
  
  if (options.xTickFormatter) {
    defaults.summary.config.xaxis.tickFormatter = options.xTickFormatter;
  }
  defaults.commits.config.yaxis.tickFormatter = options.yTickFormatter || function (n) {
    return '$' + n;
  };

  branches = new V.Component(defaults.branches);
  commits = new V.Component(defaults.commits);
  committers = new V.Component(defaults.committers);
  files = new V.Component(defaults.files);
  repositories = new V.Component(defaults.repositories);
  
  connection = new V.Component(defaults.connection);  
  summary = new V.Component(defaults.summary);  

  // Render visualization
  vis
    .add(commits)
    .add(committers)
    /* .add(branches)
    .add(files)
    .add(repositories) */
    .add(connection)
    .add(summary)
    .render(options.container);

  // Define the selection zooming interaction
  selection
    .follower(commits)
    .follower(committers)
    /* .follower(branches)
    .follower(files)
    .follower(repositories) */
    .follower(connection)
    .leader(summary)
    .add(V.actions.selection, options.selectionCallback ? { callback : options.selectionCallback } : null);

  // Define the mouseover hit interaction
  hit    
    .group([commits, committers]) //, branches, files, repositories])
    .add(V.actions.hit);

  // Optional initial selection
  if (options.selection) {
    summary.trigger('select', options.selection);
  }

  // Members
  this.vis = vis;
  this.selection = selection;
  this.hit = hit;
  this.commits = commits;
  this.committers = committers;
  this.branches = branches;
  this.files = files;
  this.repositories = repositories;
  this.summary = summary;
}

V.templates.SCM_Milestone0 = SCM_Milestone0;

})();
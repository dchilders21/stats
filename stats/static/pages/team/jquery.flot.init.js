/**
 * Theme: Minton Admin Template
 * Author: Coderthemes
 * Module/App: Flot-Chart
 */

! function($) {
	"use strict";

	var FlotChart = function() {
		this.$body = $("body")
		this.$realData = []
	};

	//creates plot graph
	FlotChart.prototype.createPlotGraph = function(selector, data1, data2, labels, colors, borderColor, bgColor) {
		//shows tooltip
		function showTooltip(x, y, contents) {
			$('<div id="tooltip" class="tooltipflot">' + contents + '</div>').css({
				position : 'absolute',
				top : y + 5,
				left : x + 5
			}).appendTo("body").fadeIn(200);
		}


		$.plot($(selector), [{
			data : data1,
			label : labels[0],
			color : colors[0]
		}, {
			data : data2,
			label : labels[1],
			color : colors[1]
		}], {
			series : {
				lines : {
					show : true,
					fill : true,
					lineWidth : 1,
					fillColor : {
						colors : [{
							opacity : 0.5
						}, {
							opacity : 0.5
						}]
					}
				},
				points : {
					show : true
				},
				shadowSize : 0
			},

			grid : {
				hoverable : true,
				clickable : true,
				borderColor : borderColor,
				tickColor : "#f9f9f9",
				borderWidth : 1,
				labelMargin : 10,
				backgroundColor : bgColor
			},
			legend : {
				position : "ne",
				margin : [0, -24],
				noColumns : 0,
				labelBoxBorderColor : null,
				labelFormatter : function(label, series) {
					// just add some space to labes
					return '' + label + '&nbsp;&nbsp;';
				},
				width : 30,
				height : 2
			},
			yaxis : {
				tickColor : '#f5f5f5',
				font : {
					color : '#bdbdbd'
				}
			},
			xaxis : {
				tickColor : '#f5f5f5',
				font : {
					color : '#bdbdbd'
				}
			},
			tooltip : true,
			tooltipOpts : {
				content : '%s: Value of %x is %y',
				shifts : {
					x : -60,
					y : 25
				},
				defaultTheme : false
			}
		});
	},
	//end plot graph

	//initializing various charts and components
	FlotChart.prototype.init = function() {

	    var appElement = document.querySelector('[ng-app=statsApp]');
        var appScope = angular.element(appElement).scope();
        var controllerScope = appScope.$$childHead;
        var data = controllerScope.team.data.data;

        //plot graph data
        // Default will be 'total_pts'
        var stats = data['features']['total_pts'];
		var opp_stats = data['opp_features']['total_pts'];
		var plabels = ["Visits", "Pages/Visit"];
		var pcolors = ['#00b19d', '#3bafda'];
		var borderColor = '#f5f5f5';
		var bgColor = '#fff';
		this.createPlotGraph("#website-stats", stats, opp_stats, plabels, pcolors, borderColor, bgColor);

	},

	//init flotchart
	$.FlotChart = new FlotChart, $.FlotChart.Constructor =
	FlotChart

}(window.jQuery),

//initializing flotchart
function($) {
	//"use strict";
	//$.FlotChart.init()
}(window.jQuery);

var initFlot = function($) {
    "use strict";
	$.FlotChart.init()
};

var changeFlot = function(feature, $) {
    console.log(feature)

    "use strict";

    var appElement = document.querySelector('[ng-app=statsApp]');
    var appScope = angular.element(appElement).scope();
    var controllerScope = appScope.$$childHead;
    var data = controllerScope.team.data.data;
    // Default will be 'total_pts'
    var stats = data['features'][feature];
    var opp_stats = data['opp_features'][feature];
    var plabels = ["Visits", "Pages/Visit"];
    var pcolors = ['#00b19d', '#3bafda'];
    var borderColor = '#f5f5f5';
    var bgColor = '#fff';
    $.FlotChart.createPlotGraph("#website-stats", stats, opp_stats, plabels, pcolors, borderColor, bgColor);

    /*$.plot("#website-stats", [{
        data : [[1.0, 38], [2.0, 32], [3.0, 35], [4.0, 36], [5.0, 43]]
    }, {
        data : [[1.0, 21], [2.0, 19], [3.0, 16], [4.0, 13], [5.0, 14]]
    }]);*/

}

$(document).ready(function() {

});


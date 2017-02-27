'use strict';

angular.module('statsApp')
    .controller('TeamCtrl', ['$scope', '$http', '$routeParams',
        function ($scope, $http, $routeParams) {

          var s = this;
          this.data = '';
          this.features;
          this.team;
          this.opponents = [];
          this.stat;
          this.teamColor = '00b19d'; // default

          this.set_features = function() {

                s.features = Object.keys(s.data.data['features']);
                s.team = s.data.data['team'];
                s.stat = 'total_pts';

                for (var key in s.data.data['opp']){
                    s.opponents.push(s.data.data['opp'][key])
                }
                //console.log(s.opponents)
                //console.log(s.features);

          };

          this.changeFlot = function (feature) {
            changeFlot(feature, window.jQuery);
          }



          $http.get('http://0.0.0.0:5000/api/team/' + $routeParams.teamId)
          .then(function (resp)
			{

			  s.data=resp;
			  s.set_features();

			  $http.get('/static/json/team_colors.json')
                  .then(function (resp)
                    {
                        s.teamColor = '#' + resp.data[s.team][0];
                        //initializing flotchart
                        initFlot(window.jQuery);
                    }, function (err)
                    {
                        console.log('json failed');
                    });

			}, function (err)
			{
				console.log('GET failed');
			});

        }
]);
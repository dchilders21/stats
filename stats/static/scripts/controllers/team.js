'use strict';

angular.module('statsApp')
    .controller('TeamCtrl', ['$scope', '$http', '$routeParams',
        function ($scope, $http, $routeParams) {

          console.log(this);
          var s = this;
          this.data = '';
          this.features;

          this.features = 'wtf';


          this.done = function(resp) {
              s.data=resp;
              s.set_features();
              //initializing flotchart
              initFlot(window.jQuery);
          };

          this.fail = function(err){
            console.log('GET failed');
          };

          this.set_features = function() {
                s.features = Object.keys(s.data.data['features']);
                console.log(s.features);

          };

          this.changeFlot = function (feature) {
            changeFlot(feature, window.jQuery);
          }

          $http.get('http://0.0.0.0:5000/api/team/' + $routeParams.teamId)
          .then(this.done, this.fail);

        }
]);
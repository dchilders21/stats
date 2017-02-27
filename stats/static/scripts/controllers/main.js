'use strict';

angular.module('statsApp')
    .controller('MainCtrl', ['$scope', '$http',
        function ($scope, $http) {

          $scope.username = 'World';

          var done=function(resp){
              $scope.data=resp.data['data'];
              console.log($scope.data);
              console.log('got response');
          };

          var fail=function(err){
            console.log('failed');
          };

          //$http.get('http://0.0.0.0:5000/api')
          $http.get('/api')
          .then(done, fail);

          console.log('we definitely in here');
        }
]);
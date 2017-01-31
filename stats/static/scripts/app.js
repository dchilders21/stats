'use strict';   // See note about 'use strict'; below

var statsApp = angular.module('statsApp', [
 'ngRoute',
]);

statsApp.config(['$routeProvider',
     function($routeProvider) {
         $routeProvider.
             when('/', {
                 templateUrl: '/static/partials/main.html',
                 controller: 'MainCtrl',
                 controllerAs: 'main'
             }).
             otherwise({
                 redirectTo: '/'
             });
    }]);

/*statsApp.controller("MainCtrl", function ($scope) {
    console.log('we in here');
    $scope.msg = "I love London";
});*/

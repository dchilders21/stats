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
             when('/team/:teamId', {
                 templateUrl: '/static/partials/team.html',
                 controller: 'TeamCtrl',
                 controllerAs: 'team'
             }).
             otherwise({
                 redirectTo: '/'
             });
    }]);

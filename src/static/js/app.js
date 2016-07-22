var app = angular.module("MatchApp", []);

app.controller("MatchController", function($scope) {
    console.log('------====---=======----');
    $scope.greetings = ["Milk", "Bread", "Cheese"];

    $scope.init = function(teams) {
        console.log(' ========== ');
        $scope.teams = teams;
        console.log(typeof($scope.teams))
    }
});


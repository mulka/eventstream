var myApp = angular.module('myApp',[]);

myApp.controller('TweetListCtrl', function($scope) {
  $scope.tweets = [];

  function openWS(messageContainer) {
    ws = new WebSocket("ws://localhost:8888/ws");
    ws.onmessage = function(e) {
      var data = JSON.parse(e.data);
      $scope.tweets.push(data);
      if ($scope.tweets.length > 10){
        $scope.tweets.shift();
      }
      $scope.$apply();
    };
    ws.onclose = function(e) {
      openWS(messageContainer);
    };
  }

  openWS();
});
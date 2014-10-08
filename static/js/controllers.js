var myApp = angular.module('myApp',[]);

myApp.controller('TweetListCtrl', function($scope) {
  $scope.tweets = [];

  function openWS(messageContainer) {
    ws = new WebSocket("ws://" + window.location.host + "/ws");
    ws.onmessage = function(e) {
      var data = JSON.parse(e.data);
      $scope.tweets.push(data);
      $scope.$apply();
    };
    ws.onclose = function(e) {
      openWS(messageContainer);
    };
  }

  openWS();
});
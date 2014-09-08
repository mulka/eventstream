var myApp = angular.module('myApp',['ngAnimate']);

function link_it_up (tweet) {
  var html = tweet.text;
  var replacements = [];

  angular.forEach(tweet.entities, function(entities, entity_type){
    if (['hashtags', 'user_mentions', 'urls', 'media'].indexOf(entity_type) > -1){
      angular.forEach(entities, function(entity) {
        var generic_entity = {
          'indices': entity.indices
        };
        var url = '#';
        var title = null;
        if (entity_type == 'hashtags'){
          url = 'https://twitter.com/search?q=%23' + entity.text;
        } else if (entity_type == 'user_mentions') {
          url = 'https://twitter.com/' + entity.screen_name;
        } else if (entity_type == 'urls' || entity_type == 'media') {
          url = entity.url;
          title = entity.expanded_url;
          generic_entity.text = entity.display_url;
        }

        generic_entity['before'] = '<a href="' + url + '" target="_blank"';
        if (title !== null) {
          generic_entity['before'] = generic_entity['before'] + ' title="' + title + '"';
        }
        generic_entity['before'] = generic_entity['before'] + '>';
        generic_entity['after'] = '</a>';
        replacements.push(generic_entity);

      });
    }

  });

  replacements.sort(function (a, b){ return a.indices[0]-b.indices[0];});

  var offset = 0;

  angular.forEach(replacements, function (replacement) {
    var old_text = html.slice(replacement.indices[0] + offset, replacement.indices[1] + offset);
    var new_text = null;
    if ('text' in replacement) {
      new_text = replacement.text;
    } else {
      new_text = old_text;
    }
    html = html.slice(0, replacement.indices[0] + offset)
      + replacement.before + new_text + replacement.after
      + html.slice(replacement.indices[1] + offset);
    offset = offset + replacement.before.length - old_text.length + new_text.length + replacement.after.length;
  });
  return html;
};

myApp.controller('TweetListCtrl', function($scope, $sce) {
  $scope.tweets = [];

  function openWS(messageContainer) {
    ws = new WebSocket("ws://" + window.location.host + "/ws");
    ws.onmessage = function(e) {
      var data = JSON.parse(e.data);
      data['linked_up_text'] = $sce.trustAsHtml(link_it_up(data));
      $scope.tweets.push(data);
      if ($scope.tweets.length > 20){
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
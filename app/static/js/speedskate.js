function removeLocalRequest(id) {
  // Remove from user added ID's
  let userIndex = app.userAdded.indexOf(id);
  if (userIndex != -1) app.userAdded.splice(userIndex, 1);
  // Remove from request list
  app.queue = app.queue.filter(function(skate) {
    return skate.id != id;
  });
}

function pushLocalRequest(request) {
  request.time = new Date(Date.parse(request.time));
  app.queue.push(request);
}

var socket = io();

var app = new Vue({
  el: '#app',
  delimiters: ['[[', ']]'],
  data: {
    connected: false,
    updateTimer: null,
    queue: [],
    userAdded: [],
    enteredSize: null,
    enteredAge: 'adult',
    enteredType: 'figure'
  },
  computed: {
    unstagedQueue: function() {
      return this.queue.filter(function(skate) {
        return skate.status == 0;
      });
    },
    stagedQueue: function() {
      return this.queue.filter(function(skate) {
        return skate.status == 1;
      });
    }
  },
  created: function() {
    this.updateTimer = setInterval(this.computeTimes, 1000);
  },
  beforeDestroy: function() {
    clearInterval(this.updateTimer);
  },
  methods: {
    setAge:  function(skateAge)  { this.enteredAge  = skateAge;  },
    setType: function(skateType) { this.enteredType = skateType; },
    skateClass: function(skate) {
      // Red border if request time is 2 minutes or greater
      let dangerBorder = skate.requestTime >= 120000;

      switch(skate.type) {
        case 'figure':
          return { 'bg-light': true, 'border-danger': dangerBorder };
        case 'hockey':
          return { 'bg-dark': true, 'text-white': true, 'border-danger': dangerBorder };
        case 'speed':
          return { 'bg-secondary': true, 'text-white': true, 'border-danger': dangerBorder };
      }
    },
    skateString: function(skate) {
      switch(skate.type) {
        case 'figure':
          return 'Figure skate';
        case 'hockey':
          return 'Hockey skate';
        case 'speed':
          return 'Speedskate';
      }
    },
    computeTimes: function() {
      let currentTime = new Date();
      for (let i = 0; i < this.queue.length; i++) {
        // Format time and redisplay
        this.$set(this.queue[i], 'requestTime', new Date(currentTime - this.queue[i].time));
      }
    },
    formatTime: function(time) {
      if (time) {
        let seconds = time.getSeconds();
        if (seconds < 10) seconds = '0' + seconds;
        return `${time.getMinutes()}:${seconds}`;
      }
    },
    submitRequest: function() {
      socket.emit('addRequest', {
        size: this.enteredSize,
        age:  this.enteredAge,
        type: this.enteredType,
        time: new Date().toISOString()
      });
    },
    cancelRequest: function(id) {
      socket.emit('cancelRequest', id);
    },
    changeState: function(id, state) {
      socket.emit('changeState', {
        id:    id,
        state: state
      });
    }
  }
});

socket.on('connect', function() {
  app.connected = true;
});

socket.on('disconnect', function() {
  app.connected = false;
});

// Authorisation failed
socket.on('denyRequest', function() {
  window.location.replace('/login');
});

socket.on('overrideQueue', function(queue) {
  queue.forEach(function(request) {
    pushLocalRequest(request);
  });
});

socket.on('addSuccess', function(id) {
  app.userAdded.push(id);

  // Reset form data
  app.enteredSize = null;
  app.enteredAge  = 'adult';
  app.enteredType = 'figure';

  // Reset form display
  $('.active').removeClass('active');
  $('#adultAge').parent().addClass('active');
  $('#figureType').parent().addClass('active');
});

socket.on('pubRequest', function(request) {
  pushLocalRequest(request);
  app.computeTimes();
});

socket.on('pubState', function(data) {
  if (data.state == 2) removeLocalRequest(data.id);
  else {
    for (var i = 0; i < app.queue.length; i++) {
      if (app.queue[i].id == data.id) break;
    }
    app.$set(app.queue[i], 'status', data.state);
  }
});

socket.on('deleteRequest', function(id) {
  removeLocalRequest(id);
});

$(document).ready(function() {
  $('[data-toggle="tooltip"]').tooltip();
});

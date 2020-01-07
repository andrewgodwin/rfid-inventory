import modal from "./components/modal.js";

var app = new Vue({
  components: {
    modal,
  },

  // app initial state
  data: {
    items: window.checklistData,
    lastReceived: null,
    state: null,
  },

  // Save items whenever they change
  watch: {
    items: {
      handler: function (items) {
        this.debouncedSave();
      },
      deep: true
    }
  },

  methods: {
    // Splits comma-separated strings
    splitcomma: function (value) {
      return value.split(",");
    },

    // Toggles an item between checked and unchecked
    toggleItem: function (item) {
      if (item.heading) return;
      if (item.skipped) {
        item.skipped = false;
        item.checked = true;
      } else {
        item.checked = !item.checked;
      }
    },

    // Sets an item to skipped
    skipItem: function (item) {
      if (item.heading) return;
      item.skipped = !item.skipped;
      item.checked = false;
    },

    // Sends the current value of items to the backend
    save: function() {
      if (!this.dragging && !_.isEqual(this.items, this.lastReceived)) {
        this.state = "saving";
        axios.post(".", {items: this.items},  {xsrfCookieName: "csrftoken", xsrfHeaderName: "X-CSRFToken"}).then((response) => {
          this.state = "saved";
          this.lastReceived = response.data.items;
          this.items = _.cloneDeep(response.data.items);
        });
      }
    }
  },

  created: function () {
    this.debouncedSave = _.debounce(this.save, 500);
  },

})

// Mount to element
app.$mount('.content')

// Debugging
window.app = app;

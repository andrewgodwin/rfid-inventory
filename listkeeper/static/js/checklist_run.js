import modal from "./components/modal.js";

var app = new Vue({
  components: {
    modal,
  },

  // app initial state
  data: {
    items: window.checklistData,
    serverItems: null,
    state: null,
    filter: null,
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

  computed: {
    filteredItems: function () {
      if (this.filter == "unchecked") {
        return this.items.filter((item) => { return item.checked == false && item.skipped == false; });
      } else {
        return this.items;
      }
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

    // Saves state to the backend
    save: function () {
      // Is there a change to save?
      if (!_.isEqual(this.items, this.serverItems) && this.state != "saving" && this.state != "loading") {
        this.state = "saving";
        axios.post(".", {items: this.items},  {xsrfCookieName: "csrftoken", xsrfHeaderName: "X-CSRFToken"}).then((response) => {
          this.state = "saved";
          this.serverItems = _.cloneDeep(this.items);
          this.load();
        }).catch((error) => {
          // handle error
          console.log("Save error: " + error);
        });;
      }
    },

    // Loads state from the backend
    load: function () {
      if (this.state == "saving" || this.state == "loading") return;
      // Try saving
      this.save();
      // OK, just load
      this.state = "loading";
      axios.get("json/").then((response) => {
        this.state = "";
        // See if they changed the content while we were loading
        if (!_.isEqual(this.items, this.serverItems)) {
          this.save();
        } else {
          if (!_.isEqual(this.items, response.data.items)) {
            this.serverItems = _.cloneDeep(response.data.items);
            this.items = response.data.items;
          }
        }
      }).catch((error) => {
        // handle error
        console.log("Load error: " + error);
      });;
    }
  },

  created: function () {
    this.debouncedSave = _.debounce(this.save, 2000);
  },

  mounted: function () {
    this.serverItems = _.cloneDeep(this.items);
    window.setInterval(this.load, 5000);
  },

})

// Mount to element
app.$mount('.content')

// Debugging
window.app = app;

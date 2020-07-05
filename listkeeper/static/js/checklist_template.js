import modal from "./components/modal.js";

var app = new Vue({
  components: {
    modal,
    vuedraggable,
  },

  // app initial state
  data: {
    items: window.checklistData,
    serverItems: null,
    currentItem: null,
    showForm: false,
    tempId: 1,
    dragging: false,
    state: null,
    insertIndex: null,
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

    // Clears the form to a default state
    clearCurrent: function () {
      this.currentItem = { name: '', heading: false, quantity: 1, condition: "", labels: "", description: "" };
    },

    // Shows the form in an "add" state
    showAdd: function (index) {
      this.clearCurrent();
      this.showForm = true;
      this.$nextTick(() => {
        this.$refs.itemName.focus();
      })
      this.insertIndex = index;
    },

    // Shows the form in an "add" state with the heading
    showAddHeading: function () {
      this.showAdd();
      this.currentItem.heading = true;
    },

    // Shows the form in an "edit" state
    showEdit: function (item) {
      this.currentItem = item;
      this.showForm = true;
      this.$nextTick(() => {
        this.$refs.itemName.focus();
      })
    },

    // Adds the current edited item to the list
    saveItem: function () {
      var value = this.currentItem.name && this.currentItem.name.trim()
      if (!value) {
        return
      }
      // See if it's a new one or an existing one
      if (this.currentItem.id) {
        this.clearCurrent();
        this.showForm = false;
      } else {
        this.currentItem.id = "temp-" + (this.tempId++);
        if (this.insertIndex >= 0) {
          this.items.splice(this.insertIndex + 1, 0, this.currentItem);
        } else {
          this.items.push(this.currentItem);
        }
        this.clearCurrent();
        this.showForm = false;
        if (!this.insertIndex) {
          this.$refs.bottomBar.scrollIntoView();
        }
      }
    },

    // Deletes an item
    deleteItem: function (item) {
      this.items.splice(this.items.indexOf(item), 1);
    },

    // Called when drag starts, suppresses saves
    dragStart: function () {
      this.dragging = true;
    },

    // Called when drag ends, force-triggers save
    dragStop: function () {
      this.dragging = false;
      this.debouncedSave();
    },

    // Saves state to the backend
    save: function () {
      // Is there a change to save?
      if (!_.isEqual(this.items, this.serverItems) && this.state != "saving" && this.state != "loading") {
        this.state = "saving";
        axios.post(".", { items: this.items }, { xsrfCookieName: "csrftoken", xsrfHeaderName: "X-CSRFToken" }).then((response) => {
          this.state = "saved";
          this.serverItems = _.cloneDeep(this.items);
          this.load();
        }).catch((error) => {
          // handle error
          console.log("Save error: " + error);
        });
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
          console.log("Loading cancelled, save needed");
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
    this.debouncedSave = _.debounce(this.save, 500);
  },

  mounted: function () {
    this.serverItems = _.cloneDeep(this.items);
    this.clearCurrent();
    window.addEventListener("keyup", e => {
      if (e.code == "KeyI" && !this.showForm) {
        this.showAdd();
      } else if (e.code == "KeyH" && !this.showForm) {
        this.showAddHeading();
      }
    });
    window.setInterval(this.load, 10000);
  }

})

// Mount to element
app.$mount('.content')

// Debugging
window.app = app;

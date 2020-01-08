import modal from "./components/modal.js";

var app = new Vue({
  components: {
    modal,
    vuedraggable,
  },

  // app initial state
  data: {
    items: window.checklistData,
    lastReceived: null,
    currentItem: null,
    showForm: false,
    tempId: 1,
    dragging: false,
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

    // Clears the form to a default state
    clearCurrent: function () {
      this.currentItem = {name: '', heading: false, quantity: 1, condition: "", labels: "", description: ""};
    },

    // Shows the form in an "add" state
    showAdd: function () {
      this.clearCurrent();
      this.showForm = true;
      this.$nextTick(() => {
       this.$refs.itemName.focus();
      })
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
        this.items.push(this.currentItem);
        this.clearCurrent();
        this.showForm = false;
        this.$refs.bottomBar.scrollIntoView();
      }
    },

    // Deletes an item
    deleteItem: function(item) {
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

  mounted: function () {
    this.clearCurrent();
    window.addEventListener("keyup", e => {
      if (e.code == "KeyI" && !this.showForm) {
        this.showAdd();
      } else if (e.code == "KeyH" && !this.showForm) {
        this.showAddHeading();
      }
    });
  }

})

// Mount to element
app.$mount('.content')

// Debugging
window.app = app;

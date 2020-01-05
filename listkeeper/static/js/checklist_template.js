import Modal from "./components/modal.js";

var app = new Vue({
  components: {
    Modal,
  },

  // app initial state
  data: {
    items: [{name: "Heading", heading: true}, {name: "Item"}],
    currentItem: {name: '', heading: false},
    showForm: false
  },

  // Save items whenever they change
  watch: {
    items: {
      handler: function (items) {
        // save items here
      },
      deep: true
    }
  },

  methods: {
    // Clears the form to a default state
    clearCurrent: function () {
      this.currentItem = {name: '', heading: false};
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

    // Adds the current edited item to the list
    addItem: function () {
      var value = this.currentItem.name && this.currentItem.name.trim()
      if (!value) {
        return
      }
      this.items.push(this.currentItem);
      this.clearCurrent();
      this.showForm = false;
    },
  },

  mounted: function () {
    this.clearCurrent();
  }

})

// Mount to element
app.$mount('#template-editor')

// Debugging
window.app = app;

var deviceViewApp = new Vue({
    el: "#details",
    data: {tokenVisible: false},
    methods: {
        showToken: function () {
            this.tokenVisible = true;
        }
    }
});

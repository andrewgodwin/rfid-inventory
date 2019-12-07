var apiTokenApp = new Vue({
    el: "#api-details",
    data: {tokenVisible: false},
    methods: {
        showToken: function () {
            this.tokenVisible = true;
        }
    }
});

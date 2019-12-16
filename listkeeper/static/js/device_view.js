var deviceViewApp = new Vue({
    el: "#details",
    data: {tokenVisible: false},
    methods: {
        showToken: function () {
            this.tokenVisible = true;
        },
        loadData: function () {
            fetch('.?patch=1').then(function (response) {
                response.json().then(function (data) {
                    Object.keys(data).forEach(function (entryId) {
                        $("#" + entryId).html(data[entryId]);
                    });
                });
            });
        }
    },
    mounted: function () {
        setInterval(function () {
          this.loadData();
        }.bind(this), 3000);
    }
});

/** @odoo-module **/

import AbstractField from 'web.AbstractField';
import fieldRegistry from 'web.field_registry';

var LeasDefaultEchartsWidget = AbstractField.extend({
    template: "Leas_default_echarts",
    start: function(){
        this._super.apply(this, arguments);
        if (this.recordData[this.nodeOptions.currentValue]){
            this.value = this.recordData[this.nodeOptions.currentValue]
        }
    },
    _render: function() {
        var self = this;
        var value = this.value;


        const dataArray = JSON.parse(value);


        var chartContainer = this.$('.leas-bar-container')[0];
        if (this.attrs.options.width) {
            chartContainer.style.width = this.attrs.options.width + 'px';
        }else{
            chartContainer.style.width = '100%';
        }
        if (this.attrs.options.height) {
            chartContainer.style.height = this.attrs.options.height + 'px';
        }else{
            chartContainer.style.height = '100%';
        }
        var barChart
        if (this.attrs.options.dark) {
            barChart = echarts.init(chartContainer, 'dark');
        }else{
            barChart = echarts.init(chartContainer);
        }

        window.addEventListener('resize', function() {
            barChart.resize();
        });

        barChart.setOption(dataArray);
        if (!this.attrs.options.height || !this.attrs.options.width){
            setTimeout(function() {
                barChart.resize();
            }, 200);
        }




    },

})

fieldRegistry.add('leas_echarts', LeasDefaultEchartsWidget);

export default LeasDefaultEchartsWidget;

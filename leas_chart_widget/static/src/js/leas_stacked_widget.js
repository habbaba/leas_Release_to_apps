/** @odoo-module **/

import AbstractField from 'web.AbstractField';
import fieldRegistry from 'web.field_registry';

var LeasStackedWidget = AbstractField.extend({
    template: "LeasStackedWidget",
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
        var segmentData = dataArray.map(item => {
          return {
            value: item.value,
            name: item.name
          };
        });
        // console.log(segmentData);
        var totalValue = segmentData.reduce(function(acc, curr) {
          return acc + curr.value;
        }, 0);

        var baseColor = tinycolor("#71639e");
        var colorScheme = [];
        generateConsistentColorScheme(baseColor, segmentData.length)
        // console.log(colorScheme);
        var html_str = ''
        for (var i = 0; i < segmentData.length; i++) {
            const percentage = (segmentData[i].value / totalValue) * 100;
            const height = percentage + '%';
            const margin = i > 0 ? ' margin-top: 1px;' : '';
            html_str = html_str + '<div class="leas-bar-segment" style="height: '+height+'; background-color: '+colorScheme[i]+';'+ margin +'"><div class="leas-bar-segment-title">'+segmentData[i].name+':'+segmentData[i].value+'</div></div>'
        }
        this.$('.leas-bar-container').html(html_str);

        // 生成指定数量的保持一致的搭配和谐颜色方案
        function generateConsistentColorScheme(baseColor, count) {
          var angle = 360 / count;
          for (var i = 0; i < count; i++) {
            var hue = (baseColor.toHsl().h + i * angle) % 360;
            var color = tinycolor({ h: hue, s: baseColor.toHsl().s, l: baseColor.toHsl().l });
            colorScheme.push(color.lighten(15).saturate(35).toHexString());
          }
        }

    },
})

fieldRegistry.add('leas_stacked', LeasStackedWidget);

export default LeasStackedWidget;

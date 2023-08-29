/** @odoo-module **/

import AbstractField from 'web.AbstractField';
import fieldRegistry from 'web.field_registry';

var LeasStackedHBarWidget = AbstractField.extend({
    template: "LeasStackedHBar",
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
        dataArray.reverse()
        const categories = dataArray.map(item => item.category);
        const dynamicKeys = Object.keys(dataArray[0]).filter(key => key !== 'category');
        const dynamicData = dynamicKeys.map(key => {
          return {
            name: key,
            type: 'bar',
            stack: 'total',
            data: dataArray.map(item => item[key])
          };
        });
        var chartContainer = this.$('.leas-stacked-bar-container')[0];
        if (this.attrs.options.width) {
            chartContainer.style.width = this.attrs.options.width + 'px';
        }
        if (this.attrs.options.height) {
            chartContainer.style.height = this.attrs.options.height + 'px';
        }
        window.addEventListener('resize', function() {
            barChart.resize();
        });
        var barChart
        if (this.attrs.options.dark) {
            barChart = echarts.init(chartContainer, 'dark');
        }else{
            barChart = echarts.init(chartContainer);
        }

        const calculateRightValue = () => {
          const maxCategoryWidth = Math.max(
            ...categories.map(category => {
              const span = document.createElement('span');
              span.style.position = 'absolute';
              span.style.visibility = 'hidden';
              span.style.whiteSpace = 'nowrap';
              span.innerText = category;
              document.body.appendChild(span);
              const width = span.offsetWidth;
              document.body.removeChild(span);
              return width;
            })
          );

          const paddingLeft = 20; // 适当的左边间距
          return maxCategoryWidth + paddingLeft;
        };
        var option = {
          tooltip: {
            trigger: 'axis',
            axisPointer: {
              // Use axis to trigger tooltip
              type: 'line' // 'shadow' as default; can also be 'line' or 'shadow'
            }
          },
          legend: {
            show: false,
          },
          grid: {
            left: 0,
            right: calculateRightValue(),
            bottom: '0',
            top: '0',
          },
          xAxis: {
            type: 'value',
            show: false,
          },
          yAxis: {
            type: 'category',
            data: categories,
            position: 'right',
            show: this.attrs.options.show_catg || false,
          },
          series: dynamicData
        };
        barChart.setOption(option);
    },

})

fieldRegistry.add('leas_stackedHBar', LeasStackedHBarWidget);

export default LeasStackedHBarWidget;

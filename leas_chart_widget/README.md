
# Document Page

This Module Enables Displaying Data Charts Through Widget.

<!-- TOC -->
* [Document Page](#document-page)
  * [Effect](#effect)
  * [Example](#example)
      * [view-xml:](#view-xml)
      * [Recognizable Field Data:](#recognizable-field-data)
      * [Bug Tracker](#bug-tracker)
  * [Contributors & Maintainers](#contributors--maintainers)
<!-- TOC -->

## Effect
![](https://github.com/fenglander/leas_chart_widget/blob/main/static/description/Effect01.jpg?raw=true)

## Example
#### view-xml:
![](https://github.com/fenglander/leas_chart_widget/blob/main/static/description/Example01.jpg?raw=true)
````
widget="leas_echarts" options="{'dark': 1}"
    or
widget="leas_stackedHBar" options="{'width': 240, 'height': 150, 'show_catg': true}"
````
dark: To specify whether its dark mode.

height: Set Chart Height, Unit: px

width: Set Chart Width, Unit: px

#### Recognizable Field Data:
leas_stackedHBar:
````
[
    {
        "category": "Punching",
        "Available Quantity": 12.0,
        "In-Process Quantity": 0.0,
        "Completed Quantity": 0.0
    },
    {
        "category": "Sheet Metal",
        "Available Quantity": 0.0,
        "In-Process Quantity": 0.0,
        "Completed Quantity": 0.0
    },
    {
        "category": "Cutting Sheet",
        "Available Quantity": 0.0,
        "In-Process Quantity": 0.0,
        "Completed Quantity": 0.0
    },
]
````
leas_echarts:  

![](https://github.com/fenglander/leas_chart_widget/blob/main/static/description/Example02.png?raw=true)

This widget will directly hand over the JSON to ECharts for processing, so you just need to generate JSON that conforms to the ECharts format. For details, you can refer to https://echarts.apache.org/examples/.

Field Type Configuration:
````python
mo_Proc_chart_data = fields.Char('production Process', compute='_compute_Proc_chart_data')
````
#### Bug Tracker
Bugs are tracked on [GitHub Issues](https://github.com/fenglander/leas_chart_widget/issues>)  
If you encounter an issue, please check here to see if your problem has already been reported.  
If you are the first to discover the issue, please help us resolve it by providing detailed information.

## Contributors & Maintainers

* Fung <[32664699@qq.com](32664699@qq.com)>


# -*- coding: utf-8 -*-
{
    'name': "Leas Chart Widget",

    'summary': """
        Chart Widget Developed with ECharts""",

    'description': """
        Chart Widget Developed with ECharts
    """,

    'author': "Leas",
    'website': "http://www.leas.life",
    'images': ['static/description/widget_preview.gif'],
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '15.0.0.0',
    'license': 'OPL-1',
    'depends': ['base'],

    # always loaded
    'data': [
    ],
    'assets': {
        'web.assets_backend': {
            '/leas_chart_widget/static/src/css/leas_stacked_widget.css',
            '/leas_chart_widget/static/src/js/tinycolor-min.js',
            '/leas_chart_widget/static/src/js/leas_stacked_widget.js',
            '/leas_chart_widget/static/src/js/echarts.min.js',
            '/leas_chart_widget/static/src/js/leas_default_echarts_widget.js',
            '/leas_chart_widget/static/src/js/echarts_stacked_Horizontal_bar_widget.js',
        },
        'web.assets_qweb': {
            '/leas_chart_widget/static/src/xml/leas_stacked_widget.xml',
            '/leas_chart_widget/static/src/xml/echarts_stacked_Horizontal_bar_widget.xml',
            '/leas_chart_widget/static/src/xml/leas_default_echarts_widget.xml',
        },
    },
    'demo': [
        # 'demo/demo.xml',
    ],
    'application': True,
    'installable': True,
}

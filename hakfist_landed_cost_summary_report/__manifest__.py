{
    "name": "Landed Cost Summary Report",
    "version": "17.0.1.0.3",
    "description": "Landed Cost Summary Report",
    "summary": "Landed Cost Summary Report",
    "author": 'HAK FIST',
    "website": "https://www.hakfist.com",
    "license": "OPL-1",
    'maintainer': 'asn,prm',
    "depends": ['purchase_stock', 'stock_landed_costs', 'stock_account','hakfist_landed_cost_ext'],
    "data": [
        'report/report.xml',
        'report/landed_cost_summary_report.xml',
        'report/landed_cost_detailed_report.xml'
    ],
    'images': [
        'static/description/icon.png',
    ],
    "auto_install": False,
    "application": False,
}

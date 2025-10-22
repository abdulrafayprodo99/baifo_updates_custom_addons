{
    'name': 'Import Attendance',
    'version': '16.0.1.0.2',
    'sequence': -100,
    'author': 'Aneeq | Odolution',
    'depends': ['hr','hr_attendance'],
    'data':[
        'security/ir.model.access.csv',
        'views/import_attendance_view.xml',
        ],
    'assets': {
    },
    'application': True,
    'installable': True,
    'auto_install': False,
}

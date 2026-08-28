from src.image_generator import ImageGenerator


image_generator = ImageGenerator()
image_generator.generate_image("2.310", lessons=[{
        "date": "2026-05-01",
        "start_time": "0815",
        "end_time": "0940",
        "teacher": "SCJ",
        "subject": "IFT",
        "klasse": "BGT251",
        "code": 'regular',
        "room_changed": True,
        "anzahl": 2,
        "classroom": '2.310->2.311'
    }, {
        "date": "2026-05-01",
        "start_time": "1000",
        "end_time": "1130",
        "teacher": "MEL",
        "subject": "wir",
        "klasse": "BGT251",
        "code": 'regular',
        "room_changed": False,
        "anzahl": 2,
        "classroom": '2.310'
    }, {
        "date": "2026-05-01",
        "start_time": "1130",
        "end_time": "1315",
        "teacher": "PIR",
        "subject": "BInf",
        "klasse": "BGT251",
        "code": 'cancelled',
        "room_changed": False,
        "anzahl": 2,
        "classroom": '2.310'
    }, {
        "date": "2026-05-01",
        "start_time": "1315",
        "end_time": "1515",
        "teacher": "SEV",
        "subject": "Eng",
        "klasse": "BGT251",
        "code": 'regular',
        "room_changed": False,
        "anzahl": 2,
        "classroom": '2.310'
    }, {
        "date": "2026-05-01",
        "start_time": "1530",
        "end_time": "1700",
        "teacher": "WIB",
        "subject": "Deu LK",
        "klasse": "BGT251",
        "code": 'regular',
        "room_changed": False,
        "anzahl": 2,
        "classroom": '2.310'
    },
    {
        "date": "2026-05-01",
        "start_time": "1530",
        "end_time": "1700",
        "teacher": "WIB",
        "subject": "Deu LK",
        "klasse": "BGT251",
        "code": 'regular',
        "room_changed": False,
        "anzahl": 2,
        "classroom": '2.310'
    },
])

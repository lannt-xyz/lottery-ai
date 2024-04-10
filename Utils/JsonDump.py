import json
import os

lotMap = {
      0: ['tp-hcm', 'dong-thap', 'ca-mau']
    , 1: ['ben-tre', 'vung-tau', 'bac-lieu']
    , 2: ['dong-nai', 'can-tho', 'soc-trang']
    , 3: ['tay-ninh', 'an-giang', 'binh-thuan']
    , 4: ['vinh-long', 'binh-duong', 'tra-vinh']
    , 5: ['tp-hcm', 'long-an', 'binh-phuoc', 'hau-giang']
    , 6: ['tien-giang', 'kien-giang', 'da-lat']
}

lotMap_json = json.dumps(lotMap)
print (lotMap_json)
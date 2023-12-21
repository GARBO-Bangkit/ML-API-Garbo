URL = "https://ml-api-rhqpsup57q-uc.a.run.app/"

check api berjalan atau tidak
GET "URL/"
respons API is Running

register akun
POST "URL/register"
Body JSON yang akan dikirim
{
  "username": "helmi",
  "password": "12345678",
  "name": "Helmi Ahmad",
  "email": "helmi@gmail.com"
}

login akun
POST "URL/login"
Contoh Body JSON yang akan dikirim
{
"username": "sigit",
"password": "12345678"
}
resposn nya berupa access token

{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTcwMzE1NjQzNCwianRpIjoiMmJmM2NmNmYtZDhjZS00NWRlLWJmYzktODdmZDBmYjMwMmMxIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6InNpZ2l0IiwibmJmIjoxNzAzMTU2NDM0LCJjc3JmIjoiYWQ5MjhkYzAtMGMwZS00NmYwLTlmNDQtYTliNjFlOThmMDAzIiwiZXhwIjoxNzAzMTYwMDM0fQ.qBvSKcFGBuWY0ieub6sNFhAqQYd_CRQj5Wc2e-tD05Q"
}
Harap access token disimpan secara lokal untuk proses selanjutnya

Mengirim gambar
POST "URL/sendpicture"
untuk autorisasi
Headers JSON-> key = Authorization & value = Bearer [access tokennya]
contoh {"Authorization" : "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTcwMzE1NjQzNCwianRpIjoiMmJmM2NmNmYtZDhjZS00NWRlLWJmYzktODdmZDBmYjMwMmMxIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6InNpZ2l0IiwibmJmIjoxNzAzMTU2NDM0LCJjc3JmIjoiYWQ5MjhkYzAtMGMwZS00NmYwLTlmNDQtYTliNjFlOThmMDAzIiwiZXhwIjoxNzAzMTYwMDM0fQ.qBvSKcFGBuWY0ieub6sNFhAqQYd_CRQj5Wc2e-tD05Q"}
Body JSON yang akan dikirim
berupa file dengan key -> 'image' dan value -> 'filenya'
contoh responsnya
{
    "accuracy": 0.8302090167999268,
    "image_url": "https://storage.googleapis.com/garbo-foto/sigit/plastik.jpg",
    "prediction": "plastic"
}

mendapatkan hasil history
GET "URL/result"
untuk autorisasi
Headers JSON-> key = Authorization & value = Bearer [access tokennya]
nanti akan mendapatkan respons seperti berikut
[
    {
        "foto": "https://storage.googleapis.com/garbo-foto/sigit/botle.jpg",
        "jenis_sampah": "glass",
        "timestamp": "2023-12-21 10:38:51",
        "username": "sigit"
    },
    {
        "foto": "https://storage.googleapis.com/garbo-foto/sigit/cardboard10.jpg",
        "jenis_sampah": "cardboard",
        "timestamp": "2023-12-21 10:42:32",
        "username": "sigit"
    },
    {
        "foto": "https://storage.googleapis.com/garbo-foto/sigit/paper.jpeg",
        "jenis_sampah": "paper",
        "timestamp": "2023-12-21 10:42:42",
        "username": "sigit"
    },
    {
        "foto": "https://storage.googleapis.com/garbo-foto/sigit/paper.jpg",
        "jenis_sampah": "paper",
        "timestamp": "2023-12-21 10:43:19",
        "username": "sigit"
    },
    {
        "foto": "https://storage.googleapis.com/garbo-foto/sigit/plastik.jpg",
        "jenis_sampah": "plastic",
        "timestamp": "2023-12-21 10:43:47",
        "username": "sigit"
    },
    {
        "foto": "https://storage.googleapis.com/garbo-foto/sigit/plastik.jpg",
        "jenis_sampah": "plastic",
        "timestamp": "2023-12-21 17:46:53",
        "username": "sigit"
    },
    {
        "foto": "https://storage.googleapis.com/garbo-foto/sigit/plastik.jpg",
        "jenis_sampah": "plastic",
        "timestamp": "2023-12-21 11:01:09",
        "username": "sigit"
    }
]

mendapatkan hasil history berdasarkan jenis sampah
GET "URL/result/{jenis-sampah}"
jenis-sampahnya yaitu ['cardboard', 'glass', 'metal', 'paper', 'plastic']
untuk autorisasi
Headers JSON-> key = Authorization & value = Bearer [access tokennya]
nanti akan mendapatkan respons seperti berikut
[
    {
        "foto": "https://storage.googleapis.com/garbo-foto/sigit/cardboard10.jpg",
        "jenis_sampah": "cardboard",
        "timestamp": "2023-12-21 10:42:32",
        "username": "sigit"
    }
]

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:12345@localhost/Yemek'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Yemek(db.Model):
    __tablename__ = 'yemekler'

    id = db.Column(db.Integer, primary_key=True)
    isim = db.Column(db.String(255))
    fiyat = db.Column(db.Numeric(255))
    kategori = db.Column(db.Integer)
    resim = db.Column(db.String)
    info = db.Column(db.String(15))
    sepet_urunleri = db.relationship("Sepet", back_populates="yemek")

class Sepet(db.Model):
    __tablename__ = 'sepet'

    id = db.Column(db.Integer, primary_key=True)
    yemek_id = db.Column(db.Integer, db.ForeignKey('yemekler.id'))
    adet = db.Column(db.Integer)
    yemek = db.relationship("Yemek", back_populates="sepet_urunleri")


    
    
@app.route('/gorev',methods=['GET'])
def hepsi_getir():
    gorev = Yemek.query.all()
    
    return([{'id':g.id, 'isim':g.isim, 'fiyat':g.fiyat, 'kategori':g.kategori, 'resim':g.resim, 'info':g.info} for g in gorev])

@app.route('/gorev/<int:id>',methods=['GET'])
def getir(id):
    getir = Yemek.query.get(id)
    return ([{"id":getir.id, "isim":getir.isim, "fiyat":getir.fiyat, "kategori":getir.kategori, "resim":getir.resim, "info":getir.info}])

@app.route('/gorev',methods=['POST'])
def ekle():
    yemek = Yemek(isim ="Döner Pilav", fiyat = 85, kategori =1,resim = "1515", info ="Miss")
    db.session.add(yemek)
    db.session.commit()
    return ([{"id":yemek.id, "isim":yemek.isim, "fiyat":yemek.fiyat, "kategori":yemek.kategori, "resim":yemek.resim, "info":yemek.info}])

@app.route('/sepet_ekle', methods=['POST'])
def sepete_urun_ekle():
    if request.headers.get('Content-Type') != 'application/json': #veri formatının json olduğunu belirtiyoruz.
        return jsonify({"message": "Content-Type should be 'application/json'"}), 400

    data = request.json
    yemek_id = data.get('yemek_id')
    adet = data.get('adet')

    if yemek_id is None or adet is None:
        return jsonify({"message": "Missing 'yemek_id' or 'adet' in request"}), 400

    yemek = Yemek.query.get(yemek_id)
    if yemek is None:
        return jsonify({"message": "Ürün bulunamadı"}), 404

    # Eğer ürün zaten sepette ise sadece adedi artır
    existing_sepet_urunu = Sepet.query.filter_by(yemek_id=yemek_id).first() #burda yemek_id ye sahip bi ürün önceden eklenmiş mi ona bakıyoruz.
    if existing_sepet_urunu:
        existing_sepet_urunu.adet += adet
    else:
        sepet_urunu = Sepet(yemek_id=yemek_id, adet=adet)
        db.session.add(sepet_urunu)

    db.session.commit()

    return jsonify({"message": "Ürün sepete eklendi veya adet artırıldı"})

@app.route('/sepet', methods=['GET'])
def sepeti_goruntule():
    sepet_icerigi = db.session.query(Yemek, Sepet.adet).join(Sepet, Yemek.id == Sepet.yemek_id).all()

    sepet_json = [{"urun_ad": yemek.isim, "fiyat": yemek.fiyat, "adet": adet} for (yemek, adet) in sepet_icerigi]

    toplam_fiyat = sum(yemek.fiyat * adet for (yemek, adet) in sepet_icerigi)

    sepet_json.append({"toplam_fiyat": toplam_fiyat})

    return jsonify({"sepet": sepet_json})

    
    
if __name__ == '__main__':
    app.run(debug=True)
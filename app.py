from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

def bersihkan_angka(kolom):
    return (
        kolom.astype(str)
        .str.replace('Rp', '', regex=False)
        .str.replace('rb', '000', regex=False)
        .str.replace(' ', '', regex=False)
        .str.replace(',', '.', regex=False)
    )

@app.route("/", methods=["GET", "POST"])
def home():
    data = None

    if request.method == "POST":

        if 'file' not in request.files:
            return "Tidak ada file"

        file = request.files["file"]

        if file.filename == '':
            return "File kosong"

        df = pd.read_excel(file)

        # 🔹 Bersihkan kolom angka
        kolom_angka = ['SISTEM', 'FISIK', 'HPP']

        for col in kolom_angka:
            if col in df.columns:
                df[col] = bersihkan_angka(df[col])
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

        # 🔥 Hitung ulang
        df['SELISIH'] = df['FISIK'] - df['SISTEM']
        df['NILAI'] = df['SELISIH'] * df['HPP']

        # 🔥 AGREGASI (1 baris per barang)
        df = df.groupby(['KODE', 'NAMA'], as_index=False).agg({
            # 'SISTEM': 'sum',
            # 'FISIK': 'sum',
            'HPP': 'first',
            'SELISIH': 'sum',
            # 'NILAI': 'sum',
        })

        # 🔹 (optional) hanya tampil yang bermasalah
        df = df[df['SELISIH'] != 0]

        # 🔹 urutkan dari yang paling parah
        df = df.sort_values(by='SELISIH', key=abs, ascending=False)

        data = df.to_html(classes="table table-striped")

    return render_template("index.html", data=data)

if __name__ == "__main__":
    app.run()
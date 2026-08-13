from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from pathlib import Path
import sys
import json

def get_gps_info(image_path):
    # 画像を開く
    img = Image.open(image_path)

    # exif.get_ifd(0x8825) でGPS情報(IFD)を直接取得する
    exif = img.getexif()
    gps_ifd = exif.get_ifd(0x8825)

    if not gps_ifd:
        print("GPS情報が見つかりません。（またはEXIFがありません）")
        return

    # タグ名を人間が読める文字列に変換して辞書に格納
    gps_info = {}
    for key, val in gps_ifd.items():
        gps_info[GPSTAGS.get(key, key)] = val

    # 緯度・経度の度分秒（DMS）を抽出
    lat = gps_info.get("GPSLatitude")
    lat_ref = gps_info.get("GPSLatitudeRef")
    lon = gps_info.get("GPSLongitude")
    lon_ref = gps_info.get("GPSLongitudeRef")

    if lat and lon:
        # 度分秒から10進法（度）に変換する関数
        def convert_to_degrees(value):
            d = float(value[0])
            m = float(value[1])
            s = float(value[2])
            return d + (m / 60.0) + (s / 3600.0)

        latitude = convert_to_degrees(lat)
        if lat_ref != "N":
            latitude = -latitude

        longitude = convert_to_degrees(lon)
        if lon_ref != "E":
            longitude = -longitude

        output = f'{{ "lat": {latitude:.4f}, "lon": {longitude:.4f}, "file": "{image_path.name}" }}'
        print(output)
        #print(f"lat: {latitude}")
        #print(f"lon: {longitude}")
        # GoogleマップのURLを作成
        #print(f"Googleマップ: https://google.com{latitude},{longitude}")
        

def process_files(folder_path_str):
    folder_path = Path(folder_path_str)

    # フォルダの存在確認
    if not folder_path.is_dir():
        print(f"エラー: フォルダが見つかりません: {folder_path}")
        return

    # 特定の拡張子（例: .txt）のファイルを処理
    target_files = folder_path.glob("*.jpg")

    for file_path in target_files:
        #print(f"処理中: {file_path.name}")
        get_gps_info(file_path)


if __name__ == "__main__":
    # 引数が正しく渡されているかチェック (スクリプト名 + フォルダ名 で計2つ)
    if len(sys.argv) < 2:
        print("使用方法: python loc_info.py <フォルダのパス>")
        sys.exit(1)

    # 1番目の引数をフォルダパスとして取得
    input_folder = sys.argv[1]
    process_files(input_folder)



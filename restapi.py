from flask import Flask, jsonify, request
import csv
import os

app = Flask(__name__)

file_path = "stock_codes.txt"  # 수정된 파일 경로

def read_stock_codes_with_ta(file_path):
    """
    파일에서 종목 코드와 눌림목 타점을 읽어오는 함수
    """
    stock_data = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                stock_code = row.get('stock_code', '').strip()
                ta_point = row.get('ta_point', '').strip()
                if stock_code and ta_point:
                    stock_data.append({
                        "stock_code": stock_code,
                        "ta_point": ta_point
                    })
        return stock_data
    except FileNotFoundError:
        print(f"파일을 찾을 수 없습니다: {file_path}")
        return []
    except Exception as e:
        print(f"파일을 읽는 중 오류가 발생했습니다: {e}")
        return []

# 파일에서 종목 코드와 타점 읽기
stock_data = read_stock_codes_with_ta(file_path)

@app.route('/submit_stock_codes', methods=['GET'])
def get_stock_codes():
    """
    모든 종목 코드와 눌림목 타점을 JSON 형태로 반환하는 엔드포인트
    """
    return jsonify(stock_data), 200

@app.route('/submit_stock_codes/<ta_point>', methods=['GET'])
def get_stock_codes_by_ta(ta_point):
    """
    특정 눌림목 타점(3/5 또는 5/10)에 해당하는 종목 코드를 JSON 형태로 반환하는 엔드포인트
    """
    filtered_stocks = [stock for stock in stock_data if stock['ta_point'] == ta_point]
    if not filtered_stocks:
        return jsonify({"message": f"No stock codes found with ta_point '{ta_point}'."}), 404
    return jsonify(filtered_stocks), 200

@app.route('/add_stock_code', methods=['POST'])
def add_stock_code():
    """
    새로운 종목 코드와 타점을 추가하는 엔드포인트
    """
    data = request.get_json()
    stock_code = data.get('stock_code')
    ta_point = data.get('ta_point')
    
    if not stock_code or not ta_point:
        return jsonify({"error": "종목 코드와 타점을 모두 제공해야 합니다."}), 400
    
    # 중복 확인
    for stock in stock_data:
        if stock['stock_code'] == stock_code:
            return jsonify({"error": f"종목 코드 {stock_code}는 이미 존재합니다."}), 409
    
    # 데이터 추가
    new_stock = {
        "stock_code": stock_code.strip(),
        "ta_point": ta_point.strip()
    }
    stock_data.append(new_stock)
    
    # 파일에 추가
    try:
        file_exists = os.path.isfile(file_path)
        with open(file_path, 'a', encoding='utf-8', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=["stock_code", "ta_point"])
            if not file_exists:
                writer.writeheader()  # 헤더가 없는 경우 헤더 작성
            writer.writerow(new_stock)
    except Exception as e:
        return jsonify({"error": f"파일에 데이터를 추가하는 중 오류가 발생했습니다: {e}"}), 500
    
    return jsonify(new_stock), 201

@app.route('/delete_stock_code/<stock_code>', methods=['DELETE'])
def delete_stock_code(stock_code):
    """
    특정 종목 코드를 삭제하는 엔드포인트
    """
    global stock_data
    stock_to_delete = None
    for stock in stock_data:
        if stock['stock_code'] == stock_code:
            stock_to_delete = stock
            break
    
    if not stock_to_delete:
        return jsonify({"error": f"종목 코드 {stock_code}를 찾을 수 없습니다."}), 404
    
    stock_data.remove(stock_to_delete)
    
    # 파일에서 삭제
    try:
        with open(file_path, 'w', encoding='utf-8', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=["stock_code", "ta_point"])
            writer.writeheader()
            writer.writerows(stock_data)
    except Exception as e:
        return jsonify({"error": f"파일에서 데이터를 삭제하는 중 오류가 발생했습니다: {e}"}), 500
    
    return jsonify({"message": f"종목 코드 {stock_code}가 삭제되었습니다."}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)

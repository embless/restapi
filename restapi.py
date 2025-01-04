from flask import Flask, jsonify, request

app = Flask(__name__)

file_path = "stock_codes.txt"  # 파일 경로

def read_stock_codes_from_file(file_path):
    """
    파일에서 종목 코드를 읽어오는 함수
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            stock_codes = [line.strip() for line in file if line.strip()]
        return stock_codes
    except FileNotFoundError:
        print(f"파일을 찾을 수 없습니다: {file_path}")
        return []

# 파일에서 종목 코드 읽기
stock_codes = read_stock_codes_from_file(file_path)

@app.route('/submit_stock_codes', methods=['GET'])
def get_stock_codes():
    """
    종목 코드를 JSON 형태로 반환하는 엔드포인트
    """
    # 각 종목 코드를 {"stock_code": "XXXXXX"} 형태로 변환
    stock_codes_json = [{"stock_code": code} for code in stock_codes]
    return jsonify(stock_codes_json)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4999)
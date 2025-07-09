import sqlite3
from app.core.config import DATABASE_FILE
from app.core.security import encrypt_data

def init_database():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    # --- 테이블 재생성 ---
    cursor.execute("DROP TABLE IF EXISTS Gantt_Tasks;")
    cursor.execute("DROP TABLE IF EXISTS Contract_Engineers;")
    cursor.execute("DROP TABLE IF EXISTS Engineers;")
    cursor.execute("DROP TABLE IF EXISTS Contracts;")
    cursor.execute("DROP TABLE IF EXISTS Parties;")

    # 참여자 정보 (계약자, 계약상대자)
    cursor.execute("""
    CREATE TABLE Parties (
        id INTEGER PRIMARY KEY, party_type TEXT, company_name TEXT, 
        ceo_name TEXT, address TEXT, registration_no BLOB, phone_no BLOB
    );""")
    # 계약 정보
    cursor.execute("""
    CREATE TABLE Contracts (
        id INTEGER PRIMARY KEY, project_name TEXT, project_location TEXT, 
        contract_amount_text TEXT, contract_date TEXT, start_date TEXT, 
        completion_date TEXT, submission_date TEXT, client_id INTEGER, contractor_id INTEGER,
        FOREIGN KEY(client_id) REFERENCES Parties(id),
        FOREIGN KEY(contractor_id) REFERENCES Parties(id)
    );""")
    # 기술인 정보
    cursor.execute("""
    CREATE TABLE Engineers (
        id INTEGER PRIMARY KEY, name TEXT, position TEXT, grade TEXT, 
        resident_no BLOB, seal_image_filename TEXT
    );""")
    # 계약-기술인 연결 정보
    cursor.execute("""
    CREATE TABLE Contract_Engineers (
        contract_id INTEGER, engineer_id INTEGER, role TEXT,
        PRIMARY KEY(contract_id, engineer_id),
        FOREIGN KEY(contract_id) REFERENCES Contracts(id),
        FOREIGN KEY(engineer_id) REFERENCES Engineers(id)
    );""")
    # [수정] 간트차트 작업 정보 - id를 자동으로 증가시키도록 변경
    cursor.execute("""
    CREATE TABLE Gantt_Tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT, contract_id INTEGER, task_name TEXT, 
        start_month INTEGER, end_month INTEGER,
        FOREIGN KEY(contract_id) REFERENCES Contracts(id)
    );""")
    print("   - 모든 테이블 재생성 완료.")

    # --- 샘플 데이터 삽입 ---
    try:
        # 참여자
        cursor.execute("INSERT INTO Parties VALUES (?, ?, ?, ?, ?, ?, ?)", (1, 'contractor', '지니 건설 주식회사', '김지니', '제주특별자치도 제주시 첨단로 242', encrypt_data('123-45-67890'), encrypt_data('010-1234-5678')))
        cursor.execute("INSERT INTO Parties VALUES (?, ?, ?, ?, ?, ?, ?)", (2, 'client', '제주특별자치도청', '오영훈', '제주특별자치도 제주시 문연로 6', encrypt_data('888-99-00001'), encrypt_data('064-710-2114')))
        # 계약
        cursor.execute("INSERT INTO Contracts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (1, 'OO지구 하수관로 정비공사', '제주시 애월읍 일원', '금 이억오천만원정 (₩250,000,000)', '2024. 07. 10', '2024. 07. 15', '2025. 07. 14', '2024. 07. 12', 2, 1))
        # 기술인
        cursor.execute("INSERT INTO Engineers VALUES (?, ?, ?, ?, ?, ?)", (1, '박기술', '용역책임기술자', '특급기술인', encrypt_data('700101-1234567'), 'seal_park.png'))
        cursor.execute("INSERT INTO Engineers VALUES (?, ?, ?, ?, ?, ?)", (2, '이분야', '분야별 책임기술자 (토목)', '고급기술인', encrypt_data('800202-2345678'), 'seal_lee.png'))
        cursor.execute("INSERT INTO Engineers VALUES (?, ?, ?, ?, ?, ?)", (3, '최참여', '참여기술자', '중급기술인', encrypt_data('900303-1456789'), 'seal_choi.png'))
        # 계약-기술인 연결
        cursor.execute("INSERT INTO Contract_Engineers VALUES (?, ?, ?)", (1, 1, '용역책임기술자'))
        cursor.execute("INSERT INTO Contract_Engineers VALUES (?, ?, ?)", (1, 2, '분야별 책임기술자 (토목)'))
        cursor.execute("INSERT INTO Contract_Engineers VALUES (?, ?, ?)", (1, 3, '참여기술자'))
        # [수정] 간트차트 - id 값을 직접 넣지 않고 DB가 자동으로 생성하게 함
        cursor.execute("INSERT INTO Gantt_Tasks (contract_id, task_name, start_month, end_month) VALUES (?, ?, ?, ?)", (1, '자료수집 및 현장조사', 7, 8))
        cursor.execute("INSERT INTO Gantt_Tasks (contract_id, task_name, start_month, end_month) VALUES (?, ?, ?, ?)", (1, '측량 및 기본설계', 9, 11))
        cursor.execute("INSERT INTO Gantt_Tasks (contract_id, task_name, start_month, end_month) VALUES (?, ?, ?, ?)", (1, '실시설계 및 도면작성', 12, 4))
        cursor.execute("INSERT INTO Gantt_Tasks (contract_id, task_name, start_month, end_month) VALUES (?, ?, ?, ?)", (1, '보고서 작성 및 제출', 5, 6))

        conn.commit()
        print("   - 샘플 데이터 삽입 완료.")
    except sqlite3.IntegrityError as e:
        print(f"   - 샘플 데이터 삽입 중 오류 발생 (이미 존재할 수 있음): {e}")

    conn.close()

def get_full_contract_details(contract_id: int) -> dict:
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    base_query = """
    SELECT c.*, p1.company_name as contractor_name, p1.ceo_name as contractor_ceo, p1.address as contractor_address, 
           p2.company_name as client_name, p2.ceo_name as client_ceo_name
    FROM Contracts c
    JOIN Parties p1 ON c.contractor_id = p1.id
    JOIN Parties p2 ON c.client_id = p2.id
    WHERE c.id = ?
    """
    result = cursor.execute(base_query, (contract_id,)).fetchone()
    if not result:
        conn.close()
        return None
    contract_data = dict(result)

    engineer_query = """
    SELECT e.*, ce.role
    FROM Engineers e
    JOIN Contract_Engineers ce ON e.id = ce.engineer_id
    WHERE ce.contract_id = ?
    """
    engineers = [dict(row) for row in cursor.execute(engineer_query, (contract_id,)).fetchall()]
    
    gantt_query = "SELECT * FROM Gantt_Tasks WHERE contract_id = ?"
    gantt_tasks = [dict(row) for row in cursor.execute(gantt_query, (contract_id,)).fetchall()]
    
    conn.close()

    from app.core.security import decrypt_data
    for eng in engineers:
        eng['resident_no'] = decrypt_data(eng['resident_no'])
    
    contract_data['engineers'] = engineers
    contract_data['gantt_tasks'] = gantt_tasks
    
    return contract_data

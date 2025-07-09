import sqlite3
from app.core.config import DATABASE_FILE
from app.core.security import encrypt_data
from num2words import num2words

def format_currency_hangeul(num_amount):
    return num2words(num_amount, lang='ko')

def init_database():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    # 테이블 초기화
    cursor.execute("DROP TABLE IF EXISTS Gantt_Tasks;")
    cursor.execute("DROP TABLE IF EXISTS Contract_Engineers;")
    cursor.execute("DROP TABLE IF EXISTS Contract_Parties;")
    cursor.execute("DROP TABLE IF EXISTS Engineers;")
    cursor.execute("DROP TABLE IF EXISTS Contracts;")
    cursor.execute("DROP TABLE IF EXISTS Parties;")
    # 테이블 생성
    cursor.execute("""CREATE TABLE Parties (id INTEGER PRIMARY KEY, company_name TEXT, ceo_name TEXT, address TEXT, registration_no BLOB);""")
    cursor.execute("""CREATE TABLE Contracts (id INTEGER PRIMARY KEY, project_name TEXT, contract_amount INTEGER, 
                                             contract_date TEXT, start_date TEXT, completion_date TEXT, 
                                             submission_date TEXT, contract_official_name TEXT);""")
    cursor.execute("""CREATE TABLE Contract_Parties (contract_id INTEGER, party_id INTEGER, role TEXT, PRIMARY KEY(contract_id, party_id));""")
    cursor.execute("""CREATE TABLE Engineers (id INTEGER PRIMARY KEY, name TEXT, resident_no BLOB, seal_image_filename TEXT);""")
    cursor.execute("""CREATE TABLE Contract_Engineers (contract_id INTEGER, engineer_id INTEGER, role TEXT, 
                                                      position TEXT, grade TEXT, field TEXT, PRIMARY KEY(contract_id, engineer_id));""")
    cursor.execute("""CREATE TABLE Gantt_Tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, contract_id INTEGER, 
                                               task_name TEXT, start_month INTEGER, end_month INTEGER, total_months INTEGER);""")
    try:
        cursor.execute("INSERT INTO Parties VALUES (?, ?, ?, ?, ?)", (1, '지니 건설(주)', '김지니', '제주특별자치도 제주시 첨단로 242', encrypt_data('123-45-67890')))
        cursor.execute("INSERT INTO Parties VALUES (?, ?, ?, ?, ?)", (2, '파트너 건축사사무소', '이파트', '제주특별자치도 제주시 연동 567', encrypt_data('111-22-33333')))
        cursor.execute("INSERT INTO Parties VALUES (?, ?, ?, ?, ?)", (3, '제주특별자치도', '오영훈', '제주특별자치도 제주시 문연로 6', encrypt_data('N/A')))
        cursor.execute("INSERT INTO Contracts VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                       (1, 'OO지구 하수관로 정비공사', 250000000, '2024. 07. 10.', '2024. 07. 15.', 
                        '2025. 07. 14.', '2024. 07. 12.', '(분임)재무관'))
        cursor.execute("INSERT INTO Contract_Parties VALUES (?, ?, ?)", (1, 1, 'contractor'))
        cursor.execute("INSERT INTO Contract_Parties VALUES (?, ?, ?)", (1, 2, 'contractor'))
        cursor.execute("INSERT INTO Contract_Parties VALUES (?, ?, ?)", (1, 3, 'client'))
        cursor.execute("INSERT INTO Engineers VALUES (?, ?, ?, ?)", (1, '박기술', encrypt_data('700101-1******'), 'seal_park.png'))
        cursor.execute("INSERT INTO Engineers VALUES (?, ?, ?, ?)", (2, '이분야', encrypt_data('800202-2******'), 'seal_lee.png'))
        cursor.execute("INSERT INTO Engineers VALUES (?, ?, ?, ?)", (3, '최참여', encrypt_data('900303-1******'), 'seal_choi.png'))
        cursor.execute("INSERT INTO Contract_Engineers VALUES (?, ?, ?, ?, ?, ?)", (1, 1, '총괄', '책임기술자', '특급', '토목'))
        cursor.execute("INSERT INTO Contract_Engineers VALUES (?, ?, ?, ?, ?, ?)", (1, 2, '분야', '참여기술자', '고급', '측량'))
        cursor.execute("INSERT INTO Contract_Engineers VALUES (?, ?, ?, ?, ?, ?)", (1, 3, '분야', '참여기술자', '중급', '안전'))
        # 간트차트 데이터
        cursor.execute("INSERT INTO Gantt_Tasks (contract_id, task_name, start_month, end_month, total_months) VALUES (?, ?, ?, ?, ?)", (1, '자료수집 및 현장조사', 7, 8, 12))
        cursor.execute("INSERT INTO Gantt_Tasks (contract_id, task_name, start_month, end_month, total_months) VALUES (?, ?, ?, ?, ?)", (1, '측량 및 기본설계', 9, 11, 12))
        cursor.execute("INSERT INTO Gantt_Tasks (contract_id, task_name, start_month, end_month, total_months) VALUES (?, ?, ?, ?, ?)", (1, '실시설계 및 도면작성', 12, 4, 12))
        cursor.execute("INSERT INTO Gantt_Tasks (contract_id, task_name, start_month, end_month, total_months) VALUES (?, ?, ?, ?, ?)", (1, '보고서 작성 및 제출', 5, 6, 12))

        conn.commit()
    except sqlite3.IntegrityError: pass
    conn.close()

def get_full_contract_details(contract_id: int) -> dict:
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    result = cursor.execute("SELECT * FROM Contracts WHERE id = ?", (contract_id,)).fetchone()
    if not result: conn.close(); return None
    
    contract_data = dict(result)
    contract_data['contract_amount_hangeul'] = format_currency_hangeul(contract_data['contract_amount'])

    parties_query = "SELECT p.*, cp.role FROM Parties p JOIN Contract_Parties cp ON p.id = cp.party_id WHERE cp.contract_id = ?"
    all_parties = [dict(row) for row in cursor.execute(parties_query, (contract_id,)).fetchall()]
    contract_data['contractors'] = [p for p in all_parties if p['role'] == 'contractor']
    contract_data['clients'] = [p for p in all_parties if p['role'] == 'client']
    
    engineer_query = "SELECT * FROM Engineers e JOIN Contract_Engineers ce ON e.id = ce.engineer_id WHERE ce.contract_id = ?"
    engineers = [dict(row) for row in cursor.execute(engineer_query, (contract_id,)).fetchall()]
    
    # [보완] 공정표 데이터 조회 로직 추가
    gantt_query = "SELECT * FROM Gantt_Tasks WHERE contract_id = ?"
    gantt_tasks = [dict(row) for row in cursor.execute(gantt_query, (contract_id,)).fetchall()]
    
    conn.close()
    
    from app.core.security import decrypt_data
    for eng in engineers: eng['resident_no'] = decrypt_data(eng['resident_no'])
    
    contract_data['engineers'] = engineers
    contract_data['gantt_tasks'] = gantt_tasks # 데이터에 포함
    contract_data['lead_engineer'] = next((eng for eng in engineers if eng['position'] == '책임기술자'), None)
    return contract_data

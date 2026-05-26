# -*- coding: utf-8 -*-
"""
Google Sheets DB 연동 모듈
- Streamlit secrets에 gcp_service_account 및 google_sheets 설정이 있으면 Google Sheets 사용
- 설정이 없으면 기존 JSON 파일 방식으로 자동 폴백
"""
import json
import os
from typing import Dict, Any, List

import streamlit as st

# ─── Google Sheets 사용 가능 여부 플래그 ───
_USE_GSHEET = False
try:
    import gspread
    from google.oauth2.service_account import Credentials
    _USE_GSHEET = True
except ImportError:
    _USE_GSHEET = False

# ─── 로컬 JSON 파일 경로 (폴백용) ───
_FRIENDS_JSON = 'friends_db.json'
_USERS_JSON = 'users_db.json'

# ─── 시트 이름 ↔ JSON 파일 매핑 ───
_SHEET_JSON_MAP = {
    'friends': _FRIENDS_JSON,
    'users': _USERS_JSON,
}

# ─── 시트별 헤더 정의 ───
_HEADERS = {
    'friends': ['이름', '성별', 'birth_date', 'birth_time', 'calendar', 'has_time', 'phone', 'pref', 'user_memo', 'maker_memo', 'memo'],
    'users': ['이름', '성별', 'birth_date', 'birth_time', 'calendar', 'has_time', 'phone', 'pref', 'user_memo', 'maker_memo'],
}

# ─── bool 필드 목록 (시트에서 읽을 때 문자열→bool 변환 필요) ───
_BOOL_FIELDS = {'has_time'}


def _has_gsheet_config() -> bool:
    """Streamlit secrets에 Google Sheets 설정이 있는지 확인"""
    try:
        return (
            _USE_GSHEET
            and 'gcp_service_account' in st.secrets
            and 'google_sheets' in st.secrets
        )
    except Exception:
        return False


@st.cache_resource
def _get_gsheet_client():
    """
    gspread 클라이언트를 생성하고 캐싱합니다.
    앱 세션 전체에서 한 번만 인증합니다.
    """
    creds = Credentials.from_service_account_info(
        dict(st.secrets['gcp_service_account']),
        scopes=[
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive',
        ],
    )
    return gspread.authorize(creds)


def _get_worksheet(sheet_name: str):
    """스프레드시트에서 특정 워크시트를 반환"""
    client = _get_gsheet_client()
    spreadsheet_url = st.secrets['google_sheets']['spreadsheet_url']
    spreadsheet = client.open_by_url(spreadsheet_url)
    return spreadsheet.worksheet(sheet_name)


# ═══════════════════════════════════════════
#  핵심 API: load / save
# ═══════════════════════════════════════════

def load_sheet_as_list(sheet_name: str) -> List[Dict[str, Any]]:
    """
    지정 시트(또는 JSON 파일)에서 전체 데이터를 List[Dict]로 반환합니다.
    
    - Google Sheets 설정이 있으면 시트에서 읽기
    - 없으면 로컬 JSON 파일에서 읽기 (폴백)
    """
    if _has_gsheet_config():
        return _load_from_gsheet(sheet_name)
    else:
        return _load_from_json(sheet_name)


def save_list_to_sheet(sheet_name: str, data: List[Dict[str, Any]]):
    """
    List[Dict] 데이터를 시트(또는 JSON 파일)에 저장합니다.
    
    - Google Sheets 설정이 있으면 시트에 덮어쓰기
    - 없으면 로컬 JSON 파일에 쓰기 (폴백)
    """
    if _has_gsheet_config():
        _save_to_gsheet(sheet_name, data)
    else:
        _save_to_json(sheet_name, data)


# ═══════════════════════════════════════════
#  Google Sheets 구현
# ═══════════════════════════════════════════

def _load_from_gsheet(sheet_name: str) -> List[Dict[str, Any]]:
    """Google Sheets에서 데이터 읽기"""
    try:
        ws = _get_worksheet(sheet_name)
        records = ws.get_all_records()
        # bool 필드 변환 및 빈 문자열 정리
        cleaned = []
        for row in records:
            clean_row = {}
            for k, v in row.items():
                if k in _BOOL_FIELDS:
                    clean_row[k] = _to_bool(v)
                elif v == '':
                    clean_row[k] = None
                else:
                    clean_row[k] = v
            cleaned.append(clean_row)
        return cleaned
    except Exception as e:
        st.error(f"⚠️ Google Sheets 읽기 오류 ({sheet_name}): {e}")
        # 폴백: 로컬 JSON에서 읽기 시도
        return _load_from_json(sheet_name)


def _save_to_gsheet(sheet_name: str, data: List[Dict[str, Any]]):
    """Google Sheets에 데이터 덮어쓰기 (헤더 유지)"""
    try:
        ws = _get_worksheet(sheet_name)
        headers = _HEADERS.get(sheet_name, [])
        
        if not headers and data:
            headers = list(data[0].keys())
        
        # 기존 데이터 영역 삭제 (헤더 제외)
        ws.clear()
        
        # 헤더 쓰기
        ws.update('A1', [headers])
        
        # 데이터 행 쓰기
        if data:
            rows = []
            for record in data:
                row = []
                for h in headers:
                    val = record.get(h, '')
                    if val is None:
                        val = ''
                    elif isinstance(val, bool):
                        val = str(val)  # True/False → 문자열
                    row.append(val)
                rows.append(row)
            
            if rows:
                ws.update(f'A2', rows)
        
    except Exception as e:
        st.error(f"⚠️ Google Sheets 저장 오류 ({sheet_name}): {e}")
        # 폴백: 로컬 JSON에도 저장
        _save_to_json(sheet_name, data)


# ═══════════════════════════════════════════
#  JSON 폴백 구현
# ═══════════════════════════════════════════

def _load_from_json(sheet_name: str) -> List[Dict[str, Any]]:
    """로컬 JSON 파일에서 데이터 읽기 (폴백)"""
    json_path = _SHEET_JSON_MAP.get(sheet_name, f'{sheet_name}.json')
    if not os.path.exists(json_path):
        return []
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"JSON 파일 읽기 오류 ({json_path}): {e}")
        return []


def _save_to_json(sheet_name: str, data: List[Dict[str, Any]]):
    """로컬 JSON 파일에 데이터 쓰기 (폴백)"""
    json_path = _SHEET_JSON_MAP.get(sheet_name, f'{sheet_name}.json')
    try:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"JSON 파일 저장 오류 ({json_path}): {e}")


# ═══════════════════════════════════════════
#  유틸리티
# ═══════════════════════════════════════════

def _to_bool(val) -> bool:
    """다양한 형태의 값을 bool로 변환"""
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        return val.strip().lower() in ('true', '1', 'yes', 'o')
    return bool(val)


def is_using_gsheet() -> bool:
    """현재 Google Sheets를 사용 중인지 반환 (UI 표시용)"""
    return _has_gsheet_config()

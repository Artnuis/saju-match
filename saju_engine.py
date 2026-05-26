# -*- coding: utf-8 -*-
"""
Saju Computation and Compatibility Engine
Calculates Saju Pillars using sajupy, extracts Five Elements (오행),
and evaluates compatibility based on traditional Saju principles.
"""

from typing import Dict, Any, Optional, List
from sajupy import SajuCalculator

# 10 Heavenly Stems (천간) Info
STEMS_INFO = {
    '甲': {'kr': '갑', 'element': '목', 'yinyang': '+', 'desc': '당당하고 뻗어나가는 나무의 기운'},
    '乙': {'kr': '을', 'element': '목', 'yinyang': '-', 'desc': '유연하고 생명력 있는 화초의 기운'},
    '丙': {'kr': '병', 'element': '화', 'yinyang': '+', 'desc': '세상을 밝게 비추는 태양의 기운'},
    '丁': {'kr': '정', 'element': '화', 'yinyang': '-', 'desc': '따뜻하고 부드러운 모닥불/촛불의 기운'},
    '戊': {'kr': '무', 'element': '토', 'yinyang': '+', 'desc': '넓고 든든한 태산의 기운'},
    '己': {'kr': '기', 'element': '토', 'yinyang': '-', 'desc': '비옥하고 자애로운 대지의 기운'},
    '庚': {'kr': '경', 'element': '금', 'yinyang': '+', 'desc': '강인하고 결단력 있는 바위/원석의 기운'},
    '辛': {'kr': '신', 'element': '금', 'yinyang': '-', 'desc': '섬세하고 아름다운 보석/칼의 기운'},
    '壬': {'kr': '임', 'element': '수', 'yinyang': '+', 'desc': '넓고 깊은 바다/강물의 기운'},
    '癸': {'kr': '계', 'element': '수', 'yinyang': '-', 'desc': '만물을 적셔주는 부드러운 빗물의 기운'},
}

# 5 Luck texts based on 10 Heavenly Stems (일간별 5가지 운세 해설)
STEM_LUCKS = {
    '甲': {'성향': '타고난 리더십과 곧은 심지로 주위 사람들을 이끄는 기둥 같은 역할입니다.', '연애운': '마음에 드는 사람에게는 앞뒤 재지 않고 직진하는 순정파입니다.', '재물운': '한 우물을 파서 큰 부를 이루는 대기만성형 재물운을 지녔습니다.', '직업운': '기획, 교육, 리더, 건축, 사업가 등에 탁월한 재능이 있습니다.', '건강운': '스트레스 관리와 뼈, 관절 계통의 피로를 주의하세요.'},
    '乙': {'성향': '부드러워 보이지만 끈질긴 생명력과 유연함으로 환경 적응력이 뛰어납니다.', '연애운': '다정다감하고 세심하게 상대를 챙기며 밀당에도 능숙합니다.', '재물운': '탁월한 인맥과 사교성으로 주변의 도움을 받아 돈이 모입니다.', '직업운': '예술, 디자인, 패션, 언론, 서비스업에 어울립니다.', '건강운': '호흡기와 알레르기, 신경성 스트레스에 취약할 수 있습니다.'},
    '丙': {'성향': '세상을 밝게 비추는 태양처럼 매사에 열정적이고 뒤끝이 없는 솔직함이 매력입니다.', '연애운': '금방 사랑에 빠지며 애정 표현이 적극적이고 화끈합니다.', '재물운': '크게 벌고 크게 쓰는 스케일로, 운의 흐름을 잘 타면 대박이 납니다.', '직업운': '방송, IT, 영업, 연예, 화려한 조명을 받는 직업이 좋습니다.', '건강운': '혈압, 심장, 안과 질환 등 불과 관련된 열성 질환을 주의하세요.'},
    '丁': {'성향': '겉으론 조용해도 내면의 열정과 속정이 깊어 따뜻한 위로를 주는 사람입니다.', '연애운': '은은하게 오래가는 사랑을 추구하는 로맨티스트입니다.', '재물운': '꼼꼼한 금전 감각으로 저축과 알뜰함으로 부를 튼튼하게 축적합니다.', '직업운': '연구, 종교, 복지, 상담, 정밀한 기술이 필요한 분야에 제격입니다.', '건강운': '예민함으로 인한 불면증이나 눈의 피로를 잘 풀어주세요.'},
    '戊': {'성향': '변함없는 큰 산처럼 묵직하고 믿음직스러워 사람들의 의지가 되어줍니다.', '연애운': '이해심과 포용력이 넓어 상대방에게 든든한 안식처가 됩니다.', '재물운': '부동산이나 땅과 관련된 투자, 묵직하고 장기적인 투자에 길합니다.', '직업운': '건축, 토목, 행정, 중간관리자, 신용을 바탕으로 한 사업에 좋습니다.', '건강운': '소화불량이나 위장, 대장 등 소화기 계통의 건강을 신경 쓰세요.'},
    '己': {'성향': '자애로운 대지처럼 품어주는 성향이 강하며 꼼꼼하고 실속을 잘 챙깁니다.', '연애운': '소소한 이벤트와 배려로 아기자기하고 예쁜 만남을 좋아합니다.', '재물운': '안정적으로 자산을 불려 나가는 알부자 스타일의 금전운입니다.', '직업운': '교육, 농업, 비서, 회계, 사람을 기르고 돕는 직업에 탁월합니다.', '건강운': '비장, 맹장, 피부 질환 등에 예민할 수 있으니 주의하세요.'},
    '庚': {'성향': '원리원칙을 중시하고 불의를 참지 못하는 강단 있는 의리파입니다.', '연애운': '책임감이 대단히 강해 한 번 맺은 인연을 끝까지 지키려 합니다.', '재물운': '큰돈을 만지는 배포가 있으며 승부사 기질로 큰 수익을 거둡니다.', '직업운': '군인, 경찰, 금융, 기계, 금속을 다루는 강인한 직업에 어울립니다.', '건강운': '호흡기, 치아, 대장 관련 질환이나 외상(다침)을 조심하세요.'},
    '辛': {'성향': '섬세하고 예리한 완벽주의자이며 자신만의 확고한 미적 기준이 있습니다.', '연애운': '눈높이가 다소 높으나 내 사람이라고 생각되면 한없이 헌신합니다.', '재물운': '가치 있는 것을 알아보는 안목이 뛰어나 예리한 재테크로 돈을 불립니다.', '직업운': '의료, 미용, 귀금속, 정밀기술, 칼이나 가위를 다루는 직업이 좋습니다.', '건강운': '피부 트러블, 호흡기, 그리고 신경성 스트레스에 특히 주의하세요.'},
    '壬': {'성향': '깊은 바다처럼 지혜롭고 포용력이 넓으나 속마음을 쉽게 드러내지 않습니다.', '연애운': '틀에 얽매이지 않고 유연하고 자유로우며 로맨틱한 연애를 즐깁니다.', '재물운': '고인 돈보다 흐르는 돈을 다루며, 무역이나 유통을 통한 재물운이 좋습니다.', '직업운': '유통, 무역, 철학, 심리, 교육 등 스케일이 크거나 깊이 있는 직업이 길합니다.', '건강운': '신장, 방광염, 혈액순환 등 수(水) 기운과 관련된 곳을 유의하세요.'},
    '癸': {'성향': '조용하고 여려 보이지만 대단히 영리하고 상황 판단이 빠릅니다.', '연애운': '모성애나 부성애처럼 상대를 보듬어주는 깊고 헌신적인 사랑을 합니다.', '재물운': '티끌 모아 태산, 지식이나 아이디어 등 보이지 않는 자산을 활용해 부를 일굽니다.', '직업운': '기획, 연구, 정보, 예술, 아이디어를 바탕으로 한 창작업이 맞습니다.', '건강운': '신장, 수족냉증, 그리고 생각이 많아 생기는 정신적 피로를 조심하세요.'}
}

# 12 Earthly Branches (지지) Info
BRANCHES_INFO = {
    '子': {'kr': '자', 'element': '수', 'yinyang': '-', 'temp': 'cold', 'animal': '쥐'},
    '丑': {'kr': '축', 'element': '토', 'yinyang': '-', 'temp': 'cold', 'animal': '소'},
    '寅': {'kr': '인', 'element': '목', 'yinyang': '+', 'temp': 'warm', 'animal': '호랑이'},
    '卯': {'kr': '묘', 'element': '목', 'yinyang': '-', 'temp': 'warm', 'animal': '토끼'},
    '辰': {'kr': '진', 'element': '토', 'yinyang': '+', 'temp': 'wet', 'animal': '용'},
    '巳': {'kr': '사', 'element': '화', 'yinyang': '+', 'temp': 'hot', 'animal': '뱀'},
    '午': {'kr': '오', 'element': '화', 'yinyang': '-', 'temp': 'hot', 'animal': '말'},
    '未': {'kr': '미', 'element': '토', 'yinyang': '-', 'temp': 'hot', 'animal': '양'},
    '申': {'kr': '신', 'element': '금', 'yinyang': '+', 'temp': 'cool', 'animal': '원숭이'},
    '酉': {'kr': '유', 'element': '금', 'yinyang': '-', 'temp': 'cool', 'animal': '닭'},
    '戌': {'kr': '술', 'element': '토', 'yinyang': '+', 'temp': 'hot', 'animal': '개'},
    '亥': {'kr': '해', 'element': '수', 'yinyang': '+', 'temp': 'cold', 'animal': '돼지'},
}

# Element colors for UI display (mystic/premium Saju colors)
ELEMENT_COLORS = {
    '목': {'bg': '#E8F5E9', 'text': '#2E7D32', 'desc': '목(木) - 청색/초록 (성장, 생명력, 기획)'},
    '화': {'bg': '#FFEBEE', 'text': '#C62828', 'desc': '화(火) - 적색/빨강 (열정, 표현력, 활기)'},
    '토': {'bg': '#FFFDE7', 'text': '#F57F17', 'desc': '토(土) - 황색/노랑 (신뢰, 중재, 포용력)'},
    '금': {'bg': '#FAFAFA', 'text': '#424242', 'desc': '금(金) - 백색/흰색 (결단, 냉철, 의리)'},
    '수': {'bg': '#E1F5FE', 'text': '#0277BD', 'desc': '수(水) - 흑색/푸른빛 (지혜, 유연성, 직관)'}
}

# Stem Harmony (천간합) pairs
STEM_HARMONY = {
    ('甲', '己'): '갑기합(甲己合) - 토(土)로 변화하는 부부의 지조 있는 결합',
    ('乙', '庚'): '을경합(乙庚合) - 금(金)으로 변화하는 도덕과 의리의 결합',
    ('丙', '辛'): '병신합(丙辛合) - 수(水)로 변화하는 애정과 권위의 결합',
    ('丁', '壬'): '정임합(丁壬合) - 목(木)으로 변화하는 다정다감하고 예술적인 결합',
    ('戊', '癸'): '무계합(戊癸合) - 화(火)로 변화하는 화려하고 지혜로운 결합',
}

# Stem Clashes (천간충) pairs
STEM_CLASH = {
    ('甲', '庚'), ('乙', '辛'), ('丙', '壬'), ('丁', '癸')
}

# Branch Six Combinations (지지육합)
BRANCH_SIX_HARMONY = {
    ('子', '丑'): '자축합(子丑合) - 현실적 협력과 굳건한 약속',
    ('寅', '亥'): '인해합(寅亥合) - 생명력을 키워가는 따뜻한 결합',
    ('卯', '戌'): '묘술합(卯戌合) - 봄과 가을의 서정적인 조화',
    ('辰', '酉'): '진유합(辰酉合) - 실리와 완벽을 추구하는 궁합',
    ('巳', '申'): '사신합(巳申合) - 열정과 냉정이 공존하는 역동적 합',
    ('午', '未'): '오미합(午未合) - 태양과 대지의 뜨거운 일치',
}

# Branch Three Combinations (지지삼합) groups
BRANCH_THREE_HARMONY = [
    ({'申', '子', '辰'}, '신자진 삼합(수 기운) - 흘러가는 물처럼 깊은 지혜와 포용력 공유'),
    ({'亥', '卯', '未'}, '해묘미 삼합(목 기운) - 푸른 나무처럼 함께 성장하고 발전하는 관계'),
    ({'寅', '午', '戌'}, '인오술 삼합(화 기운) - 뜨거운 불꽃처럼 세상을 밝히는 열정적 동반자'),
    ({'巳', '酉', '丑'}, '사유축 삼합(금 기운) - 단단한 금속처럼 변치 않는 강한 의리와 약속'),
]

# Branch Wonjin (원진살 - minor clash/tension)
BRANCH_WONJIN = {
    ('子', '未'), ('丑', '午'), ('寅', '酉'), ('卯', '申'), ('辰', '亥'), ('巳', '戌')
}

# Branch Clashes (지지충)
BRANCH_CLASH = {
    ('子', '午'), ('丑', '未'), ('寅', '申'), ('卯', '酉'), ('辰', '戌'), ('巳', '亥')
}

# Five Elements Generation (상생)
GENERATION = {
    '목': '화', # 목생화
    '화': '토', # 화생토
    '토': '금', # 토생금
    '금': '수', # 금생수
    '수': '목', # 수생목
}

# Five Elements Overcoming (상극)
OVERCOMING = {
    '목': '토', # 목극토
    '토': '수', # 토극수
    '수': '화', # 수극화
    '화': '금', # 화극금
    '금': '목', # 금극목
}

def analyze_saju(year: int, month: int, day: int, hour: Optional[int] = None, minute: int = 0) -> Dict[str, Any]:
    """
    Calculates Saju pillars using sajupy and analyzes element balances.
    If hour is None, uses 12:00 as a placeholder but sets has_hour=False to ignore hour pillar.
    """
    calculator = SajuCalculator()
    has_hour = hour is not None
    calc_hour = hour if has_hour else 12
    
    # Calculate saju
    saju_res = calculator.calculate_saju(
        year=year,
        month=month,
        day=day,
        hour=calc_hour,
        minute=minute,
        use_solar_time=False
    )
    
    # Process Pillars
    pillars = {}
    
    # Helper to parse stem & branch info
    def parse_part(stem_hanja: str, branch_hanja: str):
        stem_info = STEMS_INFO.get(stem_hanja, {'kr': '?', 'element': '?', 'yinyang': '?'})
        branch_info = BRANCHES_INFO.get(branch_hanja, {'kr': '?', 'element': '?', 'yinyang': '?', 'temp': 'balanced', 'animal': '?'})
        return {
            'stem_hanja': stem_hanja,
            'stem_kr': stem_info['kr'],
            'stem_element': stem_info['element'],
            'stem_yinyang': stem_info['yinyang'],
            'stem_desc': stem_info.get('desc', ''),
            'branch_hanja': branch_hanja,
            'branch_kr': branch_info['kr'],
            'branch_element': branch_info['element'],
            'branch_yinyang': branch_info['yinyang'],
            'branch_temp': branch_info.get('temp', 'balanced'),
            'branch_animal': branch_info.get('animal', ''),
            'pillar_hanja': stem_hanja + branch_hanja,
            'pillar_kr': stem_info['kr'] + branch_info['kr']
        }
        
    pillars['year'] = parse_part(saju_res['year_stem'], saju_res['year_branch'])
    pillars['month'] = parse_part(saju_res['month_stem'], saju_res['month_branch'])
    pillars['day'] = parse_part(saju_res['day_stem'], saju_res['day_branch'])
    
    if has_hour:
        pillars['hour'] = parse_part(saju_res['hour_stem'], saju_res['hour_branch'])
    else:
        pillars['hour'] = None

    # Count Five Elements (오행 개수 계산)
    element_counts = {'목': 0, '화': 0, '토': 0, '금': 0, '수': 0}
    total_chars = 0
    
    # We examine Year, Month, Day, and optionally Hour
    active_pillars = ['year', 'month', 'day']
    if has_hour:
        active_pillars.append('hour')
        
    for p_name in active_pillars:
        p = pillars[p_name]
        # Stem element
        se = p['stem_element']
        if se in element_counts:
            element_counts[se] += 1
            total_chars += 1
        # Branch element
        be = p['branch_element']
        if be in element_counts:
            element_counts[be] += 1
            total_chars += 1
            
    # Calculate percentages
    element_pct = {k: round((v / total_chars) * 100, 1) for k, v in element_counts.items()}
    
    # Calculate Power Scores (가중치 기반 오행 세기)
    element_power_scores = {'목': 0.0, '화': 0.0, '토': 0.0, '금': 0.0, '수': 0.0}
    power_weights = {
        'month_branch': 35.0,
        'day_branch': 15.0,
        'hour_branch': 15.0,
        'year_branch': 10.0,
        'day_stem': 10.0,
        'month_stem': 5.0,
        'year_stem': 5.0,
        'hour_stem': 5.0
    }
    
    for p_name in active_pillars:
        p = pillars[p_name]
        se = p['stem_element']
        be = p['branch_element']
        
        element_power_scores[se] += power_weights.get(f"{p_name}_stem", 0.0)
        element_power_scores[be] += power_weights.get(f"{p_name}_branch", 0.0)
        
    # Apply Sangsaeng (상생) Boost: A generates B, so B gets +40% of A's power.
    sangsaeng_map = {
        '목': '화',
        '화': '토',
        '토': '금',
        '금': '수',
        '수': '목'
    }
    
    boosted_power_scores = element_power_scores.copy()
    
    # 1. 기본 상생 부스트 (받는 쪽이 주는 쪽의 30%를 흡수)
    for giver, receiver in sangsaeng_map.items():
        boosted_power_scores[receiver] += element_power_scores[giver] * 0.3
        
    # 2. '월지(Month Branch)' 특별 부스트 (가장 강력한 계절의 힘)
    month_branch_el = pillars['month']['branch_element']
    receiver_of_month = sangsaeng_map[month_branch_el]
    boosted_power_scores[receiver_of_month] += 25.0  # 계절의 생조를 받아 폭발적 증가
    
    # 3. '일간(Day Stem, 나)' 특별 부스트 (내가 월지의 생을 받거나 같은 기운일 때 극강해짐)
    day_stem_el = pillars['day']['stem_element']
    if receiver_of_month == day_stem_el or month_branch_el == day_stem_el:
        boosted_power_scores[day_stem_el] += 20.0
        
    total_power = sum(boosted_power_scores.values())
    if total_power > 0:
        element_power_pct = {k: round((v / total_power) * 100, 1) for k, v in boosted_power_scores.items()}
    else:
        element_power_pct = {k: 0.0 for k in boosted_power_scores.keys()}
        
    element_power_scores = boosted_power_scores
    
    # Identify Dominant (과다) and Deficient/Lacking (결핍) Elements using Boosted Power Scores
    # Lacking: power is 0. If none is 0, list the minimum power.
    lacking_elements = [k for k, v in boosted_power_scores.items() if v == 0.0]
    if not lacking_elements:
        min_val = min(boosted_power_scores.values())
        lacking_elements = [k for k, v in boosted_power_scores.items() if v == min_val]
        
    # Dominant: highest power
    max_val = max(boosted_power_scores.values())
    dominant_elements = [k for k, v in boosted_power_scores.items() if v == max_val]

    # Calculate Temperature Index (조후 점수)
    # Hot elements/branches add +1, Cold elements/branches add -1
    temp_score = 0
    for p_name in active_pillars:
        p = pillars[p_name]
        # Stem Temp estimation
        if p['stem_element'] == '화':
            temp_score += 1
        elif p['stem_element'] == '수':
            temp_score -= 1
            
        # Branch Temp estimation
        bt = p['branch_temp']
        if bt == 'hot':
            temp_score += 1
        elif bt == 'cold':
            temp_score -= 1
            
    # Normalize temp rating
    if temp_score > 1:
        temp_name = 'hot'
        temp_kr = '따뜻하고 조열함 (Hot/Warm)'
    elif temp_score < -1:
        temp_name = 'cold'
        temp_kr = '차갑고 한랭함 (Cold/Cool)'
    else:
        temp_name = 'balanced'
        temp_kr = '온화하고 조화로움 (Neutral)'

    return {
        'pillars': pillars,
        'has_hour': has_hour,
        'day_stem': pillars['day']['stem_hanja'],
        'day_stem_kr': pillars['day']['stem_kr'],
        'day_stem_element': pillars['day']['stem_element'],
        'day_branch': pillars['day']['branch_hanja'],
        'day_branch_kr': pillars['day']['branch_kr'],
        'element_counts': element_counts,
        'element_percentages': element_pct,
        'element_power_scores': element_power_scores,
        'element_power_percentages': element_power_pct,
        'lacking_elements': lacking_elements,
        'dominant_elements': dominant_elements,
        'temp_score': temp_score,
        'temp_kr': temp_kr,
        'temp_name': temp_name,
        'luck_texts': STEM_LUCKS.get(pillars['day']['stem_hanja'], {}),
        'birth_date': f"{year}-{month:02d}-{day:02d}",
        'birth_time': f"{hour:02d}:{minute:02d}" if has_hour else "모름"
    }

def normalize_pair(a: str, b: str) -> tuple:
    """Returns sorted tuple to easily match combinations"""
    return (a, b) if a < b else (b, a)

def get_compatibility(user: Dict[str, Any], friend: Dict[str, Any]) -> Dict[str, Any]:
    """
    현대 명리학 기반의 사주 궁합 점수 및 설명 산출 엔진.
    4 영역(성향/가치관, 오행 보완, 일간/지지 결합, 운의 시너지)별 각 25점씩 총 100점 만점으로 평가.
    """
    stem_a = user['day_stem']
    stem_b = friend['day_stem']
    stem_a_kr = user['day_stem_kr']
    stem_b_kr = friend['day_stem_kr']
    el_a = user['day_stem_element']
    el_b = friend['day_stem_element']
    
    branch_a = user['day_branch']
    branch_b = friend['day_branch']
    branch_a_kr = user['day_branch_kr']
    branch_b_kr = friend['day_branch_kr']
    
    detailed_logs = {
        'values': [],
        'complement': [],
        'binding': [],
        'fortune': []
    }
    
    # --------------------------------------------------
    # 1. 성향 및 가치관 일치도 (Values Score) - Max 25
    # --------------------------------------------------
    values_score = 15
    values_desc = ""
    stem_pair = normalize_pair(stem_a, stem_b)
    
    if stem_pair in STEM_HARMONY:
        values_score = 25
        values_desc = f"✨ **가치관의 천생연분 (천간합)**: {STEM_HARMONY[stem_pair]}. 인생을 바라보는 눈높이와 지향점이 일치하여 서로의 말을 가장 잘 경청하는 최고의 소통 관계입니다."
        detailed_logs['values'].append({"item": "일간 소통 조화 (천간합)", "score": 25, "reason": "정신적 지향점이 완벽하게 일치하여 깊은 교감이 이루어짐"})
    elif el_a == el_b and user['pillars']['day']['stem_yinyang'] != friend['pillars']['day']['stem_yinyang']:
        values_score = 22
        values_desc = "🤝 **거울 같은 상호 이해 (비겁합)**: 같은 오행 기운이지만 음양이 다릅니다. 평생의 소울메이트처럼 서로의 가치관과 생각을 거울 보듯 완벽히 이해해 줍니다."
        detailed_logs['values'].append({"item": "일간 소통 조화 (비겁합)", "score": 22, "reason": "같은 기운에 음양이 조화로워 동질감과 깊은 상호 이해를 나눔"})
    elif GENERATION.get(el_a) == el_b or GENERATION.get(el_b) == el_a:
        values_score = 20
        sender = stem_a_kr if GENERATION.get(el_a) == el_b else stem_b_kr
        receiver = stem_b_kr if GENERATION.get(el_a) == el_b else stem_a_kr
        values_desc = f"🌱 **따뜻하고 생산적인 대화 (상생)**: {sender}의 생각이 {receiver}에게 부드러운 격려와 헌신적인 지지를 보내며 소통할수록 아이디어가 샘솟는 배려의 조합입니다."
        detailed_logs['values'].append({"item": "일간 소통 조화 (상생)", "score": 20, "reason": f"한쪽({sender})의 생각이 다른 쪽({receiver})을 포용하고 지지하는 소통 양식"})
    elif el_a == el_b:
        values_score = 18
        values_desc = f"👥 **동질감의 평행 소통 (비견)**: 두 분 다 '{el_a}' 기운으로 가치관이 매우 유사합니다. 친구처럼 편하지만 의견 충돌 시 고집을 부려 평행선을 달리지 않도록 조율이 필요합니다."
        detailed_logs['values'].append({"item": "일간 소통 조화 (비견)", "score": 18, "reason": "성향이 매우 유사하여 친근하나, 대립 시 각자의 고집 조율이 필요함"})
    elif stem_pair in STEM_CLASH:
        values_score = 12
        values_desc = f"⚡ **스파크 튀는 개성 소통 (천간충)**: {stem_a_kr}과 {stem_b_kr}이 정면으로 충돌합니다. 대화 스타일이나 사고방식에 확연한 차이가 있어 서로 다른 개성을 리스펙트하는 자세가 필수적입니다."
        detailed_logs['values'].append({"item": "일간 소통 조화 (천간충)", "score": 12, "reason": "가치관이 정면으로 부딪히는 성향으로 잦은 의견 대립 주의 요망"})
    elif OVERCOMING.get(el_a) == el_b or OVERCOMING.get(el_b) == el_a:
        values_score = 14
        controller = stem_a_kr if OVERCOMING.get(el_a) == el_b else stem_b_kr
        controlled = stem_b_kr if OVERCOMING.get(el_a) == el_b else stem_a_kr
        values_desc = f"⚠️ **긴장감 있는 조율 대화 (상극)**: {controller}의 강한 성향이 {controlled}을 리드하거나 간섭하는 흐름입니다. 서로 간의 적절한 영역 배려가 조화로운 가치관 유지를 돕습니다."
        detailed_logs['values'].append({"item": "일간 소통 조화 (상극)", "score": 14, "reason": f"{controller}의 기운이 {controlled}을 통제하는 경향이 있어 거리감 배려가 필요"})
    else:
        values_score = 16
        values_desc = "특별히 한쪽으로 쏠리지 않고 평범하고 상식적인 수준에서 원만하게 생각을 교류할 수 있는 일상적 성향 조합입니다."
        detailed_logs['values'].append({"item": "일간 소통 조화 (일반)", "score": 16, "reason": "특별한 시너 지나 대립이 없는 평범한 소통 관계"})

    # --------------------------------------------------
    # 2. 오행의 상호 보완성 (Complement Score) - Max 25
    # --------------------------------------------------
    # Eokbu (Max 15)
    eokbu_score = 5
    eokbu_reasons = []
    user_lacks = user['lacking_elements']
    friend_lacks = friend['lacking_elements']
    user_doms = user['dominant_elements']
    friend_doms = friend['dominant_elements']
    
    for lack in user_lacks:
        if lack in friend_doms:
            eokbu_score += 5
            eokbu_reasons.append(f"내 결핍 오행인 '{lack}' 기운을 상대방이 소유함")
        elif lack == el_b:
            eokbu_score += 3
            eokbu_reasons.append(f"내 결핍 오행 '{lack}' 기운이 상대의 본질임")
            
    for lack in friend_lacks:
        if lack in user_doms:
            eokbu_score += 4
            eokbu_reasons.append(f"상대의 결핍 오행 '{lack}' 기운을 내가 소유함")
        elif lack == el_a:
            eokbu_score += 2
            eokbu_reasons.append(f"상대의 결핍 오행 '{lack}' 기운이 나의 본질임")
            
    eokbu_score = min(eokbu_score, 15)
    if eokbu_reasons:
        detailed_logs['complement'].append({"item": "결핍 오행 보완 (억부)", "score": eokbu_score, "reason": ", ".join(eokbu_reasons)})
    else:
        detailed_logs['complement'].append({"item": "결핍 오행 보완 (억부)", "score": eokbu_score, "reason": "특별히 눈에 띄게 서로의 결핍 오행을 채워주는 구조는 아님 (중립)"})
    
    # Johu (Max 10)
    johu_score = 7
    ut = user['temp_name']
    ft = friend['temp_name']
    
    if (ut == 'hot' and ft == 'cold') or (ut == 'cold' and ft == 'hot'):
        johu_score = 10
        johu_desc = "뜨거운 열기와 차가운 한기가 절묘하게 섞여 서로가 편안한 심리적 안식처가 되어 줍니다."
        detailed_logs['complement'].append({"item": "온도 조화 (조후)", "score": johu_score, "reason": "열기와 한기가 만나 과열되거나 한랭한 사주의 온도를 서로 완벽하게 중화시킴"})
    elif ut == ft and ut in ['hot', 'cold']:
        johu_score = 5
        johu_desc = f"두 분 다 {ut == 'hot' and '더운' or '추운'} 성질에 치우쳐 감정 과잉이나 예민함이 증폭될 수 있어 휴식이 필요합니다."
        detailed_logs['complement'].append({"item": "온도 불균형 (조후)", "score": johu_score, "reason": f"두 사람 모두 {ut == 'hot' and '더운' or '추운'} 기운을 가져 온도 쏠림 현상이 발생"})
    else:
        johu_score = 8
        johu_desc = "조후 온도가 지나치게 춥거나 덥지 않고 쾌적하게 밸런스를 맞추는 무난하고 상쾌한 배치입니다."
        detailed_logs['complement'].append({"item": "무난한 온도 (조후)", "score": johu_score, "reason": "극단적 쏠림이 없어 쾌적하고 상쾌한 심리 상태 분위기 조성"})
        
    complement_score = min(eokbu_score + johu_score, 25)
    
    if eokbu_reasons:
        complement_desc = f"🧩 **오행·조후 보완**: " + ", ".join(eokbu_reasons[:2]) + f" ({johu_desc})"
    else:
        complement_desc = f"🧩 **오행·조후 보완**: 오행 배치는 평이하며, {johu_desc}"

    # --------------------------------------------------
    # 3. 일간 및 지지 결합도 (Binding Score) - Max 25
    # --------------------------------------------------
    # 일간 정신 교감(Max 10) + 일지 속궁합/생활습관(Max 15)
    stem_bond = 6
    stem_bond_reason = "평범한 수준의 정신적 교류"
    if stem_pair in STEM_HARMONY:
        stem_bond, stem_bond_reason = 10, "천간합으로 정신적 유대/공감대가 아주 강력함"
    elif el_a == el_b and user['pillars']['day']['stem_yinyang'] != friend['pillars']['day']['stem_yinyang']:
        stem_bond, stem_bond_reason = 9, "비겁합으로 서로의 본능을 깊이 이해하는 정서적 유대"
    elif GENERATION.get(el_a) == el_b or GENERATION.get(el_b) == el_a:
        stem_bond, stem_bond_reason = 8, "상생의 흐름으로 정신적 성장을 돕는 결속"
    elif el_a == el_b:
        stem_bond, stem_bond_reason = 7, "동질감을 기반으로 한 평온한 정신적 교감"
    elif stem_pair in STEM_CLASH:
        stem_bond, stem_bond_reason = 4, "천간충으로 인해 잦은 정서적 마찰 및 대립 우려"
    elif OVERCOMING.get(el_a) == el_b or OVERCOMING.get(el_b) == el_a:
        stem_bond, stem_bond_reason = 5, "상극 관계로 보이지 않는 정서적 압박감이 존재함"
        
    detailed_logs['binding'].append({"item": "정신적 끈끈함 (일간)", "score": stem_bond, "reason": stem_bond_reason})
        
    branch_bond = 9
    branch_bond_desc = ""
    branch_pair = normalize_pair(branch_a, branch_b)
    
    if branch_pair in BRANCH_SIX_HARMONY:
        branch_bond = 15
        branch_bond_desc = f"일지 육합({BRANCH_SIX_HARMONY[branch_pair]})으로 자석처럼 끌리는 강력한 현실적 속궁합"
        detailed_logs['binding'].append({"item": "현실 바탕 및 속궁합 (일지)", "score": branch_bond, "reason": "현실적 환경과 육체적 조화도가 완벽에 가까운 결합(육합)"})
    else:
        samhap_found = False
        for samhap_set, samhap_text in BRANCH_THREE_HARMONY:
            if branch_a in samhap_set and branch_b in samhap_set:
                branch_bond = 13
                branch_bond_desc = f"일지 삼합({samhap_text})으로 생활 습관과 인생 지향점이 굳건히 일치하는 궁합"
                detailed_logs['binding'].append({"item": "현실 바탕 및 속궁합 (일지)", "score": branch_bond, "reason": "미래를 향한 뜻과 일상적 지향점이 탁월한 시너지를 이룸(삼합)"})
                samhap_found = True
                break
        if not samhap_found:
            if branch_pair in BRANCH_CLASH:
                branch_bond = 4
                branch_bond_desc = f"일지 지지충({branch_a_kr} - {branch_b_kr} 충)으로 현실적 습관 차이 및 배려심 조율 필요"
                detailed_logs['binding'].append({"item": "현실 바탕 및 속궁합 (일지)", "score": branch_bond, "reason": "생활 습관, 성적 성향, 가정 환경이 정면으로 부딪혀 잦은 마찰(지지충)"})
            elif branch_pair in BRANCH_WONJIN:
                branch_bond = 5
                branch_bond_desc = f"일지 원진살({branch_a_kr} - {branch_b_kr} 원진)로 애증이 번갈아 찾아오는 드라마틱한 긴장 관계"
                detailed_logs['binding'].append({"item": "현실 바탕 및 속궁합 (일지)", "score": branch_bond, "reason": "미워하면서도 끌리게 되는 감정 소모와 애증의 갈등이 공존(원진)"})
            else:
                branch_bond = 10
                branch_bond_desc = "일지가 서로 부딪힘이 없이 평화로워 안정적인 일상을 이룰 수 있는 무난한 속궁합"
                detailed_logs['binding'].append({"item": "현실 바탕 및 속궁합 (일지)", "score": branch_bond, "reason": "안정적인 일상과 평범한 애정을 교류하는 모나지 않은 현실적 결합"})
                
    binding_score = min(stem_bond + branch_bond, 25)
    binding_desc = f"❤️ **교감 및 생활 밀착도**: 정신적 소통({stem_bond}/10)과 {branch_bond_desc} ({branch_bond}/15)."

    # --------------------------------------------------
    # 4. 운의 시너지 효과 (Fortune Score) - Max 25
    # --------------------------------------------------
    # 월지(사회/환경적 성공운) 및 연지(가문/기반운), 서로의 월지-일간 상생 분석
    fortune_score = 15
    fortune_reasons = []
    detailed_logs['fortune'].append({"item": "기본 시너지", "score": 15, "reason": "극단적 변화가 없는 한정된 기본 베이스 운세 점수"})
    
    month_a = user['pillars']['month']['branch_hanja']
    month_b = friend['pillars']['month']['branch_hanja']
    month_pair = normalize_pair(month_a, month_b)
    
    year_a = user['pillars']['year']['branch_hanja']
    year_b = friend['pillars']['year']['branch_hanja']
    year_pair = normalize_pair(year_a, year_b)
    
    # 월지 합/충 (Max +5, Min -3)
    if month_pair in BRANCH_SIX_HARMONY or any(month_a in s and month_b in s for s, t in BRANCH_THREE_HARMONY):
        fortune_score += 5
        fortune_reasons.append("사회적 운명과 활동 반경(월지 합)이 조화를 이루어 비즈니스, 인생 성장에 큰 발전운 공유")
        detailed_logs['fortune'].append({"item": "사회적 성장 조화 (월지 합)", "score": "+5", "reason": "직업 및 사회적 활동 환경이 시너지를 내어 동반 성공 유도"})
    elif month_pair in BRANCH_CLASH:
        fortune_score -= 3
        fortune_reasons.append("사회적 영역(월지 충)에 마찰이 있어, 직장이나 사회생활 스트레스 시기가 겹칠 우려")
        detailed_logs['fortune'].append({"item": "사회적 성장 마찰 (월지 충)", "score": "-3", "reason": "직업 방향성 및 사회 환경 변화의 엇박자로 스트레스가 겹침"})
    elif month_pair in BRANCH_WONJIN:
        fortune_score -= 2
        fortune_reasons.append("사회적 흐름의 이질감, 엇갈림(월지 원진)으로 공동 활동 시 세심한 조율 필요")
        detailed_logs['fortune'].append({"item": "사회적 성장 엇갈림 (월지 원진)", "score": "-2", "reason": "사회 환경 내에서 오해나 불편한 감정 소모가 잦은 시기가 옴"})
        
    # 연지 합/충 (Max +4, Min -2)
    if year_pair in BRANCH_SIX_HARMONY or any(year_a in s and year_b in s for s, t in BRANCH_THREE_HARMONY):
        fortune_score += 4
        fortune_reasons.append("가문과 조상운의 조화(연지 합)로 두 사람의 오랜 가치관적 뿌리가 화목하게 어우러짐")
        detailed_logs['fortune'].append({"item": "가문 및 기반 조화 (연지 합)", "score": "+4", "reason": "장기적인 집안 배경과 타고난 근본 운세가 탁월하게 상호작용"})
    elif year_pair in BRANCH_CLASH:
        fortune_score -= 2
        fortune_reasons.append("집안 환경이나 장기 연애 시 조상 자리(연지 충)의 충돌로 조심스러운 양보 필요")
        detailed_logs['fortune'].append({"item": "가문 및 기반 충돌 (연지 충)", "score": "-2", "reason": "조상의 뿌리나 장기적인 집안 가풍의 대립 가능성 존재"})
        
    # 일간과 상대 월지 간 상생 관계 (Max +6)
    u_month_el = user['pillars']['month']['branch_element']
    f_month_el = friend['pillars']['month']['branch_element']
    
    if GENERATION.get(u_month_el) == el_b or u_month_el == el_b:
        fortune_score += 3
        fortune_reasons.append(f"{user['day_stem_kr']}님이 상대방의 환경({f_month_el})으로부터 운의 조력을 입음")
        detailed_logs['fortune'].append({"item": "상생 조력", "score": "+3", "reason": f"{friend['day_stem_kr']}의 환경 기반이 {user['day_stem_kr']}의 본질을 지원하고 키워줌"})
    if GENERATION.get(f_month_el) == el_a or f_month_el == el_a:
        fortune_score += 3
        fortune_reasons.append(f"{friend['day_stem_kr']}님이 상대방의 환경({u_month_el})으로부터 운의 조력을 입음")
        detailed_logs['fortune'].append({"item": "상생 조력", "score": "+3", "reason": f"{user['day_stem_kr']}의 환경 기반이 {friend['day_stem_kr']}의 본질을 지원하고 키워줌"})
        
    fortune_score = max(10, min(fortune_score, 25))
    
    if fortune_reasons:
        fortune_desc = f"🍀 **운세 시너지**: " + ", ".join(fortune_reasons[:2]) + f" (상승지수: {fortune_score}/25)"
    else:
        fortune_desc = "🍀 **운세 시너지**: 활동 영역이나 운의 흐름이 큰 굴곡이나 충돌 없이 잔잔하여, 힘든 시기를 비껴가는 평온한 복을 나누어 가집니다."

    # 최종 점수 계산
    total_score = values_score + complement_score + binding_score + fortune_score
    
    # 점수별 궁합 등급과 해설 매핑
    if total_score >= 90:
        grade = "💖 천생연분 (Perfect Match)"
        grade_desc = "하늘과 땅이 모두 축복하는 최고의 인연입니다! 서로를 완벽히 채워주는 오행의 기운과 깊은 가치관의 교감, 평생을 밀어주고 당겨주는 환상의 운적 시너지가 결합된 귀한 짝꿍입니다."
    elif total_score >= 80:
        grade = "🌟 찰떡궁합 (Excellent Match)"
        grade_desc = "성향과 라이프스타일, 인생 흐름이 매우 조화롭게 어우러지는 인연입니다. 갈등이 오더라도 화합 오행의 자연스러운 보완성으로 쉽게 해결하고 알콩달콩 지낼 수 있습니다."
    elif total_score >= 70:
        grade = "☘️ 무난하고 좋은 궁합 (Good Match)"
        grade_desc = "이해심과 존중만 장착한다면 충분히 행복한 가정을 꾸릴 수 있는 기분 좋은 관계입니다. 서로가 조금씩만 배려해 준다면 더할 나위 없이 든든한 동반자가 됩니다."
    elif total_score >= 60:
        grade = "⚡ 매력적인 긴장 궁합 (Spicy Match)"
        grade_desc = "정반대의 자극적인 매력에 끌렸을 확률이 매우 높습니다! 서로의 고유한 습관과 다름을 있는 그대로 인정하고 배려해 준다면 독특하고 재미있는 케미스트리가 탄산수처럼 톡 튑니다."
    else:
        grade = "🌧️ 조심스런 노력 궁합 (Challenging Match)"
        grade_desc = "소통이나 생활 습관 면에서 각별한 배려와 인내가 요구되는 궁합입니다. 상대방을 고치려고 하기보다 그 사람의 그릇을 그대로 인정하는 수련의 과정을 나눈다면 한 걸음 더 성숙해질 수 있습니다."

    return {
        'total_score': total_score,
        'grade': grade,
        'grade_desc': grade_desc,
        'breakdown': {
            'values_score': values_score,
            'complement_score': complement_score,
            'binding_score': binding_score,
            'fortune_score': fortune_score
        },
        'explanations': {
            'values_desc': values_desc,
            'complement_desc': complement_desc,
            'binding_desc': binding_desc,
            'fortune_desc': fortune_desc
        },
        'detailed_logs': detailed_logs
    }

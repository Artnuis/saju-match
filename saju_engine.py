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
        
    total_power = sum(element_power_scores.values())
    if total_power > 0:
        element_power_pct = {k: round((v / total_power) * 100, 1) for k, v in element_power_scores.items()}
    else:
        element_power_pct = {k: 0.0 for k in element_power_scores.keys()}
    
    # Identify Dominant (과다) and Deficient/Lacking (결핍) Elements
    # Lacking: count is 0. If multiple are 0, we list all. If none is 0, list the minimum.
    lacking_elements = [k for k, v in element_counts.items() if v == 0]
    if not lacking_elements:
        min_val = min(element_counts.values())
        lacking_elements = [k for k, v in element_counts.items() if v == min_val]
        
    # Dominant: highest count
    max_val = max(element_counts.values())
    dominant_elements = [k for k, v in element_counts.items() if v == max_val]

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
    Computes Saju compatibility scores and details between user and friend.
    Returns scores out of 100 and explanatory texts.
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
    
    # ---------------------------------------------
    # 1. Daily Stem Harmony (일간 합/생극) - Max 30
    # ---------------------------------------------
    stem_score = 15
    stem_desc = ""
    stem_pair = normalize_pair(stem_a, stem_b)
    
    # Check Heavenly Stem Harmony (천간합)
    if stem_pair in STEM_HARMONY:
        stem_score = 30
        stem_desc = f"✨ **천생연분 일간합**: {STEM_HARMONY[stem_pair]}. 두 분은 정신적으로 깊이 교감하며 자석처럼 서로에게 강력하게 끌립니다."
    # Check same elements with opposite Yin-Yang
    elif el_a == el_b and user['pillars']['day']['stem_yinyang'] != friend['pillars']['day']['stem_yinyang']:
        stem_score = 25
        stem_desc = "🤝 **조화로운 비겁합**: 서로 같은 성질의 오행이지만 음양이 다른 관계입니다. 서로를 거울 삼아 마음 깊이 이해하며, 평생의 소울메이트처럼 편안합니다."
    # Check Generation (상생)
    elif GENERATION.get(el_a) == el_b or GENERATION.get(el_b) == el_a:
        stem_score = 22
        sender = stem_a_kr if GENERATION.get(el_a) == el_b else stem_b_kr
        receiver = stem_b_kr if GENERATION.get(el_a) == el_b else stem_a_kr
        stem_score = 22
        stem_desc = f"🌱 **따스한 상생(相生) 관계**: {sender}의 오행 기운이 {receiver}을 헌신적으로 지원해 주는 상생 구조입니다. 서로 성장할 수 있도록 격려하는 훌륭한 파트너가 됩니다."
    # Check Clash (천간충)
    elif stem_pair in STEM_CLASH:
        stem_score = 12
        stem_desc = f"⚡ **스파크 천간충**: {stem_a_kr}과 {stem_b_kr}은 서로 정면으로 부딪히는 기운을 가지고 있습니다. 때론 강렬한 매력을 느끼지만 가치관의 대립이 있을 수 있어 배려와 조율이 중요합니다."
    # Check Overcoming (상극)
    elif OVERCOMING.get(el_a) == el_b or OVERCOMING.get(el_b) == el_a:
        stem_score = 14
        controller = stem_a_kr if OVERCOMING.get(el_a) == el_b else stem_b_kr
        controlled = stem_b_kr if OVERCOMING.get(el_a) == el_b else stem_a_kr
        stem_desc = f"⚠️ **긴장감 있는 상극(相剋) 관계**: {controller}의 기운이 {controlled}을 극(剋)하는 관계입니다. 적당한 거리감과 조심스러운 태도가 특별한 매력이 되기도 합니다."
    else:
        # Same Element, Same Yin-Yang (비견)
        if el_a == el_b:
            stem_score = 18
            stem_desc = f"👥 **동성 동질 비견**: 둘 다 '{el_a}' 기운을 가졌습니다. 생각이 비슷해서 쉽게 친해지지만 서로 고집을 피우면 부딪히는 성향이 있습니다."
        else:
            stem_score = 16
            stem_desc = "평범하고 원만한 정신적 교류를 나눌 수 있는 편안한 사이입니다."

    # ---------------------------------------------
    # 2. Deficiency Complement (결핍 오행 보완) - Max 35
    # ---------------------------------------------
    def_score = 5
    def_reasons = []
    
    # Check user deficiencies vs friend abundances
    user_lacks = user['lacking_elements']
    friend_lacks = friend['lacking_elements']
    user_doms = user['dominant_elements']
    friend_doms = friend['dominant_elements']
    
    # Friend has User's lacking element in abundance or as daily stem element
    for lack in user_lacks:
        if lack in friend_doms:
            def_score += 15
            def_reasons.append(f"내게 부족한 **{lack}** 기운을 상대방이 넉넉히 가지고 있습니다")
        elif lack == el_b:
            def_score += 10
            def_reasons.append(f"내게 결핍된 **{lack}** 기운이 상대방의 본성(일간)입니다")
            
    # User has Friend's lacking element in abundance or as daily stem element
    for lack in friend_lacks:
        if lack in user_doms:
            def_score += 10
            def_reasons.append(f"상대에게 부족한 **{lack}** 기운을 내가 채워줄 수 있습니다")
        elif lack == el_a:
            def_score += 5
            def_reasons.append(f"상대에게 부족한 **{lack}** 기운이 나의 본성(일간)입니다")
            
    # Cap at 35, minimum 5
    def_score = min(def_score, 35)
    
    if def_reasons:
        def_desc = "🧩 **오행 보완**: " + ", ".join(def_reasons[:2]) + ". 사주의 불균형을 서로 완벽하게 메꿔주어 만날수록 마음이 편안해집니다."
    else:
        def_desc = "🪵 **오행 중립**: 두 분의 오행 구조가 서로 보완 작용을 일으키지는 않지만 무난하고 잔잔하게 섞이는 배치입니다."

    # ---------------------------------------------
    # 3. Daily Branch Harmony (일지 합/충) - Max 20
    # ---------------------------------------------
    branch_score = 12
    branch_desc = ""
    branch_pair = normalize_pair(branch_a, branch_b)
    
    # Six Combinations (육합)
    if branch_pair in BRANCH_SIX_HARMONY:
        branch_score = 20
        branch_desc = f"❤️ **속궁합 육합(六合)**: {BRANCH_SIX_HARMONY[branch_pair]}. 일상적인 성향과 육체적 조화(속궁합)가 가장 뛰어난 찰떡 관계입니다."
    else:
        # Check Three Combinations (삼합)
        samhap_found = False
        for samhap_set, samhap_text in BRANCH_THREE_HARMONY:
            if branch_a in samhap_set and branch_b in samhap_set:
                branch_score = 18
                branch_desc = f"🏆 **든든한 삼합(三合)**: {samhap_text}. 현실적인 지향점이 같아 동반자로서 최고의 조력자가 됩니다."
                samhap_found = True
                break
                
        if not samhap_found:
            # Check Clashes (지지충)
            if branch_pair in BRANCH_CLASH:
                branch_score = 6
                branch_desc = f"💥 **일지 지지충**: {branch_a_kr}과 {branch_b_kr}은 부딪히는 기운입니다. 사소한 습관이나 현실적 문제로 갈등이 생기기 쉬우나, 이를 극복하면 더 단단해집니다."
            # Check Wonjin (원진)
            elif branch_pair in BRANCH_WONJIN:
                branch_score = 5
                branch_desc = f"🕸️ **애증의 원진살**: {branch_a_kr}과 {branch_b_kr} 사이에는 애틋하면서도 미운 감정이 공존합니다. 묘한 끌림과 집착을 일으키기도 하는 로맨틱 스릴러 같은 궁합입니다."
            else:
                branch_score = 12
                branch_desc = "🏡 **안정적인 관계**: 일상과 가정을 꾸려가는 태도가 조화롭고 평온하여 부딪힘 없이 오랫동안 동반할 수 있는 사이입니다."

    # ---------------------------------------------
    # 4. Temperature Balance (조후 균형) - Max 15
    # ---------------------------------------------
    temp_score = 10
    temp_desc = ""
    
    ut = user['temp_name']
    ft = friend['temp_name']
    
    if (ut == 'hot' and ft == 'cold') or (ut == 'cold' and ft == 'hot'):
        temp_score = 15
        temp_desc = "🌡️ **조후 조화**: 뜨거운 에너지와 차가운 에너지가 만나 서로의 과열되거나 한랭한 상태를 녹이고 식혀줍니다. 서로에게 휴식처 같은 포근함을 줍니다."
    elif ut == ft and ut in ['hot', 'cold']:
        temp_score = 5
        temp_desc = f"🔥 **동일 온도**: 두 분 모두 {ut == 'hot' and '뜨거운' or '차가운'} 조후를 지니고 있어 한쪽 감정이나 상태로 쏠릴 수 있습니다. 서로 의식적으로 환기해 주는 노력이 유익합니다."
    else:
        temp_score = 10
        temp_desc = "🍃 **무난한 조후**: 온도가 적절하거나 균형이 맞아 과하거나 모자람 없이 상쾌하고 부드러운 분위기를 조성합니다."

    # Final Summary Score
    total_score = stem_score + def_score + branch_score + temp_score
    
    # Map score to descriptions
    if total_score >= 90:
        grade = "💖 천생연분 (Perfect Match)"
        grade_desc = "우주가 점지해 준 최고의 인연입니다! 서로를 채워주는 오행과 깊은 정신적 유대감이 결합하여 만나기 힘든 평생의 짝꿍입니다."
    elif total_score >= 80:
        grade = "🌟 찰떡궁합 (Excellent Match)"
        grade_desc = "성격과 라이프스타일 모두 조화로운 인연입니다. 큰 문제없이 서로를 존중하며 예쁜 사랑을 가꾸어 나갈 수 있습니다."
    elif total_score >= 70:
        grade = "☘️ 무난하고 좋은 궁합 (Good Match)"
        grade_desc = "서로 이해하고 존중하면 연인으로서 충분히 매력적인 관계입니다. 가끔 맞춰가야 할 부분이 있지만 대화로 쉽게 풀립니다."
    elif total_score >= 60:
        grade = "⚡ 매력적인 긴장 궁합 (Spicy Match)"
        grade_desc = "서로 성향이 아주 달라 첫눈에 깊이 끌렸을 가능성이 높습니다! 삐끗할 수 있는 부분만 미리 이해하고 배려한다면 색다르고 자극적인 재미가 가득합니다."
    else:
        grade = "🌧️ 조심스런 노력 궁합 (Challenging Match)"
        grade_desc = "서로를 위해 더 많은 이해와 인내가 요구되는 연애입니다. 상대방의 고유한 성향을 바꾸려 하지 않고 그대로 존중할 때 비로소 평온해집니다."

    return {
        'total_score': total_score,
        'grade': grade,
        'grade_desc': grade_desc,
        'breakdown': {
            'stem_score': stem_score,
            'def_score': def_score,
            'branch_score': branch_score,
            'temp_score': temp_score
        },
        'explanations': {
            'stem_desc': stem_desc,
            'def_desc': def_desc,
            'branch_desc': branch_desc,
            'temp_desc': temp_desc
        }
    }

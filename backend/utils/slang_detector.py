from detoxify import Detoxify

_slang_model = None
_cache = {}

def get_slang_model():
    global _slang_model
    if _slang_model is None:
        _slang_model = Detoxify('multilingual')
    return _slang_model

def detect_slang(text):
    """Returns True if text contains slang or offensive content in multiple languages"""
    if not text:
        return False
    
    # Check cache
    cache_key = f"slang:{hash(text)}"
    if cache_key in _cache:
        return _cache[cache_key]
    
    # Comprehensive offensive words database by language
    offensive_keywords = {
        # Spanish
        'puta', 'puto', 'mierda', 'coño', 'verga', 'chingar', 'pendejo', 
        'cabron', 'cabrón', 'joder', 'carajo', 'marica', 'culero', 'pinche',
        'hijo de puta', 'hijueputa', 'malparido', 'gonorrea', 'güey', 'wey',
        'chingada', 'chingado', 'mamada', 'mamón', 'boludo', 'pelotudo',
        'concha', 'conchudo', 'cagar', 'culo', 'huevón', 'huevon', 'pija',
        'chupame', 'chupa', 'la concha', 'perra', 'zorra', 'maricon',
        'maricón', 'putita', 'cabrona', 'vergas', 'cojones', 'chucha',
        'chimba', 'berraco', 'mamaverga', 'mamabicho', 'singao', 'singá',
        
        # French
        'putain', 'merde', 'connard', 'salope', 'enculé', 'chier', 'foutre',
        'bordel', 'bite', 'con', 'pute', 'couille', 'couilles', 'enfoiré',
        'encule', 'fils de pute', 'ta gueule', 'ferme ta gueule', 'va te faire',
        'nique', 'niquer', 'baise', 'baiser', 'casse-toi', 'chienne',
        'connasse', 'salaud', 'salopard', 'pétasse', 'branler', 'branleur',
        'con', 'conne', 'trou du cul', 'trouduc', 'tepu', 'pédé', 'tantouse',
        'tafiole', 'tapette', 'enculer', 'ta mère', 'mere', 'batard',
        'charogne', 'raclure', 'ordure', 'pouffiasse', 'grognasse',
        
        # English
        'fuck', 'fucking', 'fucker', 'fucked', 'motherfucker', 'fucks',
        'shit', 'shit', 'bullshit', 'shitty', 'shitter', 'shithouse',
        'bitch', 'bitches', 'bitching', 'son of a bitch',
        'ass', 'asshole', 'arse', 'arsehole', 'dumbass', 'badass',
        'damn', 'goddamn', 'dammit', 'damned',
        'cunt', 'cunts', 'dick', 'dickhead', 'dicks', 'prick',
        'bastard', 'bastards', 'whore', 'slut', 'sluts', 'slutty',
        'cock', 'cocks', 'pussy', 'pussies', 'twat', 'wanker',
        'bollocks', 'bugger', 'bloody', 'fag', 'faggot', 'dyke',
        'retard', 'retarded', 'moron', 'idiot', 'stupid ass',
        'jackass', 'douche', 'douchebag', 'scumbag', 'dipshit',
        'shithead', 'fuckface', 'cocksucker', 'bellend', 'tosser',
        'wank', 'knob', 'git', 'sod', 'pillock', 'minger',
        
        # German
        'scheiße', 'scheisse', 'scheiß', 'scheiss', 'kacke',
        'arschloch', 'arsch', 'fotze', 'hurensohn', 'wichser',
        'schlampe', 'verdammt', 'fick', 'ficken', 'gefickt',
        'sau', 'sausack', 'mistkerl', 'miststück', 'idiot',
        'blöd', 'dumm', 'schwein', 'schweinehund', 'drecksau',
        'dreck', 'scheißkerl', 'arschgesicht', 'arschgeige',
        'penner', 'spinner', 'vollidiot', 'vollpfosten', 'pfosten',
        'pisser', 'pisse', 'spast', 'spasti', 'mongo',
        'scheißegal', 'verdammte', 'himmel', 'hölle', 'teufel',
        'verflucht', 'gottverdammt', 'himmelherrgott',
        
        # Chinese (Simplified characters, Traditional, and Pinyin)
        '操', '肏', '草', '日', '幹', '干', '他妈的', '她妈的', '你妈的',
        '傻逼', '傻比', '沙比', '煞笔', '草泥马', '操你妈', '肏你妈',
        '妈的', '妈逼', '妈b', '婊子', '婊', '贱人', '贱',
        '混蛋', '王八蛋', '龟儿子', '狗娘养的', '狗屎', '屎',
        '滚', '滚蛋', '去死', '找死', '该死', '死全家',
        'fuck', '靠', '靠北', '靠腰', '靠夭', '他奶奶的',
        '他娘的', '老子', '你大爷', '装逼', '逼', 'sb', 'cnm',
        'cao', 'ri', 'gan', 'tamade', 'nimade', 'shabi', 'shaби',
        'caonima', 'biaozi', 'jiaren', 'hundan', 'wangbadan',
        'gou', 'gundan', 'qusi', 'gaisi', 'zhuangbi',
        
        # Japanese (Hiragana, Katakana, Kanji, and Romaji)
        'くそ', 'クソ', '糞', 'kuso', 'kusoyarou',
        'ばか', 'バカ', '馬鹿', 'baka', 'bakayarou', 'bakayaro',
        'ちくしょう', 'チクショウ', '畜生', 'chikushou', 'chikusho',
        'あほ', 'アホ', '阿呆', 'aho', 'ahou',
        'くたばれ', 'kutabare', 'しね', 'shine', '死ね', 'shinde',
        'きちがい', 'キチガイ', '気違い', 'kichigai',
        'てめえ', 'てめぇ', 'テメエ', 'temee', 'temē',
        'やろう', 'ヤロウ', '野郎', 'yarou', 'yaro',
        'うるさい', 'うるせえ', 'うるせぇ', 'urusai', 'urusee',
        'だまれ', 'ダマレ', '黙れ', 'damare',
        'きも', 'キモ', 'きもい', 'キモい', 'kimoi', 'kimo',
        'うざい', 'uzai', 'ウザい', 'ウザイ',
        'くず', 'クズ', '屑', 'kuzu',
        'げす', 'ゲス', '下種', 'gesu',
        'ぶす', 'ブス', 'busu',
        'ちんこ', 'chinko', 'まんこ', 'manko',
        'けつ', 'ケツ', '尻', 'ketsu',
        
        # Hebrew (Hebrew characters and transliterations)
        'זין', 'zayin', 'zain', 'za\'yin',
        'כוס', 'kus', 'koos', 'cus',
        'חרא', 'hara', 'khara', 'chara',
        'בן זונה', 'ben zona', 'benzόna',
        'שרמוטה', 'sharmouta', 'sharmuta', 'sharmota',
        'מניאק', 'maniac', 'manyak',
        'זונה', 'zona', 'zonah',
        'לך תזדיין', 'lech tizdayen', 'לכי תזדייני', 'lechi tizdayeni',
        'קוקסינל', 'kuksinel', 'cocksinel',
        'ערס', 'aras', 'ars',
        'פריאר', 'frayer', 'freier', 'fraier',
        'חארות', 'haraot', 'kharaot',
        'מזדיין', 'mizdayen', 'mizdayan',
        'לעזאזל', 'la\'azazel', 'laazazel',
        'חתיכת זבל', 'chatikhat zevel', 'zevel',
        'דפוק', 'dafuk', 'defuk',
        'מפגר', 'mefager', 'מטומטם', 'metumtam',
        'אידיוט', 'idiot', 'טמבל', 'tambal',
        'יבן', 'yaban', 'יא בן', 'ya ben',
        'כלב', 'kelev', 'kalba', 'כלבה',
        
        # Additional common variations and misspellings
        'f*ck', 'f**k', 'fu*k', 'fuk', 'fck', 'phuck',
        'sh*t', 's**t', 'sht', 'shyt', 'shite',
        'b*tch', 'b**ch', 'biatch', 'biotch', 'beatch',
        'a**', 'a**hole', 'azz', 'asz',
        'd*mn', 'd**n', 'dam', 'darn',
        'c*nt', 'c**t', 'cvnt',
        'pu$$y', 'p*ssy', 'psy',
        'n*gga', 'n***a', 'n1gga', 'nigga', 'nigger',
        'f@gg0t', 'f@gg*t', 'phag',
    }
    
    text_lower = text.lower()
    
    # Check for explicit keywords (fast path)
    if any(word in text_lower for word in offensive_keywords):
        _cache[cache_key] = True
        return True
    
    # ML-based detection with Detoxify
    try:
        model = get_slang_model()
        results = model.predict(text)
        
        # Multiple thresholds for better detection
        is_slang = (
            results['toxicity'] > 0.4 or
            results['obscene'] > 0.5 or
            results['insult'] > 0.5 or
            results['severe_toxicity'] > 0.3 or
            results['identity_attack'] > 0.4
        )
        
        _cache[cache_key] = is_slang
        
        # Limit cache size to prevent memory issues
        if len(_cache) > 1000:
            _cache.clear()
        
        return is_slang
    except Exception as e:
        return False

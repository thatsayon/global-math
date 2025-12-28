import re
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
    
    # Math-specific whitelist - common mathematical terms that might trigger false positives
    math_whitelist = {
        'dx', 'dy', 'dz', 'dt', 'du', 'dv', 'dw',  # Differentials
        'sin', 'cos', 'tan', 'sec', 'csc', 'cot',  # Trig functions
        'exp', 'log', 'ln',  # Exponential/log
        'ass', 'assume', 'assumption', 'class',  # Common in math (e.g., "assume x=1", "class of functions")
        'mass', 'gas', 'glass', 'pass', 'compass',  # Physics/geometry terms
        'tangent', 'secant', 'asymptote',
        'factorial', 'fact',
        'expression', 'expressions',
        'function', 'functions',
    }
    
    # Check if text is primarily mathematical
    text_lower = text.lower()
    words = re.findall(r'\b\w+\b', text_lower)
    
    # If text contains math symbols or whitelisted terms, be more lenient
    math_symbols_pattern = r'[∫∑∏√∂∆∇≠≈≤≥±×÷∞π∈∉⊂⊃∪∩∧∨¬∀∃]|[\d]+|[xy][\d]+|d[xyztuv]/d[xyztuv]|[a-z]\^[\d]+|\b(sin|cos|tan|log|ln|exp|lim|integral|derivative|equation|solve|theorem|proof|formula|calculate)\b'
    has_math_context = bool(re.search(math_symbols_pattern, text_lower))
    
    # Comprehensive offensive words database by language
    # Using WORD BOUNDARIES to prevent partial matches
    offensive_keywords = {
        # Spanish (using word boundaries)
        r'\bputa\b', r'\bputo\b', r'\bmierda\b', r'\bcoño\b', r'\bverga\b', 
        r'\bchingar\b', r'\bpendejo\b', r'\bcabron\b', r'\bcabrón\b', 
        r'\bjoder\b', r'\bcarajo\b', r'\bmarica\b', r'\bculero\b', r'\bpinche\b',
        r'\bhijo de puta\b', r'\bhijueputa\b', r'\bmalparido\b', r'\bgonorrea\b',
        r'\bgüey\b', r'\bwey\b', r'\bchingada\b', r'\bchingado\b', r'\bmamada\b',
        r'\bmamón\b', r'\bboludo\b', r'\bpelotudo\b', r'\bconcha\b', r'\bconchudo\b',
        r'\bcagar\b', r'\bculo\b', r'\bhuevón\b', r'\bhuevon\b', r'\bpija\b',
        r'\bchupame\b', r'\bchupa\b', r'\bla concha\b', r'\bperra\b', r'\bzorra\b',
        r'\bmaricon\b', r'\bmaricón\b', r'\bputita\b', r'\bcabrona\b', r'\bvergas\b',
        r'\bcojones\b', r'\bchucha\b', r'\bchimba\b', r'\bberraco\b', r'\bmamaverga\b',
        r'\bmamabicho\b', r'\bsingao\b', r'\bsingá\b',
        
        # French
        r'\bputain\b', r'\bmerde\b', r'\bconnard\b', r'\bsalope\b', r'\benculé\b',
        r'\bchier\b', r'\bfoutre\b', r'\bbordel\b', r'\bbite\b', r'\bcon\b',
        r'\bpute\b', r'\bcouille\b', r'\bcouilles\b', r'\benfoiré\b', r'\bencule\b',
        r'\bfils de pute\b', r'\bta gueule\b', r'\bferme ta gueule\b', r'\bva te faire\b',
        r'\bnique\b', r'\bniquer\b', r'\bbaise\b', r'\bbaiser\b', r'\bcasse-toi\b',
        r'\bchienne\b', r'\bconnasse\b', r'\bsalaud\b', r'\bsalopard\b', r'\bpétasse\b',
        r'\bbranler\b', r'\bbranleur\b', r'\bconne\b', r'\btrou du cul\b', r'\btrouduc\b',
        r'\btepu\b', r'\bpédé\b', r'\btantouse\b', r'\btafiole\b', r'\btapette\b',
        r'\benculer\b', r'\bta mère\b', r'\bmere\b', r'\bbatard\b', r'\bcharogne\b',
        r'\braclure\b', r'\bordure\b', r'\bpouffiasse\b', r'\bgrognasse\b',
        
        # English (with word boundaries to avoid false positives)
        r'\bfuck\b', r'\bfucking\b', r'\bfucker\b', r'\bfucked\b', r'\bmotherfucker\b',
        r'\bfucks\b', r'\bshit\b', r'\bbullshit\b', r'\bshitty\b', r'\bshitter\b',
        r'\bshithouse\b', r'\bbitch\b', r'\bbitches\b', r'\bbitching\b',
        r'\bson of a bitch\b', r'\basshole\b', r'\barse\b', r'\barsehole\b',
        r'\bdumbass\b', r'\bbadass\b', r'\bdamn\b', r'\bgoddamn\b', r'\bdammit\b',
        r'\bdamned\b', r'\bcunt\b', r'\bcunts\b', r'\bdick\b', r'\bdickhead\b',
        r'\bdicks\b', r'\bprick\b', r'\bbastard\b', r'\bbastards\b', r'\bwhore\b',
        r'\bslut\b', r'\bsluts\b', r'\bslutty\b', r'\bcock\b', r'\bcocks\b',
        r'\bpussy\b', r'\bpussies\b', r'\btwat\b', r'\bwanker\b', r'\bbollocks\b',
        r'\bbugger\b', r'\bbloody\b', r'\bfag\b', r'\bfaggot\b', r'\bdyke\b',
        r'\bretard\b', r'\bretarded\b', r'\bmoron\b', r'\bidiot\b', r'\bstupid ass\b',
        r'\bjackass\b', r'\bdouche\b', r'\bdouchebag\b', r'\bscumbag\b', r'\bdipshit\b',
        r'\bshithead\b', r'\bfuckface\b', r'\bcocksucker\b', r'\bbellend\b',
        r'\btosser\b', r'\bwank\b', r'\bknob\b', r'\bgit\b', r'\bsod\b',
        r'\bpillock\b', r'\bminger\b',
        
        # German
        r'\bscheiße\b', r'\bscheisse\b', r'\bscheiß\b', r'\bscheiss\b', r'\bkacke\b',
        r'\barschloch\b', r'\barsch\b', r'\bfotze\b', r'\bhurensohn\b', r'\bwichser\b',
        r'\bschlampe\b', r'\bverdammt\b', r'\bfick\b', r'\bficken\b', r'\bgefickt\b',
        r'\bsau\b', r'\bsausack\b', r'\bmistkerl\b', r'\bmiststück\b', r'\bidiot\b',
        r'\bblöd\b', r'\bdumm\b', r'\bschwein\b', r'\bschweinehund\b', r'\bdrecksau\b',
        r'\bdreck\b', r'\bscheißkerl\b', r'\barschgesicht\b', r'\barschgeige\b',
        r'\bpenner\b', r'\bspinner\b', r'\bvollidiot\b', r'\bvollpfosten\b',
        r'\bpfosten\b', r'\bpisser\b', r'\bpisse\b', r'\bspast\b', r'\bspasti\b',
        r'\bmongo\b', r'\bscheißegal\b', r'\bverdammte\b', r'\bhimmel\b',
        r'\bhölle\b', r'\bteufel\b', r'\bverflucht\b', r'\bgottverdammt\b',
        r'\bhimmelherrgott\b',
        
        # Chinese (Simplified, Traditional, Pinyin)
        '操', '肏', '草', '日', '幹', '干', '他妈的', '她妈的', '你妈的',
        '傻逼', '傻比', '沙比', '煞笔', '草泥马', '操你妈', '肏你妈',
        '妈的', '妈逼', '妈b', '婊子', '婊', '贱人', '贱',
        '混蛋', '王八蛋', '龟儿子', '狗娘养的', '狗屎', '屎',
        '滚', '滚蛋', '去死', '找死', '该死', '死全家',
        '靠', '靠北', '靠腰', '靠夭', '他奶奶的',
        '他娘的', '老子', '你大爷', '装逼', '逼',
        r'\bsb\b', r'\bcnm\b', r'\bcao\b', r'\bri\b', r'\bgan\b',
        r'\btamade\b', r'\bnimade\b', r'\bshabi\b', r'\bcaonima\b',
        r'\bbiaozi\b', r'\bjiaren\b', r'\bhundan\b', r'\bwangbadan\b',
        r'\bgou\b', r'\bgundan\b', r'\bqusi\b', r'\bgaisi\b', r'\bzhuangbi\b',
        
        # Japanese
        'くそ', 'クソ', '糞', 'ばか', 'バカ', '馬鹿', 'ちくしょう', 'チクショウ',
        '畜生', 'あほ', 'アホ', '阿呆', 'くたばれ', 'しね', '死ね',
        'きちがい', 'キチガイ', '気違い', 'てめえ', 'てめぇ', 'テメエ',
        'やろう', 'ヤロウ', '野郎', 'うるさい', 'うるせえ', 'うるせぇ',
        'だまれ', 'ダマレ', '黙れ', 'きも', 'キモ', 'きもい', 'キモい',
        'うざい', 'ウザい', 'ウザイ', 'くず', 'クズ', '屑',
        'げす', 'ゲス', '下種', 'ぶす', 'ブス',
        'ちんこ', 'まんこ', 'けつ', 'ケツ', '尻',
        r'\bkuso\b', r'\bkusoyarou\b', r'\bbaka\b', r'\bbakayarou\b',
        r'\bbakayaro\b', r'\bchikushou\b', r'\bchikusho\b', r'\baho\b',
        r'\bahou\b', r'\bkutabare\b', r'\bshine\b', r'\bshinde\b',
        r'\bkichigai\b', r'\btemee\b', r'\byarou\b', r'\byaro\b',
        r'\burusai\b', r'\burusee\b', r'\bdarame\b', r'\bkimoi\b',
        r'\bkimo\b', r'\buzai\b', r'\bkuzu\b', r'\bgesu\b',
        r'\bbusu\b', r'\bchinko\b', r'\bmanko\b', r'\bketsu\b',
        
        # Hebrew
        'זין', 'כוס', 'חרא', 'בן זונה', 'שרמוטה', 'מניאק', 'זונה',
        'לך תזדיין', 'לכי תזדייני', 'קוקסינל', 'ערס', 'פריאר',
        'חארות', 'מזדיין', 'לעזאזל', 'חתיכת זבל', 'דפוק',
        'מפגר', 'מטומטם', 'אידיוט', 'טמבל', 'יבן', 'יא בן', 'כלב', 'כלבה',
        r'\bzayin\b', r'\bzain\b', r'\bkus\b', r'\bkoos\b', r'\bcus\b',
        r'\bhara\b', r'\bkhara\b', r'\bchara\b', r'\bben zona\b',
        r'\bsharmouta\b', r'\bsharmuta\b', r'\bsharmota\b', r'\bmaniac\b',
        r'\bmanyak\b', r'\bzona\b', r'\bzonah\b', r'\blech tizdayen\b',
        r'\blechi tizdayeni\b', r'\bkuksinel\b', r'\baras\b', r'\bars\b',
        r'\bfrayer\b', r'\bfreier\b', r'\bfraier\b', r'\bharaot\b',
        r'\bkharaot\b', r'\bmizdayen\b', r'\bmizdayan\b', r'\blaazazel\b',
        r'\bzevel\b', r'\bdafuk\b', r'\bdefuk\b', r'\bmefager\b',
        r'\bmetumtam\b', r'\btambal\b', r'\byaban\b', r'\bkelev\b', r'\bkalba\b',
        
        # Common variations with special characters (word boundaries)
        r'\bf\*ck\b', r'\bf\*\*k\b', r'\bfu\*k\b', r'\bfuk\b', r'\bfck\b', r'\bphuck\b',
        r'\bsh\*t\b', r'\bs\*\*t\b', r'\bsht\b', r'\bshyt\b', r'\bshite\b',
        r'\bb\*tch\b', r'\bb\*\*ch\b', r'\bbiatch\b', r'\bbiotch\b', r'\bbeatch\b',
        r'\ba\*\*\b', r'\ba\*\*hole\b', r'\bazz\b', r'\basz\b',
        r'\bd\*mn\b', r'\bd\*\*n\b', r'\bdam\b', r'\bdarn\b',
        r'\bc\*nt\b', r'\bc\*\*t\b', r'\bcvnt\b',
        r'\bpu\$\$y\b', r'\bp\*ssy\b', r'\bpsy\b',
        r'\bn\*gga\b', r'\bn\*\*\*a\b', r'\bn1gga\b', r'\bnigga\b', r'\bnigger\b',
        r'\bf@gg0t\b', r'\bf@gg\*t\b', r'\bphag\b',
    }
    
    # First check: Explicit keyword matching with word boundaries and math context awareness
    matched_offensive = False
    for pattern in offensive_keywords:
        if isinstance(pattern, str) and not pattern.startswith(r'\b'):
            # Non-Latin characters (Chinese, Japanese, Hebrew, etc.)
            if pattern in text_lower:
                matched_offensive = True
                break
        else:
            # Latin characters with word boundaries
            if re.search(pattern, text_lower, re.IGNORECASE):
                # Check if it's a math whitelisted term
                match = re.search(pattern, text_lower, re.IGNORECASE)
                if match:
                    matched_word = match.group(0).strip(r'\b')
                    if matched_word not in math_whitelist:
                        matched_offensive = True
                        break
    
    # If in math context and no strong offensive match, be lenient
    if has_math_context and not matched_offensive:
        _cache[cache_key] = False
        return False
    
    if matched_offensive:
        _cache[cache_key] = True
        return True
    
    # ML-based detection with Detoxify (with adjusted thresholds for math content)
    try:
        model = get_slang_model()
        results = model.predict(text)
        
        # Adjust thresholds based on math context
        if has_math_context:
            # Be more lenient for math content
            is_slang = (
                results['toxicity'] > 0.7 or
                results['obscene'] > 0.8 or
                results['insult'] > 0.75 or
                results['severe_toxicity'] > 0.6
            )
        else:
            # Standard thresholds for non-math content
            is_slang = (
                results['toxicity'] > 0.5 or
                results['obscene'] > 0.6 or
                results['insult'] > 0.6 or
                results['severe_toxicity'] > 0.4 or
                results['identity_attack'] > 0.5
            )
        
        _cache[cache_key] = is_slang
        
        # Limit cache size to prevent memory issues
        if len(_cache) > 1000:
            _cache.clear()
        
        return is_slang
    except Exception as e:
        # If ML model fails, rely on keyword matching
        return matched_offensive

from celery import shared_task
from core.utils import translate_text, translate_texts_batch
from administration.models import DailyChallenge, DailyChallengeTranslation, ChallengeQuestionTranslation

import logging
import time
logger = logging.getLogger(__name__)

@shared_task
def translate_challenge_task(challenge_id):
    try:
        challenge = DailyChallenge.objects.get(id=challenge_id)
        source_lang = 'en' # challenges are generated in English
        target_languages = ['en', 'es', 'fr', 'de', 'zh', 'ja', 'he']
        
        for lang in target_languages:
            if lang == source_lang:
                continue
                
            # Gather all texts to translate
            questions = list(challenge.questions.all())
            texts_to_translate = [challenge.name, challenge.description]
            for q in questions:
                texts_to_translate.append(q.question_text)
                texts_to_translate.append(q.answer)
                
            translated_texts = translate_texts_batch(texts_to_translate, target_lang=lang, source_lang=source_lang)
            
            translated_name = translated_texts[0]
            translated_desc = translated_texts[1]
            
            DailyChallengeTranslation.objects.update_or_create(
                challenge=challenge,
                language=lang,
                defaults={
                    'translated_name': translated_name,
                    'translated_description': translated_desc
                }
            )
            
            # Translate Challenge questions
            offset = 2
            for q in questions:
                translated_q_text = translated_texts[offset]
                translated_answer = translated_texts[offset+1]
                offset += 2
                
                ChallengeQuestionTranslation.objects.update_or_create(
                    question=q,
                    language=lang,
                    defaults={
                        'translated_question_text': translated_q_text,
                        'translated_answer': translated_answer
                    }
                )
    except DailyChallenge.DoesNotExist:
        logger.error(f"Challenge {challenge_id} not found for translation")
    except Exception as e:
        logger.error(f"Failed to translate challenge {challenge_id}: {str(e)}")


@shared_task
def translate_math_level_task(math_level_id):
    from administration.models import MathLevels, MathLevelTranslation
    try:
        math_level = MathLevels.objects.get(id=math_level_id)
        source_lang = 'en'
        target_languages = ['en', 'es', 'fr', 'de', 'zh', 'ja', 'he']
        
        for lang in target_languages:
            if lang == source_lang:
                continue
                
            translated_name = translate_text(math_level.name, target_lang=lang, source_lang=source_lang)
            
            MathLevelTranslation.objects.update_or_create(
                math_level=math_level,
                language=lang,
                defaults={
                    'translated_name': translated_name
                }
            )
    except MathLevels.DoesNotExist:
        logger.error(f"MathLevels {math_level_id} not found for translation")
    except Exception as e:
        logger.error(f"Failed to translate math level {math_level_id}: {str(e)}")

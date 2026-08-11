from celery import shared_task
from core.utils import translate_text
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
                
            # Translate Challenge details
            translated_name = translate_text(challenge.name, target_lang=lang, source_lang=source_lang)
            time.sleep(0.5)
            translated_desc = translate_text(challenge.description, target_lang=lang, source_lang=source_lang)
            time.sleep(0.5)
            
            DailyChallengeTranslation.objects.update_or_create(
                challenge=challenge,
                language=lang,
                defaults={
                    'translated_name': translated_name,
                    'translated_description': translated_desc
                }
            )
            
            # Translate Challenge questions
            for question in challenge.questions.all():
                translated_q_text = translate_text(question.question_text, target_lang=lang, source_lang=source_lang)
                time.sleep(0.5)
                translated_answer = translate_text(question.answer, target_lang=lang, source_lang=source_lang)
                time.sleep(0.5)
                
                ChallengeQuestionTranslation.objects.update_or_create(
                    question=question,
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

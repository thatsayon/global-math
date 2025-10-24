import io
import re
import json
import requests
from PIL import Image
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework import status
from .utils import process_math_problem, extract_text_from_genai_response, classification_model
import logging

# Root: serve static/index.html if present, otherwise simple redirect-style HTML
@api_view(['GET'])
def root(request):
    try:
        with open('static/index.html', 'r', encoding='utf-8') as f:
            return HttpResponse(f.read(), content_type='text/html')
    except FileNotFoundError:
        html = """
        <html>
            <head>
                <title>Math Bot & Message Classifier</title>
                <meta http-equiv="refresh" content="0; URL='/static/index.html'" />
            </head>
            <body>
                <p>Redirecting to <a href="/static/index.html">the application</a>...</p>
            </body>
        </html>
        """
        return HttpResponse(html, content_type='text/html')

# @csrf_exempt
# @api_view(['POST'])
# @parser_classes([FormParser, MultiPartParser])
# def solve_text_problem(request):
#     problem = request.data.get('problem')
#     if not problem or not str(problem).strip():
#         return JsonResponse({"detail": "Field 'problem' is required."}, status=400)
#     prompt = f"""
#     Solve the following math problem. Provide a clear, step-by-step solution in natural language.
#     Use LaTeX formatting for mathematical expressions (enclose in $ for inline and $$ for display equations).
#     Avoid markdown formatting except for LaTeX.

#     Problem: {problem}

#     Format your response with clear steps and a final answer.
#     """
#     try:
#         solution = process_math_problem(prompt)
#         return JsonResponse({"problem": problem, "solution": solution})
#     except Exception as e:
#         return JsonResponse({"detail": str(e)}, status=500)


logger = logging.getLogger(__name__)

@csrf_exempt
@api_view(['POST'])
@parser_classes([FormParser, MultiPartParser])
def solve_text_problem(request):
    problem = request.data.get('problem')
    
    if not problem or not str(problem).strip():
        # This is a client-side error (missing input)
        return JsonResponse({"detail": "Field 'problem' is required."}, status=400)
    
    # --- MODIFIED PROMPT to include failure keywords ---
    prompt = f"""
Solve the following math problem. Provide a clear, step-by-step solution in natural language.

**IMPORTANT RULES:**
1.  If the input **is not a math problem** (e.g., it's a random sentence, a name, or non-math content), you must return only the word "NULL".
2.  If the input **is a math problem, but you cannot understand it** (e.g., it's ambiguous, ill-posed, or contains undefined variables) or **you cannot solve it** (e.g., it's too complex or requires external data), you must return only the word "UNSOLVABLE".
3.  If a math problem IS present and you CAN solve it, provide a clear, step-by-step solution. Use LaTeX formatting for mathematical expressions (enclose in $ for inline and $$ for display equations). Avoid markdown formatting except for LaTeX.

Problem: {problem}
"""
    try:
        # Call your existing processing function (assuming it takes only the prompt)
        solution = process_math_problem(prompt)

        # --- NEW LOGIC START ---
        
        # Check for None or empty string first
        if not solution or not solution.strip():
            logger.warning("AI returned an empty or None response.")
            # Status 1 for system/data failure
            return JsonResponse({"status": 1})

        # Clean the response for reliable checking
        solution_clean = solution.strip().upper()

        if solution_clean == "NULL":
            # Status 1: Not a math problem
            return JsonResponse({"status": 1})
        
        elif solution_clean == "UNSOLVABLE":
            # Status 2: Math problem found but could not be solved/understood
            return JsonResponse({
                "status": 2, 
                "message": "I am unable to understand the math question or provide a solution."
            })
            
        else:
            # Status 0: Success
            return JsonResponse({"status": 0, "solution": solution.strip()})
        
        # --- NEW LOGIC END ---

    except Exception as e:
        # Status 1 for system error
        logger.error(f"Error processing text math problem: {str(e)}")
        return JsonResponse({"status": 1})





# @csrf_exempt
# @api_view(['POST'])
# @parser_classes([MultiPartParser, FormParser])
# def solve_image_problem(request):
#     file = request.FILES.get('file')
#     if file is None or not file.content_type.startswith('image/'):
#         return JsonResponse({"detail": "File must be an image"}, status=400)
#     try:
#         image_data = file.read()
#         prompt = """
#         Extract and solve the math problem from this image. Provide a clear, step-by-step solution in natural language.
#         Use LaTeX formatting for mathematical expressions (enclose in $ for inline and $$ for display equations).
#         Avoid markdown formatting except for LaTeX.

#         Format your response with clear steps and a final answer.
#         """
#         img = Image.open(io.BytesIO(image_data))
#         solution = process_math_problem(prompt, img)
#         return JsonResponse({"solution": solution})
#     except Exception as e:
#         return JsonResponse({"detail": str(e)}, status=500)

logger = logging.getLogger(__name__)
@csrf_exempt
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def solve_image_problem(request):
    file = request.FILES.get('file')
    if file is None or not file.content_type.startswith('image/'):
        return JsonResponse({"detail": "File must be an image"}, status=400)

    try:
        image_data = file.read()
        
        # --- PROMPT (Remains the same for the AI to return the correct keywords) ---
        prompt = """
Extract and solve the math problem from this image.

**IMPORTANT RULES:**
1.  If the image **does not contain any math problem** (e.g., it's a picture
    of food, people, objects), you must return only the word "NULL".
2.  If the image **contains a math problem, but you cannot understand it** (e.g., it's too blurry, badly handwritten) or **you cannot solve it**
    (e.g., it's too complex, ambiguous, or lacks information), you
    must return only the word "UNSOLVABLE".
3.  If a math problem IS present and you CAN solve it, provide a clear,
    step-by-step solution in natural language. Use LaTeX formatting
    (enclose in $ for inline and $$ for display equations).
    Avoid markdown formatting except for LaTeX.
        """
        img = Image.open(io.BytesIO(image_data))
        
        # Call your existing processing function
        solution = process_math_problem(prompt, img)

        # --- UPDATED LOGIC ---
        
        # Check for None or empty string first
        if not solution or not solution.strip():
            logger.warning("AI returned an empty or None response.")
            # Status 1 for system/data failure
            return JsonResponse({"status": 1})

        # Clean the response for reliable checking
        solution_clean = solution.strip().upper()

        if solution_clean == "NULL":
            # Status 1: No math problem found
            return JsonResponse({"status": 1})
        
        elif solution_clean == "UNSOLVABLE":
            # Status 2: Math problem found but could not be solved/understood
            # Providing the simple response here
            return JsonResponse({
                "status": 2, 
                "message": "I am unable to understand the math question or provide a solution."
            })
            
        else:
            # Status 0: Success
            return JsonResponse({"status": 0, "solution": solution.strip()})
        
        # --- END UPDATED LOGIC ---

    except Exception as e:
        # Status 1 for system error
        logger.error(f"Error processing math image: {str(e)}")
        return JsonResponse({"status": 1})





# @csrf_exempt
# @api_view(['POST'])
# @parser_classes([MultiPartParser, FormParser])
# def solve_image_with_prompt(request):
#     file = request.FILES.get('file')
#     prompt = request.data.get('prompt')

#     if file is None and (prompt is None or str(prompt).strip() == ""):
#         return JsonResponse({"detail": "Provide an image file, a text prompt, or both."}, status=400)

#     try:
#         img = None
#         if file is not None:
#             if not file.content_type.startswith('image/'):
#                 return JsonResponse({"detail": "File must be an image"}, status=400)
#             image_bytes = file.read()
#             try:
#                 img = Image.open(io.BytesIO(image_bytes))
#             except Exception:
#                 return JsonResponse({"detail": "Could not open image. Ensure it's a valid image file."}, status=400)

#         if not prompt or str(prompt).strip() == "":
#             prompt = """
#             Extract and solve the math problem from this image. Provide a clear, step-by-step solution in natural language.
#             Use LaTeX formatting for mathematical expressions (enclose in $ for inline and $$ for display equations).
#             Avoid markdown formatting except for LaTeX.

#             Format your response with clear steps and a final answer.
#             """

#         solution = process_math_problem(prompt, img) if img is not None else process_math_problem(prompt)

#         response_content = {
#             "solution": solution,
#             "input": {
#                 "provided_image": bool(img),
#                 "provided_prompt": bool(prompt and str(prompt).strip() != "")
#             }
#         }
#         if file is not None:
#             response_content["input"]["image_filename"] = file.name
#         if prompt is not None:
#             response_content["user_prompt"] = prompt

#         return JsonResponse(response_content)
#     except Exception as e:
#         return JsonResponse({"detail": str(e)}, status=500)
    

# solve_image_with_prompt with 3-status logic


logger = logging.getLogger(__name__)

FAILURE_NULL = "NULL"
FAILURE_UNSOLVABLE = "UNSOLVABLE"

CORE_MATH_PROMPT_TEMPLATE = """
Solve the following math problem. Provide a clear, step-by-step solution in natural language.

**PROBLEM INPUT:**
{problem_content}

**INSTRUCTION RULES:**
1.  Use LaTeX formatting for mathematical expressions (enclose in $ for inline and $$ for display equations).
2.  Avoid markdown formatting except for LaTeX.

**FAILURE RULES (For System Status):**
1.  If the input (text or image) **does not contain any math problem**, you must return **only** the word "{failure_null}".
2.  If the input **contains a math problem, but you cannot understand it** (e.g., too blurry, ambiguous) or **you cannot solve it** (e.g., too complex, lacks data), you must return **only** the word "{failure_unsolvable}".
3.  Otherwise, provide the solution.
"""

# =========================================================================

@csrf_exempt
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def solve_image_with_prompt(request):
    """Handles combined image and optional text prompt solving with 3-status logic."""
    
    # NOTE: The function process_math_problem must be defined and imported elsewhere.
    # It must be callable as: process_math_problem(prompt, img) or process_math_problem(prompt)

    file = request.FILES.get('file')
    user_prompt = request.data.get('prompt')

    if file is None and (user_prompt is None or str(user_prompt).strip() == ""):
        return JsonResponse({"detail": "Provide an image file, a text prompt, or both."}, status=400)

    try:
        img = None
        if file is not None:
            if not file.content_type.startswith('image/'):
                return JsonResponse({"detail": "File must be an image"}, status=400)
            image_bytes = file.read()
            try:
                img = Image.open(io.BytesIO(image_bytes))
            except Exception:
                return JsonResponse({"detail": "Could not open image. Ensure it's a valid image file."}, status=400)

        # 1. Determine problem description for the unified prompt
        if img and user_prompt and str(user_prompt).strip() != "":
            problem_description = f"Solve the problem based on the provided image and this clarifying text: {user_prompt}"
        elif img:
            problem_description = "The math problem is contained within the uploaded image."
        elif user_prompt and str(user_prompt).strip() != "":
            problem_description = f"The problem text is: {user_prompt}"
        else:
            problem_description = "Solve the provided problem."
        
        # Format the core prompt with the specific problem content and failure keywords
        final_prompt = CORE_MATH_PROMPT_TEMPLATE.format(
            problem_content=problem_description,
            failure_null=FAILURE_NULL,
            failure_unsolvable=FAILURE_UNSOLVABLE
        )

        # 2. Process the problem
        solution = process_math_problem(final_prompt, img) if img is not None else process_math_problem(final_prompt)
        
        # 3. Check status and prepare full response (Logic moved inside this function)
        
        # Initialize response dictionary
        response_content = {} 
        
        # Check for None or empty string first (System failure)
        if not solution or not solution.strip():
            logger.warning("AI returned an empty or None response.")
            response_content["status"] = 1
        else:
            solution_clean = solution.strip().upper()
            
            if solution_clean == FAILURE_NULL:
                response_content["status"] = 1
                
            elif solution_clean == FAILURE_UNSOLVABLE:
                response_content.update({
                    "status": 2, 
                    "message": "I am unable to understand the math question or provide a solution."
                })
                
            else:
                response_content.update({
                    "status": 0,
                    "solution": solution.strip()
                })

        # Add input metadata regardless of status
        response_content["input"] = {
            "provided_image": bool(img),
            "provided_prompt": bool(user_prompt and str(user_prompt).strip() != "")
        }
        if file is not None:
            response_content["input"]["image_filename"] = file.name
        if user_prompt is not None:
            response_content["user_prompt"] = str(user_prompt).strip()
            
        return JsonResponse(response_content)

    except Exception as e:
        logger.error(f"Error in solve_image_with_prompt: {str(e)}")
        # System-level error defaults to status 1
        return JsonResponse({"status": 1, "detail": str(e)})








@csrf_exempt
@api_view(['POST'])
@parser_classes([JSONParser, MultiPartParser])
def solve_image_url(request):
    url = request.data.get('url')
    if not url or not str(url).strip():
        return JsonResponse({"detail": "Field 'url' is required."}, status=400)

    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()

        # Check if the URL actually points to an image
        content_type = r.headers.get("Content-Type", "")
        if not content_type.startswith("image/"):
            return JsonResponse({"detail": "URL does not point to a valid image."}, status=400)

        # Open image safely
        try:
            image = Image.open(io.BytesIO(r.content)).convert("RGB")
        except UnidentifiedImageError:
            return JsonResponse({"detail": "Cannot identify image file from the URL."}, status=400)

        # Prepare prompt for math solver
        prompt = """
        Extract and solve the math problem from this image. Provide a clear, step-by-step solution in natural language.
        Use LaTeX formatting for mathematical expressions (enclose in $ for inline and $$ for display equations).
        Avoid markdown formatting except for LaTeX.

        Format your response with clear steps and a final answer.
        """

        # Call your existing function to process the math problem
        solution = process_math_problem(prompt, image)
        return JsonResponse({"solution": solution})

    except requests.exceptions.RequestException as e:
        return JsonResponse({"detail": f"Error fetching image from URL: {str(e)}"}, status=400)
    except Exception as e:
        return JsonResponse({"detail": f"Error processing image URL: {str(e)}"}, status=500)

@csrf_exempt
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def check_solution(request):
    problem_text = request.data.get('problem_text')
    solution_text = request.data.get('solution_text')
    problem_file = request.FILES.get('problem_file')
    solution_file = request.FILES.get('solution_file')

    if (not problem_text or not str(problem_text).strip()) and problem_file is None:
        return JsonResponse({"detail": "Provide the problem as text, an image, or both."}, status=400)
    if (not solution_text or not str(solution_text).strip()) and solution_file is None:
        return JsonResponse({"detail": "Provide the solution as text, an image, or both."}, status=400)

    if problem_file is not None and not problem_file.content_type.startswith('image/'):
        return JsonResponse({"detail": "Problem file must be an image."}, status=400)
    if solution_file is not None and not solution_file.content_type.startswith('image/'):
        return JsonResponse({"detail": "Solution file must be an image."}, status=400)

    try:
        problem_img = None
        if problem_file is not None:
            problem_bytes = problem_file.read()
            try:
                problem_img = Image.open(io.BytesIO(problem_bytes)).convert("RGB")
                problem_img.load()
            except Exception:
                return JsonResponse({"detail": "Could not open problem image. Ensure it's a valid image file."}, status=400)

        solution_img = None
        if solution_file is not None:
            solution_bytes = solution_file.read()
            try:
                solution_img = Image.open(io.BytesIO(solution_bytes)).convert("RGB")
                solution_img.load()
            except Exception:
                return JsonResponse({"detail": "Could not open solution image. Ensure it's a valid image file."}, status=400)

        # 1) Canonical correct solution (final answer only)
        problem_prompt = "Solve the following math problem. Provide only the final answer in its simplest form.\nUse LaTeX formatting if appropriate. Do not include any explanations or steps.\n\n"
        if problem_text and str(problem_text).strip():
            problem_prompt += f"Problem (text): {str(problem_text).strip()}\n\n"
        problem_prompt += "Final answer only:"

        if problem_img is not None:
            correct_solution = process_math_problem(problem_prompt, problem_img)
        else:
            correct_solution = process_math_problem(problem_prompt)
        correct_solution = (correct_solution or "").strip()

        # 2) Compare user's provided solution with canonical answer
        check_prompt_base = f"""
Extract the final answer from the provided solution (either text or image). Then compare it with the correct answer: {correct_solution}

Return ONLY a single word: CORRECT (if the answers match, considering equivalent formats like fractions vs decimals) or INCORRECT (if they don't match).
If you cannot determine, return INCORRECT.
Do not include any explanations.
"""
        if solution_text and str(solution_text).strip():
            check_prompt_base = f"Solution (text): {str(solution_text).strip()}\n\n" + check_prompt_base

        if solution_img is not None:
            raw_result = process_math_problem(check_prompt_base, solution_img)
        else:
            raw_result = process_math_problem(check_prompt_base)
        raw_result = (raw_result or "").strip()

        m = re.search(r'\b(CORRECT|INCORRECT)\b', raw_result, re.IGNORECASE)
        if m:
            verdict = m.group(1).upper()
            comparison = 0 if verdict == "CORRECT" else 1
        else:
            comparison = 1

        # 3) Extract final answer from user's solution
        extract_prompt = """
Extract the final answer from the provided solution. Return only the answer (use LaTeX if appropriate).
If you cannot determine the final answer, return "UNCLEAR".
"""
        if solution_text and str(solution_text).strip():
            extract_prompt = f"Solution (text): {str(solution_text).strip()}\n\n" + extract_prompt

        if solution_img is not None:
            extracted_raw = process_math_problem(extract_prompt, solution_img)
        else:
            extracted_raw = process_math_problem(extract_prompt)

        extracted_solution = (extracted_raw or "").strip()

        return JsonResponse({
            "comparison": comparison,
            "correct_solution": correct_solution,
            "extracted_solution": extracted_solution,
            "raw_result": raw_result,
            "inputs": {
                "problem_text_provided": bool(problem_text and str(problem_text).strip()),
                "problem_image_provided": bool(problem_file),
                "solution_text_provided": bool(solution_text and str(solution_text).strip()),
                "solution_image_provided": bool(solution_file)
            }
        })
    except Exception as e:
        return JsonResponse({"detail": str(e)}, status=500)

@csrf_exempt
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def classify_message(request):
    message = request.data.get('message')
    if not message or not str(message).strip():
        return JsonResponse({"detail": "Field 'message' is required."}, status=400)

    classification_prompt = f"""
Analyze the following message and classify it. Return only a single digit (0 or 1) with no additional text.

Return 1 if the message contains any of the following:
- Bullying or harassment
- Slang or inappropriate language
- Dangerous links (malware, viruses, etc.)
- Phishing attempts
- Any other harmful content

Return 0 if the message is normal, safe conversation.

Message: {message}

Classification:
"""
    try:
        response = classification_model.generate_content(classification_prompt)
        raw = extract_text_from_genai_response(response).strip()

        m = re.search(r'(?<!\d)([01])(?!\d)', raw)
        if m:
            classification = int(m.group(1))
            return JsonResponse({"message": message, "classification": classification})

        raw_lower = raw.lower()
        if "one" in raw_lower and "zero" not in raw_lower:
            return JsonResponse({"message": message, "classification": 1})
        if "zero" in raw_lower and "one" not in raw_lower:
            return JsonResponse({"message": message, "classification": 0})

        return JsonResponse({"message": message, "classification": 0})
    except Exception as e:
        return JsonResponse({"detail": f"Error classifying message: {str(e)}"}, status=500)

MAX_QUESTIONS = 20

@csrf_exempt
@api_view(['POST'])
@parser_classes([FormParser, MultiPartParser])
def generate_math_question(request):
    grade = request.data.get('grade')
    subject = request.data.get('subject')
    count = request.data.get('count', 1)

    if not grade or not subject:
        return JsonResponse({"detail": "Fields 'grade' and 'subject' are required."}, status=400)

    try:
        try:
            count = int(count)
        except Exception:
            count = 1
        if count < 1:
            count = 1
        if count > MAX_QUESTIONS:
            count = MAX_QUESTIONS

        from .utils import text_model

        json_prompt = f"""
You are a math teacher. Generate {count} unique math questions for a student in grade {grade}
on the topic of {subject}. Each question should be age-appropriate, clear, and solvable.

Return **only** valid JSON. The JSON must be an array of objects with exactly these keys:
[
  {{
    "question": "question text here",
    "answer": "answer text here"
  }},
  ...
]

Do NOT include any additional text outside the JSON array. Make sure there are exactly {count} objects.
"""
        response = text_model.generate_content(json_prompt)
        text = getattr(response, "text", "").strip() or str(response)

        questions = []

        m = re.search(r'(\[.*\])', text, re.DOTALL)
        if m:
            try:
                arr = json.loads(m.group(1))
                for item in arr:
                    q = item.get("question") if isinstance(item, dict) else None
                    a = item.get("answer") if isinstance(item, dict) else None
                    if q and a:
                        questions.append({"question": q.strip(), "answer": a.strip()})
            except Exception:
                pass

        if len(questions) < count:
            qa_pairs = re.findall(
                r"(?:Question\s*\d*[:：]\s*)(.*?)(?:\r?\n\s*Answer\s*\d*[:：]\s*)(.*?)(?=(?:\r?\n\s*Question\s*\d*[:：])|$)",
                text,
                re.DOTALL | re.IGNORECASE
            )
            for q, a in qa_pairs:
                if len(questions) >= count:
                    break
                questions.append({"question": q.strip(), "answer": a.strip()})

        attempt = 0
        while len(questions) < count and attempt < (count * 2):
            attempt += 1
            single_prompt = f"""
Generate 1 unique math question for grade {grade} on the topic {subject}.
Return as:
Question: ...
Answer: ...
Do not repeat previous questions.
"""
            resp = text_model.generate_content(single_prompt)
            text_single = getattr(resp, "text", "").strip() or str(resp)
            m2 = re.search(r"Question\s*\d*[:：]\s*(.*?)(?:\r?\n\s*Answer\s*\d*[:：]\s*(.*))?$",
                           text_single, re.DOTALL | re.IGNORECASE)
            if m2:
                q = (m2.group(1) or "").strip()
                a = (m2.group(2) or "").strip()
                if q and a and not any(q == e["question"] for e in questions):
                    questions.append({"question": q, "answer": a})
                    continue
            lines = [ln.strip() for ln in text_single.splitlines() if ln.strip()]
            if len(lines) >= 2:
                q = lines[0]
                a = lines[1]
                if not any(q == e["question"] for e in questions):
                    questions.append({"question": q, "answer": a})

        while len(questions) < count:
            questions.append({"question": "Unable to generate question — please retry.", "answer": ""})

        result = []
        for i in range(count):
            qitem = questions[i]
            result.append({
                "number": i + 1,
                "question": qitem["question"],
                "answer": qitem["answer"]
            })

        return JsonResponse({
            "grade": grade,
            "subject": subject,
            "count": count,
            "questions": result
        })
    except Exception as e:
        return JsonResponse({"detail": f"Error generating questions: {str(e)}"}, status=500)

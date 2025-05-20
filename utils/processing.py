# # utils/processing.py

# import random

# def get_transition_from_gpt(para_a, para_b, examples, client, model="gpt-4", previous_transitions=None):
#     """
#     Generate a context-aware French transition (EXACTLY 5 words)
#     using few-shot prompting from the examples list and OpenAI GPT.
#     """
#     # Initialize empty list for previous transitions if none provided
#     if previous_transitions is None:
#         previous_transitions = []
    
#     # Use only 5-word examples for few-shot learning
#     five_word_examples = []
#     for ex in examples:
#         if len(ex["transition"].split()) == 5:
#             five_word_examples.append(ex)
    
#     selected_examples = []
#     if len(five_word_examples) >= 3:
#         # Prefer using 5-word examples
#         selected_examples = random.sample(five_word_examples, 3)
#     else:
#         # Fallback to original examples
#         selected_examples = random.sample(examples, min(3, len(examples)))

#     system_prompt = (
#         "Tu es un assistant de presse francophone spécialisé dans la création de transitions. "
#         "Ta tâche est de produire UNE TRANSITION DE 5 MOTS EXACTEMENT entre deux paragraphes.\n\n"
        
#         "🔴 RÈGLE PRINCIPALE ET ABSOLUE 🔴\n"
#         "• LA TRANSITION DOIT CONTENIR EXACTEMENT 5 MOTS (NI PLUS, NI MOINS)\n\n"
        
#         "EXEMPLES DE TRANSITIONS CORRECTES À 5 MOTS :\n"
#         "• 'Passons maintenant au point suivant'\n"
#         "• 'Cette situation mérite notre attention'\n"
#         "• 'À présent, examinons autre chose'\n"
#         "• 'Ces développements changent la donne'\n"
#         "• 'Dans ce contexte, précisons que'\n\n"
        
#         "RÈGLES SECONDAIRES :\n"
#         "• Éviter les répétitions de mots\n"
#         "• Ne jamais réutiliser une transition précédente\n"
#         "• Éviter d'utiliser toujours 'Par ailleurs' ou 'En parallèle'\n\n"
        
#         "INSTRUCTIONS POUR LA DERNIÈRE TRANSITION :\n"
#         "Pour la dernière transition uniquement, utiliser une formule conclusive en 5 mots exactement.\n\n"
        
#         "🔢 COMPTE TES MOTS AVANT DE RÉPONDRE\n"
#         "TA RÉPONSE DOIT ÊTRE UNE PHRASE DE 5 MOTS, RIEN D'AUTRE."
#     )

#     # Add information about previously used transitions
#     if previous_transitions:
#         system_prompt += f"\n\nTRANSITIONS DÉJÀ UTILISÉES (À NE PAS RÉPÉTER) :\n"
#         for i, t in enumerate(previous_transitions, 1):
#             system_prompt += f"{i}. '{t}'\n"

#     # Prepare messages for OpenAI chat completion
#     messages = [{"role": "system", "content": system_prompt}]
    
#     # Add few-shot examples
#     for ex in selected_examples:
#         messages.append({"role": "user", "content": ex["input"]})
#         messages.append({"role": "assistant", "content": ex["transition"]})

#     # Add final instruction that emphasizes 5 words
#     messages.append({
#         "role": "user", 
#         "content": f"{para_a.strip()}\nTRANSITION\n{para_b.strip()}\n\n" +
#                    "Ta réponse doit être UNE transition de EXACTEMENT 5 MOTS."
#     })

#     # Generate transitions until we get a valid one
#     max_attempts = 3
#     for attempt in range(max_attempts):
#         # Generate with OpenAI client
#         response = client.chat.completions.create(
#             model=model,
#             messages=messages,
#             temperature=0.7 - (0.2 * attempt),  # Lower temperature with each retry
#             max_tokens=20
#         )

#         transition = response.choices[0].message.content.strip()
        
#         # Clean up the transition
#         transition = transition.strip('.,;:"\'!?()-')
        
#         # Check word count
#         words = transition.split()
#         word_count = len(words)
        
#         # If exactly 5 words, return it
#         if word_count == 5:
#             return transition
        
#         # If too long, just trim and return
#         if word_count > 5:
#             return " ".join(words[:5])
        
#         # If too short and this is our last attempt, add generic words
#         if attempt == max_attempts - 1 and word_count < 5:
#             if word_count == 4:
#                 return transition + " notamment"
#             elif word_count == 3:
#                 return transition + " bien entendu"
#             else:
#                 # Fallback transitions
#                 fallbacks = [
#                     "Passons maintenant au suivant",
#                     "Examinons maintenant ce point",
#                     "Considérons aussi cet aspect",
#                     "Cette situation mérite attention",
#                     "Notons également ce fait"
#                 ]
#                 return fallbacks[attempt % len(fallbacks)]
    
#     # If all attempts failed, return a safe fallback
#     is_final = para_b.strip().endswith((".", "!", "?")) and not any(next_para.strip() for next_para in para_b.split("\n") if next_para.strip())
    
#     if is_final:
#         return "Pour conclure cette analyse"
#     else:
#         return "Passons maintenant au suivant"






# utils/processing.py

import random
import requests  # Added for API requests

def get_transition_from_gpt(para_a, para_b, examples, client, headers=None, model="gpt-4", previous_transitions=None):
    """
    Generate a context-aware French transition (EXACTLY 5 words)
    using few-shot prompting from the examples list and API.
    Note: 'client' parameter is now expected to be an API URL
    """
    # Initialize empty list for previous transitions if none provided
    if previous_transitions is None:
        previous_transitions = []
    
    # Use default headers if none provided
    if headers is None:
        headers = {"Content-Type": "application/json"}
    
    # Use only 5-word examples for few-shot learning
    five_word_examples = []
    for ex in examples:
        if len(ex["transition"].split()) == 5:
            five_word_examples.append(ex)
    
    selected_examples = []
    if len(five_word_examples) >= 3:
        # Prefer using 5-word examples
        selected_examples = random.sample(five_word_examples, 3)
    else:
        # Fallback to original examples
        selected_examples = random.sample(examples, min(3, len(examples)))

    # Build the prompt for the API
    prompt = (
        "Tu es un assistant de presse francophone spécialisé dans la création de transitions. "
        "Ta tâche est de produire UNE TRANSITION DE 5 MOTS EXACTEMENT entre deux paragraphes.\n\n"
        
        "🔴 RÈGLE PRINCIPALE ET ABSOLUE 🔴\n"
        "• LA TRANSITION DOIT CONTENIR EXACTEMENT 5 MOTS (NI PLUS, NI MOINS)\n\n"
        
        "EXEMPLES DE TRANSITIONS CORRECTES À 5 MOTS :\n"
        "• 'Passons maintenant au point suivant'\n"
        "• 'Cette situation mérite notre attention'\n"
        "• 'À présent, examinons autre chose'\n"
        "• 'Ces développements changent la donne'\n"
        "• 'Dans ce contexte, précisons que'\n\n"
        
        "RÈGLES SECONDAIRES :\n"
        "• Éviter les répétitions de mots\n"
        "• Ne jamais réutiliser une transition précédente\n"
        "• Éviter d'utiliser toujours 'Par ailleurs' ou 'En parallèle'\n\n"
        
        "INSTRUCTIONS POUR LA DERNIÈRE TRANSITION :\n"
        "Pour la dernière transition uniquement, utiliser une formule conclusive en 5 mots exactement.\n\n"
        
        "🔢 COMPTE TES MOTS AVANT DE RÉPONDRE\n"
        "TA RÉPONSE DOIT ÊTRE UNE PHRASE DE 5 MOTS, RIEN D'AUTRE."
    )

    # Add information about previously used transitions
    if previous_transitions:
        prompt += f"\n\nTRANSITIONS DÉJÀ UTILISÉES (À NE PAS RÉPÉTER) :\n"
        for i, t in enumerate(previous_transitions, 1):
            prompt += f"{i}. '{t}'\n"

    # Add few-shot examples
    if selected_examples:
        prompt += "\n\nEXEMPLES :\n"
        for ex in selected_examples:
            prompt += f"Contexte : {ex['input']}\nTransition : {ex['transition']}\n\n"

    # Add the paragraphs
    prompt += f"\nParagraphe A :\n{para_a.strip()}\n\nParagraphe B :\n{para_b.strip()}\n\n"
    prompt += "Ta réponse doit être UNE transition de EXACTEMENT 5 MOTS."
    
    # Generate transitions until we get a valid one
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            # Call the API
            response = requests.post(
                client,  # Now this is expected to be the API URL
                json={"prompt": prompt},
                headers=headers,
                timeout=10  # Add timeout to prevent hanging
            )
            
            # Check status code before proceeding
            if response.status_code != 200:
                print(f"API error on attempt {attempt+1}: Status code {response.status_code}")
                if attempt == max_attempts - 1:
                    # Use fallback if this is the last attempt
                    break
                continue
                
            # Extract transition from response
            try:
                result = response.json()
                transition = result.get("response", "").strip()
            except (ValueError, KeyError):
                print(f"Invalid response format on attempt {attempt+1}")
                if attempt == max_attempts - 1:
                    break
                continue
            
            # Clean up the transition
            transition = transition.strip('.,;:"\'!?()-')
            
            # Check word count
            words = transition.split()
            word_count = len(words)
            
            # If exactly 5 words, return it
            if word_count == 5:
                return transition
            
            # If too long, just trim and return
            if word_count > 5:
                return " ".join(words[:5])
            
            # If too short and this is our last attempt, add generic words
            if attempt == max_attempts - 1 and word_count < 5:
                if word_count == 4:
                    return transition + " notamment"
                elif word_count == 3:
                    return transition + " bien entendu"
                else:
                    # Fallback transitions - made sure each has exactly 5 words
                    fallbacks = [
                        "Passons maintenant au point suivant",
                        "Examinons maintenant ce point important",
                        "Considérons aussi cet aspect essentiel",
                        "Cette situation mérite notre attention",
                        "Notons également ce fait important"
                    ]
                    return fallbacks[attempt % len(fallbacks)]
        
        except requests.exceptions.ConnectionError:
            print(f"Connection error on attempt {attempt+1}")
            if attempt == max_attempts - 1:
                break
        except requests.exceptions.Timeout:
            print(f"Timeout error on attempt {attempt+1}")
            if attempt == max_attempts - 1:
                break
        except Exception as e:
            # Handle API errors, log and continue to fallback
            print(f"API error on attempt {attempt+1}: {str(e)}")
            if attempt == max_attempts - 1:
                break
            # Adjust prompt if needed for next attempt
            prompt += "\n\nTrès important: Ta réponse doit être EXACTEMENT 5 mots."
    
    # If all attempts failed, return a safe fallback
    is_final = para_b.strip().endswith((".", "!", "?")) and not any(next_para.strip() for next_para in para_b.split("\n") if next_para.strip())
    
    if is_final:
        return "Pour conclure cette analyse importante"  # Fixed to 5 words
    else:
        return "Passons maintenant au point suivant"  # Fixed to 5 words
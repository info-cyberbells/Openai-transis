# # utils/title_blurb.py

# import openai

# PROMPT = """Tu es un assistant de rédaction pour un journal local français.

# Ta tâche est de générer un **titre** et un **chapeau** (blurb) à partir du **premier paragraphe uniquement**.

# Règles :

# 1. Titre :
#    - Court, clair et journalistique (max. 12 mots).
#    - Inclure le lieu si mentionné dans le paragraphe.
#    - Inclure la date si mentionnée dans le paragraphe.
#    - Doit annoncer le fait principal.

# 2. Chapeau :
#    - Résume quoi, qui, où, quand.
#    - Mentionner la date et le lieu s’ils sont dans le paragraphe.
#    - Max. 30 mots, ton neutre.

# Utilise uniquement le contenu du paragraphe fourni, sans rien ajouter.

# Format de réponse :
# Titre : [titre généré]
# Chapeau : [chapeau généré]
# """

# def generate_title_and_blurb(paragraph, client):
#     response = client.chat.completions.create(
#         model="gpt-4",
#         messages=[
#             {"role": "system", "content": PROMPT},
#             {"role": "user", "content": paragraph.strip()}
#         ],
#         temperature=0.5,
#         max_tokens=100
#     )
#     return response.choices[0].message.content.strip()







# utils/title_blurb.py

import requests  # Added for API requests

PROMPT = """Tu es un assistant de rédaction pour un journal local français.

Ta tâche est de générer un **titre** et un **chapeau** (blurb) à partir du **premier paragraphe uniquement**.

Règles :

1. Titre :
   - Court, clair et journalistique (max. 12 mots).
   - Inclure le lieu si mentionné dans le paragraphe.
   - Inclure la date si mentionnée dans le paragraphe.
   - Doit annoncer le fait principal.

2. Chapeau :
   - Résume quoi, qui, où, quand.
   - Mentionner la date et le lieu s'ils sont dans le paragraphe.
   - Max. 30 mots, ton neutre.

Utilise uniquement le contenu du paragraphe fourni, sans rien ajouter.

Format de réponse :
Titre : [titre généré]
Chapeau : [chapeau généré]
"""

def generate_title_and_blurb(paragraph, client, headers=None):
    """
    Generate a title and blurb for the given paragraph using the API.
    
    Args:
        paragraph (str): The paragraph to generate a title and blurb for.
        client (str): The API URL to use.
        headers (dict, optional): Headers for the API request, including auth.
    
    Returns:
        str: The generated title and blurb.
    """
    # Use default headers if none provided
    if headers is None:
        headers = {"Content-Type": "application/json"}
    try:
        # Create the full prompt for the API
        full_prompt = f"{PROMPT}\n\nParagraphe:\n{paragraph.strip()}"
        
        # Call the API
        response = requests.post(
            client,
            json={"prompt": full_prompt},
            headers=headers,
            timeout=10  # Add a timeout to prevent hanging
        )
        
        # Check status code before proceeding
        if response.status_code != 200:
            return f"Titre : Erreur API (code {response.status_code})\nChapeau : L'API a retourné une erreur. Vérifiez l'URL et que le service est en cours d'exécution."
            
        # Extract and return the response
        result = response.json()
        if "response" not in result:
            return f"Titre : Format de réponse incorrect\nChapeau : La réponse de l'API ne contient pas le champ 'response' attendu."
            
        return result["response"].strip()
    except requests.exceptions.ConnectionError:
        return f"Titre : Erreur de connexion\nChapeau : Impossible de se connecter à l'API. Vérifiez l'URL et que le service est en cours d'exécution."
    except requests.exceptions.Timeout:
        return f"Titre : Délai d'attente dépassé\nChapeau : L'API n'a pas répondu dans le délai imparti. Le service peut être surchargé."
    except requests.exceptions.JSONDecodeError:
        return f"Titre : Erreur de format JSON\nChapeau : La réponse de l'API n'est pas un JSON valide."
    except Exception as e:
        return f"Titre : Erreur technique\nChapeau : {str(e)}"
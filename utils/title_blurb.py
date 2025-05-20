# utils/title_blurb.py

import requests
import json
import streamlit as st

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
        
        # Prepare the payload
        payload = {"prompt": full_prompt}
        
        # Add debugging in Streamlit
        with st.expander("API Debug Info (Expand to see details)", expanded=False):
            st.write("**API URL:**", client)
            st.write("**Headers:**", {k: "..." if k == "Authorization" else v for k, v in headers.items()})
            st.write("**Payload:**", payload)
        
        # Call the API
        response = requests.post(
            client,
            json=payload,
            headers=headers,
            timeout=35  # Increased timeout
        )
        
        # Debug the response
        with st.expander("API Response (Expand to see details)", expanded=False):
            st.write("**Status Code:**", response.status_code)
            try:
                st.write("**Response Content:**", response.json())
            except:
                st.write("**Raw Response:**", response.text)
        
        # Check status code before proceeding
        if response.status_code != 200:
            return f"Titre : Erreur API (code {response.status_code})\nChapeau : L'API a retourné une erreur. Vérifiez l'URL et que le service est en cours d'exécution."
        
        # Try to parse the response as JSON
        try:
            result = response.json()
        except json.JSONDecodeError:
            # If response isn't JSON, try to use the raw text if it looks like our format
            if "Titre :" in response.text and "Chapeau :" in response.text:
                return response.text
            return f"Titre : Format de réponse incorrect\nChapeau : La réponse de l'API n'est pas un JSON valide."
        
        # Handle different response formats
        if "response" in result:
            return result["response"].strip()
        elif "choices" in result and len(result["choices"]) > 0:
            # Handle OpenAI-like format
            return result["choices"][0]["message"]["content"].strip()
        elif "generations" in result and len(result["generations"]) > 0:
            # Handle Anthropic-like format
            return result["generations"][0]["text"].strip()
        elif "output" in result:
            # Handle generic output field
            return result["output"].strip()
        elif isinstance(result, str):
            # Handle if the response itself is a string
            return result.strip()
        else:
            # If we can't find a known field, dump the entire response as debug
            return f"Titre : Format de réponse incorrect\nChapeau : La réponse de l'API a un format inconnu. Contenu : {str(result)[:100]}..."
            
    except requests.exceptions.ConnectionError:
        return f"Titre : Erreur de connexion\nChapeau : Impossible de se connecter à l'API. Vérifiez l'URL et que le service est en cours d'exécution."
    except requests.exceptions.Timeout:
        return f"Titre : Délai d'attente dépassé\nChapeau : L'API n'a pas répondu dans le délai imparti. Le service peut être surchargé."
    except Exception as e:
        return f"Titre : Erreur technique\nChapeau : {str(e)}"

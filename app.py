import streamlit as st
import requests  # Changed from OpenAI import
import random
import os
from dotenv import load_dotenv
from utils.io import load_examples
from utils.processing import get_transition_from_gpt
from utils.layout import rebuild_article_with_transitions
from utils.display import layout_title_and_input, show_output, show_version
from utils.version import compute_version_hash
from utils.title_blurb import generate_title_and_blurb


def main():
    # First check if running on Streamlit Cloud (use st.secrets)
    if 'API_URL' in st.secrets:
        api_url = st.secrets["API_URL"]
        api_token = st.secrets["API_TOKEN"]
    else:
        
    
    # Create headers with authentication
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_token}"
    }
    
    # Validate that API credentials are available
    if not api_url or not api_token:
        st.error("⚠️ API credentials not found. Please check your environment variables.")
        st.info("Create a .env file with API_URL and API_TOKEN variables.")
        return


    # ✅ Compute version hash for debug and traceability
    VERSION = compute_version_hash([
        "app.py",
        "transitions.json",
        "utils/io.py",
        "utils/processing.py",
        "utils/layout.py",
        "utils/display.py",
        "utils/version.py",
        "utils/title_blurb.py"
    ])

    # ✅ Display input UI
    text_input = layout_title_and_input()

    if st.button("✨ Générer les transitions"):
        if "TRANSITION" not in text_input:
            st.warning("Aucune balise `TRANSITION` trouvée.")
            return

        # ✅ Load few-shot examples
        examples = load_examples()

        # ✅ Split input into paragraphs and transition pairs
        parts = text_input.split("TRANSITION")
        pairs = list(zip(parts[:-1], parts[1:]))

        # ✅ Generate title and blurb from the first paragraph
        title_blurb = generate_title_and_blurb(parts[0], api_url, headers)

        # ✅ Generate transitions for each paragraph pair
        generated_transitions = []
        for para_a, para_b in pairs:
            transition = get_transition_from_gpt(para_a, para_b, examples, api_url, headers=headers, previous_transitions=generated_transitions)
            generated_transitions.append(transition)

        # ✅ VALIDATION: Check for duplicate transitions
        transition_count = {}
        for t in generated_transitions:
            transition_count[t] = transition_count.get(t, 0) + 1

        # Check for duplicates
        duplicates = [t for t, count in transition_count.items() if count > 1]
        if duplicates:
            st.warning(f"🚨 Transitions répétées détectées: {', '.join(duplicates)}")
            
            # Fix duplicates by adding a variation marker
            for i in range(1, len(generated_transitions)):
                if generated_transitions[i] in generated_transitions[:i]:
                    # Add a variation to make it unique - all guaranteed to be 5 words
                    variations = [
                        "À noter également ce fait", 
                        "Il faut aussi mentionner ceci", 
                        "Soulignons encore ce point important", 
                        "Précisons ce point très important", 
                        "Ajoutons cette information très essentielle"
                    ]
                    generated_transitions[i] = variations[i % len(variations)]

        # ✅ VALIDATION: Verify each transition has exactly 5 words
        invalid_word_count = []
        for i, t in enumerate(generated_transitions):
            words = t.split()
            word_count = len(words)
            
            if word_count != 5:
                # Store the original for reporting
                invalid_word_count.append(f"Transition {i+1} ({word_count} mots): '{t}'")
                
                # Automatic correction based on word count
                if word_count > 5:
                    # If too long, trim to 5 words
                    generated_transitions[i] = " ".join(words[:5])
                    st.info(f"Transition {i+1} raccourcie à 5 mots: '{generated_transitions[i]}'")
                elif word_count < 5:
                    # If too short, add generic words to reach 5
                    if word_count == 4:
                        # Add one word based on context
                        if i == len(generated_transitions) - 1:  # Last transition
                            generated_transitions[i] = t + " maintenant"
                        else:
                            generated_transitions[i] = t + " notamment"
                    elif word_count == 3:
                        # Add two words
                        generated_transitions[i] = t + " comme on sait"
                    else:
                        # Fallback for very short transitions - ensured exactly 5 words
                        fillers = ["Comme on peut le constater", 
                                "Il faut bien le dire",
                                "À ce stade, précisons que",
                                "Dans ce contexte particulier",
                                "Pour bien comprendre ceci"
                        ]
                        generated_transitions[i] = random.choice(fillers)
                    
                    st.info(f"Transition {i+1} complétée à 5 mots: '{generated_transitions[i]}'")

        if invalid_word_count:
            st.warning(f"🚨 Transitions qui ne respectaient pas la règle de 5 mots: {', '.join(invalid_word_count)}")

        # ✅ Final validation check after corrections
        for i, t in enumerate(generated_transitions):
            word_count = len(t.split())
            if word_count != 5:
                st.error(f"⛔ ERREUR: La transition {i+1} a toujours {word_count} mots après correction")
                # Last resort fix - ensure exactly 5 words
                generated_transitions[i] = "Passons maintenant au point suivant"

        # ✅ Rebuild the final article with transitions inserted
        rebuilt_text, error = rebuild_article_with_transitions(text_input, generated_transitions)
        if error:
            st.error(error)
        else:
            # ✅ Nicely render Titre and Chapeau with required spacing
            if "Titre :" in title_blurb and "Chapeau :" in title_blurb:
                lines = title_blurb.split("\n")
                title_line = next((l for l in lines if l.startswith("Titre :")), "")
                chapo_line = next((l for l in lines if l.startswith("Chapeau :")), "")

                st.markdown("### 📰 Titre")
                st.markdown(f"**{title_line.replace('Titre :', '').strip()}**")

                # 3 blank lines between title and chapeau
                st.markdown("&nbsp;\n&nbsp;\n&nbsp;", unsafe_allow_html=True)

                st.markdown("### ✏️ Chapeau")
                st.markdown(chapo_line.replace("Chapeau :", "").strip())

                # 6 blank lines after the title/chapeau block
                st.markdown("&nbsp;\n&nbsp;\n&nbsp;\n&nbsp;\n&nbsp;\n&nbsp;", unsafe_allow_html=True)
            else:
                # Fallback if format is unexpected
                st.markdown("### 📰 Titre et chapeau")
                st.markdown(title_blurb)
                st.markdown("&nbsp;\n&nbsp;\n&nbsp;\n&nbsp;\n&nbsp;\n&nbsp;", unsafe_allow_html=True)

            # ✅ Display full output article with transitions
            st.markdown("### 🧾 Article reconstruit")
            show_output(rebuilt_text)

            # ✅ Display generated transitions list
            st.markdown("### 🧩 Transitions générées")
            for i, t in enumerate(generated_transitions, 1):
                st.markdown(f"{i}. _{t}_")

    # ✅ Always show version
    show_version(VERSION)

if __name__ == "__main__":
    main()

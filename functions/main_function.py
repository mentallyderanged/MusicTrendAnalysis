import re
from collections import defaultdict
from typing import Dict, List
#from pysentimiento import create_analyzer # Removed pysentimiento import
from transformers import pipeline

import os
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

def chunk_lyrics_to_sentences(lyrics):
    """
    Chunks lyrics into sentences from a SINGLE CONTINUOUS STRING,
    with sentences starting at capitalized words (except 'I') and ending *before* the next.
    """
    lyrics_no_signals = re.sub(r'\[.*?\]', '', lyrics)
    words = lyrics_no_signals.strip().split()

    sentences = []
    current_sentence_words = []
    expecting_start = True

    for word in words:
        if not word:
            continue

        word_capitalized = word and word[0].isupper()
        is_letter_i = word.upper() == 'I' # Check if the word is 'I' (case-insensitive)

        if expecting_start:
            if word_capitalized:
                if current_sentence_words:
                    sentences.append(" ".join(current_sentence_words).strip())
                    current_sentence_words = []
                current_sentence_words.append(word)
                expecting_start = False

        else: # Expecting words within sentence
            if word_capitalized and not is_letter_i: # Capitalized, but NOT 'I' - end sentence before
                sentences.append(" ".join(current_sentence_words).strip())
                current_sentence_words = [word]
                expecting_start = False
            else: # Lowercase word OR Capitalized 'I' - part of current sentence
                current_sentence_words.append(word)

    if current_sentence_words:
        sentences.append(" ".join(current_sentence_words).strip())

    return sentences

def predict_lyric(data):
    """Returns AnalyzerOutput with emotion probabilities"""
    classifier = pipeline(
        "text-classification",
        model="cirimus/modernbert-large-go-emotions",
        return_all_scores=True
    )

    predictions = classifier(data)
    #print(predictions) # Keep print for debugging if needed

    # Transform predictions to the format expected by analyze_song_emotion (.probas)
    probas_dict = {}
    if predictions and predictions[0]: # Ensure predictions and the first element exist
        for prediction in predictions[0]: # predictions is a list of lists, we take the first list
            label = prediction['label']
            score = prediction['score']
            probas_dict[label] = score
    return probas_dict # Return the transformed dictionary


def analyze_song_emotion(lyrics: str) -> Dict:
    """
    Calculates average emotion probabilities for the entire song and prints dominant emotion per sentence.
    Returns:
        ... (rest of analyze_song_emotion function remains the same) ...
    """
    sentences = chunk_lyrics_to_sentences(lyrics)

    total_probas = defaultdict(float)
    emotion_counts = defaultdict(int)

    for sentence in sentences:
        if not sentence.strip():
            continue

        print('sentence----------------------------------------------')
        print(sentence)
        result = predict_lyric(sentence) # Now predict_lyric returns probas_dict

        # Determine dominant emotion for the sentence
        sentence_dominant_emotion = max(result, key=result.get, default="neutral") if result else "neutral"
        print(f"Sentence Dominant Emotion: {sentence_dominant_emotion}") # Print sentence dominant emotion

        for emotion, prob in result.items(): # Iterate through the dictionary directly
            total_probas[emotion] += prob
            emotion_counts[emotion] += prob

    avg_probas = {emotion: total / len(sentences)
                 for emotion, total in total_probas.items()} if sentences else {}

    dominant_emotion = max(avg_probas, key=avg_probas.get, default="neutral") if avg_probas else "neutral"

    return {
        "dominant_emotion": dominant_emotion,
        "average_probas": avg_probas,
        "sentence_count": len(sentences)
    }


lyrics_example_continuous_string = "[Verse 1] We clawed, we chained, our hearts in vain We jumped, never asking why We kissed, I fell under your spell A love no one could deny  [Pre-Chorus] Don't you ever say I just walked away I will always want you I can't live a lie, running for my life I will always want you  [Chorus] I came in like a wrecking ball I never hit so hard in love All I wanted was to break your walls All you ever did was wreck me Yeah, you, you wreck me  [Verse 2] I put you high up in the sky And now, you're not coming down It slowly turned, you let me burn And now, we're ashes on the ground  [Pre-Chorus] Don't you ever say I just walked away I will always want you I can't live a lie, running for my life I will always want you  [Chorus] I came in like a wrecking ball I never hit so hard in love All I wanted was to break your walls All you ever did was wreck me I came in like a wrecking ball Yeah, I just closed my eyes and swung Left me crashing in a blazing fall All you ever did was wreck me Yeah, you, you wreck me  [Bridge] I never meant to start a war I just wanted you to let me in And instead of using force I guess I should've let you win I never meant to start a war I just wanted you to let me in I guess I should've let you win  [Interlude] Don't you ever say I just walked away I will always want you  [Chorus] I came in like a wrecking ball I never hit so hard in love All I wanted was to break your walls All you ever did was wreck me I came in like a wrecking ball Yeah, I just closed my eyes and swung Left me crashing in a blazing fall All you ever did was wreck me Yeah, you, you wreck me Yeah, you, you wreck me  [Produced by Dr. Luke and Cirkut] [Video by Terry Richardson]" # No \n characters
#lyrics_example_continuous_string = "People in the world is really worried because of Coronavirus"
analysis = analyze_song_emotion(lyrics_example_continuous_string)
print(f"Dominant Emotion: {analysis['dominant_emotion']}")
print("Average Probabilities:")
for emotion, prob in analysis["average_probas"].items():
    print(f"{emotion}: {prob:.3f}")
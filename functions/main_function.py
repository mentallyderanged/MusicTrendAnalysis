import re
from collections import defaultdict
from typing import Dict, List
from pysentimiento import create_analyzer

def chunk_lyrics_to_sentences(lyrics):
    """
    Chunks lyrics into sentences based on capitalization, handling consecutive
    capitalized lines and removing bracketed signals.
    """
    lyrics_no_signals = re.sub(r'\[.*?\]', '', lyrics)
    lines = lyrics_no_signals.strip().split('\n')

    sentences = []
    current_sentence = ""
    previous_line_capitalized = False  # Track if the previous line started with a capital

    for line in lines:
        line = line.strip()
        if not line:
            continue

        line_capitalized = line[0].isupper() if line else False # Check if current line starts with capital

        if not current_sentence: # Start of first sentence
            current_sentence += line
        elif line_capitalized: # Current line starts with capital
            sentences.append(current_sentence.strip()) # End previous sentence
            current_sentence = line # Start new sentence with current line
        else: # Current line is lowercase or not capitalized after first word
            current_sentence += " " + line # Append to current sentence

        previous_line_capitalized = line_capitalized # Update for next iteration

    if current_sentence: # Append the last sentence
        sentences.append(current_sentence.strip())

    return sentences

def predict_lyric(data):
    """Returns AnalyzerOutput with emotion probabilities"""
    analyzer = create_analyzer(task="emotion", lang="en")
    #test - keep this for now to see the sentence analysis
    a = analyzer.predict(data)
    print(a)
    return a

def analyze_song_emotion(lyrics: str) -> Dict:
    """
    Calculates average emotion probabilities for the entire song.
    Returns:
        ... (rest of the function is the same) ...
    """
    sentences = chunk_lyrics_to_sentences(lyrics)

    # Initialize aggregation structures (rest is the same) ...

    for sentence in sentences:
        if not sentence.strip():
            continue

        print('sentence----------------------------------------------')
        print(sentence)
        result = predict_lyric(sentence)

        # Aggregate probabilities (rest is the same) ...

    # Calculate averages, dominant emotion, and return (rest is the same) ...
    avg_probas = {emotion: total / len(sentences)
                 for emotion, total in total_probas.items()} if sentences else {}

    dominant_emotion = max(avg_probas, key=avg_probas.get, default="neutral") if avg_probas else "neutral"

    return {
        "dominant_emotion": dominant_emotion,
        "average_probas": avg_probas,
        "sentence_count": len(sentences)
    }


lyrics_example = "[Verse 1] We clawed, we chained, our hearts in vain We jumped, never asking why We kissed, I fell under your spell A love no one could deny  [Pre-Chorus] Don't you ever say I just walked away I will always want you I can't live a lie, running for my life I will always want you  [Chorus] I came in like a wrecking ball I never hit so hard in love All I wanted was to break your walls All you ever did was wreck me Yeah, you, you wreck me  [Verse 2] I put you high up in the sky And now, you're not coming down It slowly turned, you let me burn And now, we're ashes on the ground  [Pre-Chorus] Don't you ever say I just walked away I will always want you I can't live a lie, running for my life I will always want you  [Chorus] I came in like a wrecking ball I never hit so hard in love All I wanted was to break your walls All you ever did was wreck me I came in like a wrecking ball Yeah, I just closed my eyes and swung Left me crashing in a blazing fall All you ever did was wreck me Yeah, you, you wreck me  [Bridge] I never meant to start a war I just wanted you to let me in And instead of using force I guess I should've let you win I never meant to start a war I just wanted you to let me in I guess I should've let you win  [Interlude] Don't you ever say I just walked away I will always want you  [Chorus] I came in like a wrecking ball I never hit so hard in love All I wanted was to break your walls All you ever did was wreck me I came in like a wrecking ball Yeah, I just closed my eyes and swung Left me crashing in a blazing fall All you ever did was wreck me Yeah, you, you wreck me Yeah, you, you wreck me  [Produced by Dr. Luke and Cirkut] [Video by Terry Richardson]"

analysis = analyze_song_emotion(lyrics_example)
print(f"Dominant Emotion: {analysis['dominant_emotion']}")
print("Average Probabilities:")
for emotion, prob in analysis["average_probas"].items():
    print(f"{emotion}: {prob:.3f}")
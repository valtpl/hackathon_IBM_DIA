import sys
import os
import re
import string

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from main import analyze_prompt

# Test prompts
test_cases = [
    "yes",
    "say yes",
    "Hello",
    "Hello how are you?",
    "What is machine learning?",
]

print("=" * 80)
print("FEATURE EXTRACTION VERIFICATION")
print("=" * 80)

for prompt in test_cases:
    print(f"\n{'='*80}")
    print(f"Prompt: \"{prompt}\"")
    print(f"Length: {len(prompt)} chars")
    print(f"{'='*80}")
    
    features = analyze_prompt(prompt)
    
    # Manual verification
    words = prompt.split()
    actual_word_count = len(words)
    actual_char_count = len(prompt)
    actual_letter_count = sum(1 for c in prompt if c.isalpha())
    actual_punctuation = sum(1 for c in prompt if c in string.punctuation)
    
    print(f"\n--- BASIC COUNTS ---")
    print(f"word_count:        {features['word_count']:>6} (expected: {actual_word_count})")
    print(f"char_count:        {features['char_count']:>6} (expected: {actual_char_count})")
    print(f"letter_count:      {features['letter_count']:>6} (expected: {actual_letter_count})")
    print(f"punctuation_count: {features['punctuation_count']:>6} (expected: {actual_punctuation})")
    
    print(f"\n--- WORD ANALYSIS ---")
    print(f"unique_word_count: {features['unique_word_count']:>6}")
    print(f"long_word_count:   {features['long_word_count']:>6} (>6 chars)")
    print(f"verb_count:        {features['verb_count']:>6}")
    print(f"word_diversity:    {features['word_diversity']:>6.4f}")
    print(f"lexical_diversity: {features['lexical_diversity']:>6.4f}")
    
    print(f"\n--- SENTENCE ANALYSIS ---")
    print(f"sentence_count:       {features['sentence_count']:>6}")
    print(f"avg_word_length:      {features['avg_word_length']:>6.2f}")
    print(f"avg_sentence_length:  {features['avg_sentence_length']:>6.2f} (chars per sentence)")
    
    print(f"\n--- SYLLABLE ANALYSIS ---")
    print(f"syllable_count:       {features['syllable_count']:>6}")
    print(f"monosyllabcount:      {features['monosyllabcount']:>6}")
    print(f"polysyllabcount:      {features['polysyllabcount']:>6}")
    
    print(f"\n--- PUNCTUATION MARKS ---")
    print(f"question_marks:       {features['question_marks']:>6}")
    print(f"exclamation_marks:    {features['exclamation_marks']:>6}")
    
    print(f"\n--- DERIVED FEATURES ---")
    print(f"word_count_squared:        {features['word_count_squared']:>10}")
    print(f"avg_sentence_length_cubed: {features['avg_sentence_length_cubed']:>10.2f}")
    print(f"lexicon_count:             {features['lexicon_count']:>10}")
    
    # Check for issues
    issues = []
    if features['word_count'] != actual_word_count:
        issues.append(f"❌ word_count mismatch: {features['word_count']} != {actual_word_count}")
    if features['char_count'] != actual_char_count:
        issues.append(f"❌ char_count mismatch: {features['char_count']} != {actual_char_count}")
    if features['letter_count'] != actual_letter_count:
        issues.append(f"❌ letter_count mismatch: {features['letter_count']} != {actual_letter_count}")
    if features['punctuation_count'] != actual_punctuation:
        issues.append(f"❌ punctuation_count mismatch: {features['punctuation_count']} != {actual_punctuation}")
    
    if issues:
        print(f"\n{'='*80}")
        print("ISSUES FOUND:")
        for issue in issues:
            print(issue)
    else:
        print(f"\n✓ All basic counts verified correctly")

print("\n" + "=" * 80)
print("DETAILED WORD-BY-WORD ANALYSIS FOR 'What is machine learning?'")
print("=" * 80)

prompt = "What is machine learning?"
words = prompt.split()
print(f"\nWords: {words}")
print(f"Total words: {len(words)}")

for i, word in enumerate(words, 1):
    clean_word = word.strip(string.punctuation)
    vowel_clusters = re.findall(r'[aeiou]+', word.lower())
    syllables = max(1, len(vowel_clusters))
    
    print(f"\n{i}. '{word}'")
    print(f"   Clean: '{clean_word}'")
    print(f"   Length: {len(clean_word)} chars")
    print(f"   Vowel clusters: {vowel_clusters}")
    print(f"   Syllable count: {syllables}")
    print(f"   Is long word (>6): {len(clean_word) > 6}")
    print(f"   Monosyllabic: {len(vowel_clusters) == 1}")
    print(f"   Polysyllabic (3+): {len(vowel_clusters) >= 3}")

# Check verb detection
print("\n" + "=" * 80)
print("VERB DETECTION TEST")
print("=" * 80)
verb_patterns = ['ing', 'ed', 'ate', 'ize', 'ise']
test_words = ['running', 'walked', 'create', 'realize', 'organise', 'hello', 'is', 'learning']

for word in test_words:
    is_verb = any(word.lower().endswith(pattern) for pattern in verb_patterns)
    print(f"{word:12} -> {'VERB' if is_verb else 'NOT VERB'}")

from roster.intent_classifier import IntentClassifier

def test_classifier_routes_common_intents():
    classifier=IntentClassifier(); assert classifier.classify("quit").name=="exit"; assert classifier.classify("open calculator").name=="tool"; assert classifier.classify("hello").name=="chat"

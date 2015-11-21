"""
I am version 0.5 of the J.A.R.V.I.S. natural language interface for Slack,
configured to perform a multitude of functions.
"""
outputs = []


def process_message(data):
    if 'where is the blue goose?' in data['text']:
        outputs.append([
            data['channel'],
            """Oh hello, Lara! You are on your final step! The blue goose was a red herring
            But I'll tell you your final clue anyways. You must now travel to the mysterious and far
            away land called the park. There you will go to the sporting venue that shares the
            same name as the thing that definitely isn't your reward and is found in kimberlite."""
        ])

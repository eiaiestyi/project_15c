import random

from airtable import Airtable

import config


class Word:
    def __init__(self, user):
        self.user_name = user
        # Take scores
        print('Collecting scores...')
        self.scores_table = Airtable(config.base_key, 'scores', config.api_key)
        scores = self.scores_table.search('user_name', self.user_name)
        self.scores = {}
        self.existing_scores = {}
        self.scores_total = 0
        for score in scores:
            self.scores[score['fields']['word_id']] = score['fields']
            self.existing_scores[score['fields']['word_id']] = score['fields']
            self.scores_total += score['fields']['score']
        self.scores_mean = self.scores_total / len(self.scores) if len(self.scores) > 0 else 0
        print('Scores collected.')

        # Take words
        print('Collecting words...')
        words_table = Airtable(config.base_key, 'words', config.api_key)
        words = words_table.get_all()
        self.known_words = {}
        self.learn_words = {}
        for word in words:
            word_id = word['fields']['id']
            if word_id in self.scores:
                if self.scores[word_id]['score'] > self.scores_mean:
                    # If score is bigger than mean, add word to known_words
                    self.known_words[word_id] = word['fields']
                else:
                    # If score smaller or equal to mean, add to learn_word
                    self.learn_words[word_id] = word['fields']
            else:
                self.learn_words[word_id] = word['fields']
        print('Words collected.')

    def learn(self):
        """
        Show words in English and write answer in Spanish.
        Calculate correct answers.
        :return:
        """
        print('If you want to end learning, type /END at any time.')
        # Get random word id from learn_words list
        word_id = random.choice(list(self.learn_words))
        word = self.learn_words[word_id]
        # Take answer from input
        answer = input('Enter Spanish word for "{}": '.format(word['english']))
        if answer.upper() == '/END':
            # If /END entered, then show stats and end program
            return self.stats()
        elif answer.lower() == word['spanish'].lower():
            # If answer correct
            print('Correct.')
            score = 1
        else:
            # If answer incorrect
            print('Incorrect. Correct word was:', word['spanish'])
            score = -1
        if word_id in self.scores:
            # If word already in scores, add score to current score
            self.scores[word_id]['score'] += score
            # Update score in table
            self.scores_table.update_by_field('word_id', word_id, {'score': self.scores[word_id]['score']})
        else:
            # If word is not in scores, add new score
            self.scores[word_id] = {'user_name': self.user_name, 'word_id': word_id, 'score': score}
            # Add new score in table
            self.scores_table.insert(self.scores[word_id])
        # Update total score
        self.scores_total += score
        # Update scores mean
        self.scores_mean = self.scores_total / len(self.scores)
        if self.scores[word_id]['score'] > self.scores_mean:
            # If word score is higher than mean, then put it to known_words
            self.known_words[word_id] = self.learn_words.pop(word_id)
        self.learn()

    def stats(self):
        """
        Show words statistics.
        :return:
        """
        # Total
        print('Total score:', self.scores_total)
        # Mean
        print('Mean score:', round(self.scores_mean, 2))
        # Lowest
        lowest = min(self.scores, key=lambda x: self.scores[x]['score'])
        print('Lowest score:', self.scores[lowest]['score'], end=' ')
        if lowest in self.learn_words:
            print('({} - {})'.format(self.learn_words[lowest]['english'], self.learn_words[lowest]['spanish']))
        else:
            print('({} - {})'.format(self.known_words[lowest]['english'], self.known_words[lowest]['spanish']))
        # Highest
        highest = max(self.scores, key=lambda x: self.scores[x]['score'])
        print('Highest score:', self.scores[highest]['score'], end=' ')
        if highest in self.learn_words:
            print('({} - {})'.format(self.learn_words[highest]['english'], self.learn_words[highest]['spanish']))
        else:
            print('({} - {})'.format(self.known_words[highest]['english'], self.known_words[highest]['spanish']))

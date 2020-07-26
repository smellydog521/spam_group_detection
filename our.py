# this is our approach to detect aspect-oriented sentiment
# so as to cluster reviewers into groups
import os
import re

import jieba
import jieba.posseg as jp
import pandas as pd

MIN_LEN = 5
MAX_ASPECT_LEN = 5
# positive = ['非常好', '太棒了']
# neutral = ['一般般', '凑合', '还行']
# negative = ['差', '烂', '没用']

def cut_words(texts):
    # 切词时保留sentiment相关词汇
    # jieba.load_userdict(r'sentiment_strength.txt')
    jieba.load_userdict(r'E://reviewData//Kingston//positive_terms.txt')
    jieba.load_userdict(r'E://reviewData//Kingston//negative_terms.txt')
    flags = ('n', 'nr', 'ns', 'nt', 'eng', 'v', 'd', 'a', 'z')  # 词性
    stopwords = ('\n', '，', ',', '没', '就', '知道', '是', '才', '也', '拿到',
                 '听听', '坦言', '越来越', '评价', '放弃', '人', '好好', '收到', '还')  # 停词

    # with open('stop_words.txt') as fs:
    #     for line in fs:
    #         stopwords.append(line.strip())

    # 分词
    words = [w for w in jp.cut(texts) if w.flag in flags and w.word not in stopwords]
    # words 含flag 和 word
    return words


# to dig any aspects associated with sentiment
# and then filter any related aspects
# for now, extra aspects are not included
def find_aspects_sentiments(review, s_labels):
    words = cut_words(review)

    terms = []
    term_flags = []
    for w in words:
        terms.append(w.word)
        term_flags.append(w.flag)

    aspects = dict()
    flags = ('n', 'nr', 'ns', 'nt')

    aspect_indices = []
    hit_labels = []
    for index, term in enumerate(terms):
        if term_flags[index] in flags:
            for label, alternatives in s_labels.items():
                if term in alternatives:
                    hit_labels.append(label)
                    aspect_indices.append(index)

    # print('aspect_indices', aspect_indices)
    sentiments = dict()
    for index1, aspect1 in enumerate(aspect_indices):
        for index2, aspect2 in enumerate(aspect_indices):
            if index2 - index1 == 1 and aspect2 - aspect1 - len(terms[aspect1]) > 2:
                sentiments[hit_labels[index1]] = terms[aspect1 + 1:aspect2]

    return sentiments


def partial_aspect_case(content):
    pass


def load_corpus(reviews, labels, similar_labels):
    pattern2 = '；确认收货后[\d]+天追加'
    pattern1 = '此用户没有填写评价。'

    corpus = []
    for review in reviews:
        ass = dict()
        if len(review) < MIN_LEN:
            ass[labels[0]] = 0
            corpus.append(ass)
            continue
        else:
            # to check if suggested labels are applied
            _, content = re.split(r'%%%', review)
            content = re.sub(pattern1, '', content)
            content = re.sub(pattern2, '', content)
            if '：' in content and '；' in content:
                terms = re.split(r'；', content)
                ass = dict()
                for aspect_sentiment in terms:
                    if '：' in aspect_sentiment and len(aspect_sentiment) > 2:
                        # print('aspect_sentiment', aspect_sentiment)
                        a_s = re.split(r'：', aspect_sentiment)
                        aspect = a_s[0]
                        if aspect in labels:
                            sentiment = cut_words(a_s[1])
                            senti_words = []
                            for pair in sentiment:
                                senti_words.append(pair.word)
                            ass[aspect] = senti_words
            # to find any words which could be seen as an alternative expression of any individual aspect
            else:
                # to cut the review into words and find aspect alternatives
                ass = find_aspects_sentiments(content, similar_labels)
            if len(ass) == 0:
                ass[labels[0]] = 0
            corpus.append(ass)
    return corpus


# to recognize sentiment and its strength
def inspect_sentiment(corpus, positives, negatives, log_path, labels):
    aspect_sentiment = []
    logfile = open(log_path, 'w')
    for review in corpus:
        sentiment_vector = dict()
        logfile.write('---------------Here comes a new review-------------------')
        logfile.write(str(review))
        for aspect, sentiment in review.items():
            logfile.write('Review aspect: {0} - {1}'.format(aspect, sentiment))
            if sentiment == 0:
                sentiment_vector[aspect] = 0
                logfile.write('0; ')
            else:
                if set(sentiment).intersection(set(positives)):
                    sentiment_vector[aspect] = 1
                    logfile.write('1; ')
                elif set(sentiment).intersection(set(negatives)):
                    sentiment_vector[aspect] = -1
                    logfile.write('-1; ')
                else:
                    sentiment_vector[aspect] = 0
                    logfile.write('0; ')
        logfile.write('\n')
        aspect_sentiment.append(sentiment_vector)

    return aspect_sentiment


def check_aspect(aspect):
    punctuations = ['，', '。', '！', ',', '.', '!']
    forbidden_words = ['第', '步', '评论']
    if len(aspect) > 6:
        return False
    for word in forbidden_words:
        if word in aspect:
            return False
    for punctuation in punctuations:
        if punctuation in aspect:
            return False
    return True


def find_direct_aspects(reviews):
    aspects = list()

    for line in reviews:
        _, content = re.split(r'%%%', line.strip())
        if '：' in content and '；' in content:
            ass = re.split(r'；', content)
            for a_s in ass:
                if '：' in a_s:
                    aspect, _ = re.split(r'：', a_s)
                    if check_aspect(aspect):
                        aspects.append(aspect)
    return aspects


if __name__ == "__main__":
    # build corpus
    # filename = 'review_sample_clean.txt'
    base_path = r'E://reviewData//Kingston//'
    label_path = base_path + r'labels.txt'
    label_similar_path = base_path + r'labels_alternatives.txt'
    aspects_sentiments_path = base_path + r'aspects_sentiments.txt'
    log_path = base_path + r'log.txt'
    all_review_meta_path = base_path + r'all_review_metas.txt'
    all_review_path = base_path + r'all_reviews.txt'

    vector_path = base_path + r'review_vector.csv'
    aspects = set()

    positive_path = base_path + r'positive_terms.txt'
    negative_path = base_path + r'negative_terms.txt'

    labels = []
    with open(label_path) as similar_file:
        for line in similar_file:
            labels.append(line.strip())

    similar_labels = dict()
    with open(label_similar_path) as similar_file:
        for line in similar_file:
            label, alternatives = re.split(r'：', line.strip())
            similar_labels[label] = alternatives

    positives = []
    with open(positive_path, encoding='utf-8') as pf:
        for line in pf:
            positives.append(line.strip())

    negatives = []
    with open(negative_path, encoding='utf-8') as nf:
        for line in nf:
            negatives.append(line.strip())

    all_review_metas = []
    all_sentiments = []
    all_reviews = []
    all_ass = []
    assdf = pd.DataFrame()

    for root, dirs, files in os.walk(base_path):
        for dir in dirs:
            item_base_path = base_path + dir + r'//'
            print('item_base_path', item_base_path)
            # item_base_path = base_path + r'13_4311178_金士顿 Kingston 240GB SSD固态硬盘 SATA3.0接口 A400系列//'
            # item_base_path = base_path + r'4311178_下图高手//'

            stopreview = ['此用户未填写评价内容']
            meta_file_path = item_base_path + r'review_meta.txt'
            pure_review_path = item_base_path + r'purereviewcontent.txt'

            review_metas = []
            with open(meta_file_path) as meta_file:
                for line in meta_file:
                    review_metas.append(line.strip())

            all_review_metas.append(review_metas)

            pure_reviews = []
            with open(pure_review_path) as pure_review_file:
                for line in pure_review_file:
                    pure_reviews.append(line.strip())

            all_reviews.append(pure_reviews)

            # # to automatically find aspects
            # labels = find_direct_aspects(pure_reviews)
            # print('len of labels ', len(labels))
            # aspects = aspects.union(set(labels))

            # corpus is a list of dicts, in which multi-aspect-oriented sentiments are collected
            corpus = load_corpus(pure_reviews, labels, similar_labels)
            # # to recognize sentiment and its strength
            aspects_sentiments = inspect_sentiment(corpus, positives, negatives, log_path, labels)
            print('aspect_sentiment', len(aspects_sentiments))
            all_ass.append(aspects_sentiments)

            assdf = assdf.append(pd.DataFrame(data=aspects_sentiments))

            with open(aspects_sentiments_path, 'a') as asf:
                for ass in aspects_sentiments:
                    if ass:
                        for k, v in ass.items():
                            label_id = labels.index(k)
                            asf.write(str(label_id))
                            # asf.write(k)
                            asf.write(':')
                            asf.write(str(v))
                            asf.write('; ')
                        asf.write('\n')

    with open(all_review_meta_path, 'w') as rmf:
        for review_metas in all_review_metas:
            for review_meta in review_metas:
                rmf.write(str(review_meta))
                rmf.write('\n')

    with open(all_review_path, 'w') as rf:
        for reviews in all_reviews:
            for review in reviews:
                rf.write(str(review))
                rf.write('\n')

    assdf = assdf.fillna(0)
    assdf.to_csv(vector_path, encoding='ansi')


# -*- coding: utf-8 -*-
"""
@author:XuMing（xuming624@qq.com)
@description: 
"""
import sys

import tensorflow as tf
from sklearn.model_selection import train_test_split

sys.path.append('../..')

from pycorrector.seq2seq_attention import config
from pycorrector.seq2seq_attention.data_reader import create_dataset, max_length, save_word_dict
from pycorrector.seq2seq_attention.model import Seq2SeqModel


def tokenize(lang, maxlen):
    lang_tokenizer = tf.keras.preprocessing.text.Tokenizer(filters='')
    lang_tokenizer.fit_on_texts(lang)
    seq = lang_tokenizer.texts_to_sequences(lang)
    seq = tf.keras.preprocessing.sequence.pad_sequences(seq, maxlen=maxlen, padding='post')
    lang_word2id = lang_tokenizer.word_index
    return seq, lang_word2id


def train(train_path='', model_dir='', save_src_vocab_path='', save_trg_vocab_path='', embedding_dim=256,
          batch_size=64, epochs=4, maxlen=400, hidden_dim=1024, gpu_id=0):
    source_texts, target_texts = create_dataset(train_path, None)
    print(source_texts[-1])
    print(target_texts[-1])

    source_seq, source_word2id = tokenize(source_texts, maxlen)
    target_seq, target_word2id = tokenize(target_texts, maxlen)
    save_word_dict(source_word2id, save_src_vocab_path)
    save_word_dict(target_word2id, save_trg_vocab_path)

    # Calculate max_length of the target tensors
    max_length_target, max_length_source = max_length(target_seq), max_length(source_seq)
    print(max_length_target, max_length_source)

    # Creating training and validation sets using an 80-20 split
    source_seq_train, source_seq_val, target_seq_train, target_seq_val = train_test_split(source_seq,
                                                                                          target_seq,
                                                                                          test_size=0.2)

    # Show length
    print(len(source_seq_train), len(target_seq_train), len(source_seq_val), len(target_seq_val))

    steps_per_epoch = len(source_seq_train) // batch_size
    print(steps_per_epoch)
    dataset = tf.data.Dataset.from_tensor_slices((source_seq_train, target_seq_train)).shuffle(len(source_seq_train))
    dataset = dataset.batch(batch_size, drop_remainder=True)
    example_source_batch, example_target_batch = next(iter(dataset))
    model = Seq2SeqModel(source_word2id, target_word2id, embedding_dim=embedding_dim,
                         hidden_dim=hidden_dim, batch_size=batch_size, maxlen=maxlen, checkpoint_path=model_dir,
                         gpu_id=gpu_id)
    model.train(example_source_batch, dataset, steps_per_epoch, epochs=epochs)

    sentence = "例 如 病 人 必 须 在 思 想 清 醒 时 。"
    result, sentence, attention_plot = model.evaluate(sentence)

    print('Input: %s' % (sentence))
    print('Predicted translation: {}'.format(result))


if __name__ == "__main__":
    train(train_path=config.train_path,
          model_dir=config.model_dir,
          save_src_vocab_path=config.save_src_vocab_path,
          save_trg_vocab_path=config.save_trg_vocab_path,
          embedding_dim=config.embedding_dim,
          batch_size=config.batch_size,
          epochs=config.epochs,
          maxlen=config.maxlen,
          hidden_dim=config.hidden_dim,
          gpu_id=config.gpu_id)

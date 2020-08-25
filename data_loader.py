import torchtext.data as data
from torchtext.data import Field, BucketIterator, Iterator
from utils import get_sent_file
import os

class Librispeech(data.Dataset):    
    def __init__(self, data_lines, G_FIELD, P_FIELD):
        fields = [('grapheme', G_FIELD), ('phoneme', P_FIELD)]
        examples = []
        for line in data_lines:
            grapheme, phoneme = line.split('##')
            examples.append(data.Example.fromlist([grapheme, phoneme], fields))
        self.sort_key = lambda x:len(x.grapheme)
        super().__init__(examples, fields)

    @classmethod
    def splits(cls, fpath, g_field, p_field):
        with open(fpath+'sent_train.txt', 'r', encoding='utf-8') as train_f,\
        open(fpath+'sent_dev.txt', 'r', encoding='utf-8') as val_f,\
        open(fpath+'sent_test.txt', 'r', encoding='utf-8') as test_f:
            train_lines = train_f.readlines()
            val_lines = val_f.readlines()
            test_lines = test_f.readlines()
        
        train_data = cls(train_lines, g_field, p_field)
        val_data = cls(val_lines, g_field, p_field)
        test_data = cls(test_lines, g_field, p_field)

        print(f"Number of training examples: {len(train_data.examples)}")
        print(f"Number of validation examples: {len(val_data.examples)}")
        print(f"Number of testing examples: {len(test_data.examples)}")

        return (train_data, val_data, test_data)
    
class DataLoader:
    def __init__(self, fpath, librispeech, batch_size, device, model_type):
        
        self.batch_first = False
        if model_type == 'transformer':
            self.batch_first = True

        self.G_FIELD = Field(init_token='<sos>',
                eos_token='<eos>',
                tokenize=(lambda x: x.split()),
                batch_first=True)
        self.P_FIELD = Field(init_token='<sos>',
                eos_token='<eos>',
                tokenize=(lambda x: x.split()),
                batch_first=True)

        if not os.path.exists(os.path.join(fpath, 'sent_train.txt')):
            self.load_dataset(fpath)
        
        self.librispeech = librispeech
        self.train_data, self.val_data, self.test_data = self.librispeech.splits(fpath, self.G_FIELD, self.P_FIELD)
        self.batch_size = batch_size
        self.device = device
        print(vars(self.train_data.examples[0]))
        print(vars(self.val_data.examples[0]))

        self.G_FIELD.build_vocab(self.train_data, self.val_data, self.test_data)
        self.P_FIELD.build_vocab(self.train_data, self.val_data, self.test_data)
        # print(self.G_FIELD.vocab.stoi)
        # print(self.P_FIELD.vocab.stoi)
    
    def load_dataset(self, fpath):
        for type in 'train dev test'.split():
            get_sent_file(fpath, type)


    def build_iterator(self):
        train_iter = Iterator(self.train_data, batch_size=self.batch_size, train=True, device=self.device, shuffle=False)
        val_iter = Iterator(self.val_data, batch_size=self.batch_size, train=False, device=self.device, shuffle=False)
        test_iter = Iterator(self.test_data, batch_size=1, train=False, device=self.device)

        # batch = next(iter(train_iter))
        # print(batch.grapheme)
        # print(batch.grapheme.shape)
        # print(batch.phoneme)
        # print(batch.phoneme.shape)
        # print(' '.join([self.G_FIELD.vocab.itos[i] for i in batch.grapheme.view(-1).numpy()]))
        # print(' '.join([self.P_FIELD.vocab.itos[i] for i in batch.phoneme.view(-1).numpy()]))       

        # batch = next(iter(val_iter))
        # print(batch.grapheme)
        # print(batch.grapheme.shape)
        # print(batch.phoneme)
        # print(batch.phoneme.shape)
        # print(' '.join([self.G_FIELD.vocab.itos[i] for i in batch.grapheme.view(-1).numpy()]))
        # print(' '.join([self.P_FIELD.vocab.itos[i] for i in batch.phoneme.view(-1).numpy()]))     
        # raise Exception('dd')
        return (train_iter, val_iter, test_iter)


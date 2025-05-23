import time
import yaml
import argparse
import torch
import torch.nn.functional as F
import torchmetrics
from sklearn.metrics import r2_score
from model_node import Specformer
from utils import count_parameters, init_params, seed_everything, get_split


def main_worker(args, config):
    print(args, config)
    seed_everything(args.seed)
    device = 'cuda:{}'.format(args.cuda)
    torch.cuda.set_device(device)

    epoch = config['epoch']
    lr = config['lr']
    weight_decay = config['weight_decay']
    nclass = config['nclass']
    nlayer = config['nlayer']
    hidden_dim = config['hidden_dim']
    num_heads = config['num_heads']
    tran_dropout = config['tran_dropout']
    feat_dropout = config['feat_dropout']
    prop_dropout = config['prop_dropout']
    norm = config['norm']


    if 'signal' in args.dataset:
        e, u, x, y, m = torch.load('data/{}.pt'.format(args.dataset))
        e, u, x, y, m = e.cuda(), u.cuda(), x.cuda(), y.cuda(), m.cuda()
        mask = torch.where(m == 1)
        x = x[:, args.image].unsqueeze(1)
        y = y[:, args.image]
    else:
        e, u, x, y = torch.load('data/{}.pt'.format(args.dataset))
        e, u, x, y = e.cuda(), u.cuda(), x.cuda(), y.cuda()

        if len(y.size()) > 1:
            if y.size(1) > 1:
                y = torch.argmax(y, dim=1)
            else:
                y = y.view(-1)

    nfeat = x.size(1)
    net = Specformer(nclass,nfeat, nlayer, hidden_dim, num_heads, tran_dropout, feat_dropout, prop_dropout, norm).cuda()
    net.apply(init_params)
    print(count_parameters(net))

    start_time=time.time()
    for _ in range(500):
        _ = net(e, u, x)
    end_time=time.time()
    print(end_time-start_time)
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', type=int, default=1)
    parser.add_argument('--cuda', type=int, default=0)
    parser.add_argument('--dataset', default='signal_low')
    parser.add_argument('--image', type=int, default=0)

    args = parser.parse_args()
    
    if 'signal' in args.dataset:
        config = yaml.load(open('config.yaml'), Loader=yaml.SafeLoader)['signal']
    else:
        config = yaml.load(open('config.yaml'), Loader=yaml.SafeLoader)[args.dataset]

    main_worker(args, config)


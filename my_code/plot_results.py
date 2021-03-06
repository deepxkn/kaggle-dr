import sys
import cPickle
import numpy
import matplotlib.pyplot as plt
import argparse

import pdb

def plot_results(result_file, max_epoch, include_training_variance):
    result_file_id = result_file.split('-')[0].split('/')[-1]
    f = open(result_file)
    historical_train_losses, historical_val_losses, historical_val_kappas, n_iter_per_epoch = cPickle.load(f)
    n_iter_per_epoch = float(n_iter_per_epoch)
    try:
        learn_rate_reduced_epochs = cPickle.load(f)
    except EOFError:
        learn_rate_reduced_epochs = [[]] # looks like if there is only 1 thing loaded, it unpacks as an array
    learn_rate_reduced_epochs = learn_rate_reduced_epochs[0]

    train = numpy.array(historical_train_losses)
    valid = numpy.array(historical_val_losses)
    kappa = numpy.array(historical_val_kappas)
    # scale iter to epoch
    train[:,0] = train[:,0] / n_iter_per_epoch
    valid[:,0] = valid[:,0] / n_iter_per_epoch
    kappa[:,0] = kappa[:,0] / n_iter_per_epoch

    if sum(numpy.isnan(train[:,1])):
        first_nan = numpy.isnan(train[:,1]).tolist().index(True) / n_iter_per_epoch
        last_nan = len(train[:,1]) - numpy.isnan(train[:,1]).tolist()[::-1].index(True) / n_iter_per_epoch
        plt.axvspan(first_nan, last_nan, facecolor='r', alpha=0.5)
        plt.text(first_nan - 7, -0.5, "nan Zone ->", color='r', size=18)

    plt.plot(train[:,0], train[:,1], 'g', label="Training Loss")
    plt.plot(valid[:,0], valid[:,1], 'r', label="Validation Loss")
    plt.plot(kappa[:,0], kappa[:,1], 'b', label="Validation Kappa")
    plt.xlabel("Epochs. Decays at: {}".format(learn_rate_reduced_epochs))

    if include_training_variance:
        errors_by_epoch = {}
        for idx, epoch in enumerate([int(itr) for itr in train[:,0]]):
            if not errors_by_epoch.get(epoch):
                errors_by_epoch[epoch] = []
            errors_by_epoch[epoch].append(train[:,1][idx])
        training_epochs = list(range(1, len(errors_by_epoch))) # skip very first epoch b/c of super-high variance
        training_variances = numpy.array([numpy.var(errors_by_epoch[epoch]) for epoch in training_epochs])
        plt.plot(training_epochs, (training_variances / max(training_variances)), 'black', label="Rescaled Training Variances")

    best_valy_idx, best_valy = min(enumerate(valid[:,1]), key=lambda p: p[1])
    best_valx = valid[best_valy_idx, 0]

    best_kapy_idx, best_kapy = max(enumerate(kappa[:,1]), key=lambda p: p[1])
    best_kapx = kappa[best_kapy_idx, 0]

    plt.ylabel("Best Val: %.3f (%.0f) and Kappa: %.3f (%.0f)" % (best_valy, best_valx, best_kapy, best_kapx))

    plt.axhline(y=best_valy, color='r', ls='dashed')
    best_val_marker = plt.Circle((best_valx,best_valy),1,color='r',fill=False, clip_on=False)

    plt.axhline(y=best_kapy, color='b', ls='dashed')
    best_kap_marker = plt.Circle((best_kapx,best_kapy),1,color='b',fill=False, clip_on=False)

    plt.scatter([best_valx], [best_valy], color='r', s=500,zorder=21,alpha=0.5)
    plt.scatter([best_kapx], [best_kapy], color='b', s=500,zorder=20,alpha=0.5)

    for epoch in learn_rate_reduced_epochs:
        plt.axvline(x=epoch, color='g')
    plt.title("%s\n%s" % (result_file, result_file_id))
    plt.ylim((-1,1.5))

    if max_epoch:
        plt.xlim((0,max_epoch))
    else:
        plt.xlim((0,len(train[:,1]) / n_iter_per_epoch))

    plt.legend(loc=3)
    plt.grid()
    plt.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-f",
                        "--result-file",
                        type=str,
                        default=None)
    parser.add_argument("-m",
                        "--max-epoch",
                        type=float,
                        default=None)
    parser.add_argument("-v",
                        "--include-training-variance",
                        type=bool,
                        default=False)
    _ = parser.parse_args()
    plot_results(_.result_file, _.max_epoch, _.include_training_variance)

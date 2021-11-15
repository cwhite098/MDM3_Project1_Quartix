import numpy as np
from sklearn.metrics import normalized_mutual_info_score, adjusted_rand_score
from scipy.optimize import linear_sum_assignment as linear_assignment
from itertools import chain, combinations
import matplotlib.pyplot as plt

nmi = normalized_mutual_info_score
ari = adjusted_rand_score

def acc(y_true, y_pred):
    """
    Calculate clustering accuracy. Require scikit-learn installed
    # Arguments
        y: true labels, numpy.array with shape `(n_samples,)`
        y_pred: predicted labels, numpy.array with shape `(n_samples,)`
    # Return
        accuracy, in [0,1]
    """
    y_true = y_true.astype(np.int64)
    assert y_pred.size == y_true.size
    D = max(y_pred.max(), y_true.max()) + 1
    w = np.zeros((D, D), dtype=np.int64)
    for i in range(y_pred.size):
        w[y_pred[i], y_true[i]] += 1
    ind = np.transpose(np.asarray(linear_assignment(w.max() - w)))
    return sum([w[i, j] for i, j in ind]) * 1.0 / y_pred.size



def get_optimal_conmat(conmat, plot_ROC = True):

    clusters = np.linspace(0,conmat.shape[0]-1,conmat.shape[0], dtype=int)

    def powerset(iterable):
        "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
        s = list(iterable)
        return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

    powerset_clusters = list(powerset(clusters))

    mat_list = []
    FNR_list = []
    FPR_list = []
    TPR_list = []
    for i in range(int(len(powerset_clusters)/2)):

        new_mat = np.hstack( 
            (np.reshape(np.sum(conmat[:2, powerset_clusters[i]], axis=1), (2,1)), 
            np.reshape(np.sum(conmat[:2, np.delete(clusters, powerset_clusters[i])],axis=1), (2,1)))
            )

        FNR = 1 - (new_mat[1,1]/(new_mat[1,0] + new_mat[1,1]))

        TPR = (new_mat[1,1]/(new_mat[1,0] + new_mat[1,1]))
        FPR = (new_mat[0,1]/(new_mat[0,0] + new_mat[0,1]))

        mat_list.append(new_mat)
        FNR_list.append(FNR)
        FPR_list.append(FPR)
        TPR_list.append(TPR)

    ROC_points = np.vstack((np.array(FPR_list), np.array(TPR_list)))

    scores = []
    for point in range(ROC_points.shape[1]):
        score = np.linalg.norm(ROC_points[:,point] - [0,1])
        scores.append(score)

    optimal_idx = np.argmin(np.array(scores))

    optimal_assignment = powerset_clusters[optimal_idx]
    optimal_mat = mat_list[optimal_idx]

    optimal_FPR = FPR_list[optimal_idx]
    optimal_FNR = FNR_list[optimal_idx]

    if plot_ROC:
        plt.plot([0,1],[0,1],'--', c='r')
        plt.scatter(FPR_list, TPR_list)
        plt.scatter(FPR_list[optimal_idx], TPR_list[optimal_idx])
        plt.title('ROC'), plt.xlabel('FPR'), plt.ylabel('TPR')
        plt.show()

    return optimal_mat, optimal_assignment, optimal_FNR, optimal_FPR
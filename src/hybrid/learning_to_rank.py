import itertools
import numpy as np
import json

from sklearn import svm, linear_model, cross_validation


def transform_pairwise(X, y):
    """Transforms data into pairs with balanced labels for ranking
    Transforms a n-class ranking problem into a two-class classification
    problem. Subclasses implementing particular strategies for choosing
    pairs should override this method.
    In this method, all pairs are choosen, except for those that have the
    same target value. The output is an array of balanced classes, i.e.
    there are the same number of -1 as +1
    Parameters
    ----------
    X : array, shape (n_samples, n_features)
        The data
    y : array, shape (n_samples,) or (n_samples, 2)
        Target labels. If it's a 2D array, the second column represents
        the grouping of samples, i.e., samples with different groups will
        not be considered.
    Returns
    -------
    X_trans : array, shape (k, n_feaures)
        Data as pairs
    y_trans : array, shape (k,)
        Output class labels, where classes have values {-1, +1}
    """
    X_new = []
    y_new = []
    y = np.asarray(y)
    if y.ndim == 1:
        y = np.c_[y, np.ones(y.shape[0])]
    comb = itertools.combinations(range(X.shape[0]), 2)
    for k, (i, j) in enumerate(comb):
        if y[i, 0] == y[j, 0] or y[i, 1] != y[j, 1]:
            # skip if same target or different group
            continue
        X_new.append(X[i] - X[j])
        y_new.append(np.sign(y[i, 0] - y[j, 0]))
        # output balanced classes
        if y_new[-1] != (-1) ** k:
            y_new[-1] = - y_new[-1]
            X_new[-1] = - X_new[-1]
    return np.asarray(X_new), np.asarray(y_new).ravel()


class RankSVM(svm.LinearSVC):
    """Performs pairwise ranking with an underlying LinearSVC model
    Input should be a n-class ranking problem, this object will convert it
    into a two-class classification problem, a setting known as
    `pairwise ranking`.
    See object :ref:`svm.LinearSVC` for a full description of parameters.
    """

    def fit(self, X, y):
        """
        Fit a pairwise ranking model.
        Parameters
        ----------
        X : array, shape (n_samples, n_features)
        y : array, shape (n_samples,) or (n_samples, 2)
        Returns
        -------
        self
        """
        X_trans, y_trans = transform_pairwise(X, y)
        super(RankSVM, self).fit(X_trans, y_trans)
        return self

    def decision_function(self, X):
        return np.dot(X, self.coef_.ravel())

    def predict(self, X):
        """
        Predict an ordering on X. For a list of n samples, this method
        returns a list from 0 to n-1 with the relative order of the rows of X.
        The item is given such that items ranked on top have are
        predicted a higher ordering (i.e. 0 means is the last item
        and n_samples would be the item ranked on top).
        Parameters
        ----------
        X : array, shape (n_samples, n_features)
        Returns
        -------
        ord : array, shape (n_samples,)
            Returns a list of integers representing the relative order of
            the rows in X.
        """
        if hasattr(self, 'coef_'):
            return np.argsort(np.dot(X, self.coef_.ravel()))
        else:
            raise ValueError("Must call fit() prior to predict()")

    def score(self, X, y):
        """
        Because we transformed into a pairwise problem, chance level is at 0.5
        """
        X_trans, y_trans = transform_pairwise(X, y)
        return np.mean(super(RankSVM, self).predict(X_trans) == y_trans)

class LearningToRank:
    def __init__(self):
        pass

    def learning_to_rank(self,simscores_across_features, events, members, hybrid_simscores):

        #### Basic Average of simscores
        # for member in members:
        #     for event in events:
        #         for feature in simscores_across_features:
        #             hybrid_simscores[member][event] += simscores_across_features[feature][member][event]
        #
        # args = sorted(hybrid_simscores['11173777'].items(), key=operator.itemgetter(1))[-6:-1]
        # print "Top 5 events recommended to user 11173777", args

        print len(simscores_across_features["location_classifier"]["12563492"])
        print len(simscores_across_features["content_classifier"]["12563492"])
        print len(simscores_across_features["time_classifier"]["12563492"])
        print len(simscores_across_features["grp_freq_classifier"]["12563492"])

        arr1 = np.array(simscores_across_features["location_classifier"]["12563492"].values())
        arr2 = np.array(simscores_across_features["content_classifier"]["12563492"].values())
        arr3 = np.array(simscores_across_features["time_classifier"]["12563492"].values())
        arr4 = np.array(simscores_across_features["grp_freq_classifier"]["12563492"].values())

        result = np.column_stack((arr1, arr2, arr3, arr4))

        # as showcase, we will create some non-linear data
        # and print the performance of ranking vs linear regression

        np.random.seed(1)
        n_samples, n_features = 30587, 4
        true_coef = np.random.randn(n_features)
        # X = np.random.randn(n_samples, n_features)
        X = result
        noise = np.random.randn(n_samples) / np.linalg.norm(true_coef)
        y = np.dot(X, true_coef)
        y = np.arctan(y)  # add non-linearities
        y += .1 * noise  # add noise
        Y = np.c_[y, np.mod(np.arange(n_samples), 4)]  # add query fake id
        cv = cross_validation.KFold(n_samples, 4)
        train, test = iter(cv).next()

        # print the performance of ranking
        rank_svm = RankSVM().fit(X[train], Y[train])
        print 'Performance of ranking ', rank_svm.score(X[test], Y[test])

        # and that of linear regression
        ridge = linear_model.RidgeCV(fit_intercept=True)
        ridge.fit(X[train], y[train])
        X_test_trans, y_test_trans = transform_pairwise(X[test], y[test])
        score = np.mean(np.sign(np.dot(X_test_trans, ridge.coef_)) == y_test_trans)
        print 'Performance of linear regression ', score
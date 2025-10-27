from sklearn.metrics import classification_report, roc_auc_score


def cls_metric(ground_truth_labels, predict_labels):
    return classification_report(
        y_true=ground_truth_labels,
        y_pred=predict_labels,
        target_names=["negatives", "positives"],
        digits=4,
        output_dict=True,
    )


def auc_metric(ground_truth_labels, predict_probs):
    return roc_auc_score(ground_truth_labels, predict_probs)

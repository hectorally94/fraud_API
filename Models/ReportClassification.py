class ReportClassification:
  def __init__(self, precision, recall, f1score,support,classes):
    self.precision = precision
    self.recall = recall
    self.f1score = f1score
    self.support=support
    self.classes=classes
    
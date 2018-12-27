import Graph
import networkx as nx
import numpy as np

class Metric:
    def calculate(self, graph):
        raise NotImplementedError('calculate method must be implemented by concrete metric class')

    def getMetricName(self):
        raise NotImplementedError('getMetricName method must be implemented by concrete metric class')

    def plot(self, plt, x,y, xlabel='version', label=''):
        raise NotImplementedError('plot method must be implemented by concrete metric class')

def plotLinear(plt, x, y, title, xlabel, ylabel,label):
    plt.plot(x,y,label=label)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

class MetricGraphSize(Metric):
    def calculate(self, graph):
        return len(graph.nodes)

    def getMetricName(self):
        return 'GraphSize'

    def plot(self, plt, x,y, xlabel='version', label=''):
        plotLinear(plt, x, y, self.getMetricName(), xlabel, 'Number of nodes', label)

class MetricAvgClustering(Metric):
    def calculate(self, graph):
        return nx.average_clustering(graph)

    def getMetricName(self):
        return 'AverageClustering'

    def plot(self, plt, x,y, xlabel='version', label=''):
        plotLinear(plt, x, y, self.getMetricName(), xlabel, 'Clustering coefficient', label)

class MetricDensity(Metric):
    def calculate(self, graph):
        return nx.density(graph)

    def getMetricName(self):
        return 'Density'

    def plot(self, plt, x,y, xlabel='version', label=''):
        plotLinear(plt, x,y, self.getMetricName(), xlabel, 'Density', label)

class MetricOpinionConsensus(Metric):
    def __init__(self, topicIndex=None):
        self.topicIndex = topicIndex if topicIndex is not None else 'All'

    def _calcForTopic(self, graph, ind):
        opinions = [graph.nodes[nid][Graph.KEY_OPINIONS][ind] for nid in graph.nodes]
        numberPositive = np.sum(np.array(opinions) > 0)
        numberNegative = np.sum(np.array(opinions) < 0)
        return 1 - min(numberPositive,numberNegative)/max(numberPositive,numberNegative)

    def calculate(self, graph):
        consensus = []
        topicIndex = self.topicIndex if self.topicIndex is not 'All' else list(range(len(graph.nodes[0][Graph.KEY_OPINIONS])))

        for i in topicIndex:
            consensus.append(self._calcForTopic(graph, i))

        return np.mean(consensus)

    def getMetricName(self):
        return 'OpinionConsensus' + str(self.topicIndex)

    def plot(self, plt, x,y, xlabel='version', label=''):
        plotLinear(plt, x,y, self.getMetricName(), xlabel, 'Consensus', label)

defaultConfig = {
    'stepSize' : 10
}

availableMetrics = [
    MetricGraphSize(),
    MetricAvgClustering(),
    MetricDensity(),
    MetricOpinionConsensus(),
]

class Analyser:
    def initAnalysis(self, graph, metrics = availableMetrics, config = defaultConfig):
        self.metrics = metrics
        self.config = config
        self.results = {metric.getMetricName():[] for metric in metrics}
        self.results['version'] = []

    def _calcMetrics(self, graph):
        self.results['version'].append(Graph.getVersion(graph))
        for metric in self.metrics:
            self.results[metric.getMetricName()].append(metric.calculate(graph))

    def onNewVersion(self, graph):
        if Graph.getVersion(graph) % self.config['stepSize'] < 1e5:
            self._calcMetrics(graph)

    def finishAnalysis(self, graph):
        if self.results['version'][-1] != Graph.getVersion(graph):
            self._calcMetrics(graph)

    # ToDo: export this to a viewer module
    def plot(self):
        import matplotlib.pyplot as plt
        for metric in self.metrics:
            plt.figure()
            metric.plot(plt, self.results['version'], self.results[metric.getMetricName()])

        plt.show()

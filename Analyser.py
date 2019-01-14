import Graph
import networkx as nx
import numpy as np
import community
import utility
import csv

class Metric:
    def calculate(self, graph):
        raise NotImplementedError('calculate method must be implemented by concrete metric class')

    def getMetricName(self):
        raise NotImplementedError('getMetricName method must be implemented by concrete metric class')

    def plot(self, plt, x,y, xlabel='version', label=''):
        raise NotImplementedError('plot method must be implemented by concrete metric class')

def plotLinear(plt, x, y, title, xlabel, ylabel,label):
    plt.plot(x,y,label=label,marker='*',linestyle='dashed')
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

class MetricTransitivity(Metric):
    def calculate(self, graph):
        return nx.transitivity(graph)

    def getMetricName(self):
        return 'Transitivity'

    def plot(self, plt, x,y, xlabel='version', label=''):
        plotLinear(plt, x, y, self.getMetricName(), xlabel, 'Transitivity', label)

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

class MetricOpinionStrength(Metric):
    def __init__(self, topicIndex=None):
        self.topicIndex = topicIndex if topicIndex is not None else 'All'

    def _calcForTopic(self, graph, ind):
        opinions = np.array([graph.nodes[nid][Graph.KEY_OPINIONS][ind] for nid in graph.nodes])
        numberNeutral = np.sum(opinions == 0)
        return numberNeutral/opinions.size

    def calculate(self, graph):
        strength = []
        topicIndex = self.topicIndex if self.topicIndex is not 'All' else list(range(len(graph.nodes[0][Graph.KEY_OPINIONS])))

        for i in topicIndex:
            strength.append(self._calcForTopic(graph, i))

        return np.mean(strength)

    def getMetricName(self):
        return 'OpinionStrength' + str(self.topicIndex)

    def plot(self, plt, x,y, xlabel='version', label=''):
        plotLinear(plt, x,y, self.getMetricName(), xlabel, 'Strength', label)

class MetricNumberOfClusters(Metric):
    def calculate(self, graph):
        return max(community.best_partition(graph).values())

    def getMetricName(self):
        return 'NumberOfClusters'

    def plot(self, plt, x,y, xlabel='version', label=''):
        plotLinear(plt, x,y, self.getMetricName(), xlabel, 'Number', label)

class MetricMeanOrientation(Metric):
    def calculate(self, graph):
        return np.mean([graph.edges[eid][Graph.KEY_ORIENTATION] for eid in graph.edges])

    def getMetricName(self):
        return 'MeanOrientation'

    def plot(self, plt, x,y, xlabel='version', label=''):
        plotLinear(plt, x,y, self.getMetricName(), xlabel, 'Mean orientation', label)

class HelperMetricVersion(Metric):
    def calculate(self, graph):
        return Graph.getVersion(graph)

    def getMetricName(self):
        return 'Version'

    def plot(self, plt, x,y, xlabel='version', label=''):
        plotLinear(plt, x,y, self.getMetricName(), xlabel, 'Version', label)

defaultConfig = {
    'stepSize' : 10
}

availableMetrics = [
    MetricGraphSize(),
    MetricAvgClustering(),
    MetricDensity(),
    MetricOpinionConsensus(),
    MetricOpinionStrength(),
    MetricTransitivity(),
    MetricNumberOfClusters(),
    MetricMeanOrientation(),
]

class Analyser:
    def initAnalysis(self, graph, metrics = availableMetrics, config = defaultConfig):
        self.metrics = [HelperMetricVersion()] + metrics
        self.config = config
        self.results = {metric.getMetricName():[] for metric in self.metrics}

    def _calcMetrics(self, graph):
        for metric in self.metrics:
            self.results[metric.getMetricName()].append(metric.calculate(graph))

    def onNewVersion(self, graph):
        if utility.isDivisor(Graph.getVersion(graph), self.config['stepSize']):
            self._calcMetrics(graph)

    def finishAnalysis(self, graph):
        if self.results[HelperMetricVersion().getMetricName()][-1] != Graph.getVersion(graph):
            self._calcMetrics(graph)

    def write(self, filename):
        w = csv.writer(open(filename, 'w'))
        w.writerow([name for name in self.results.keys()])
        for i in range(len(self.results[HelperMetricVersion().getMetricName()])):
            w.writerow([m[i] for m in self.results.values()])

    # ToDo: export this to a viewer module
    def plot(self):
        import matplotlib.pyplot as plt
        for metric in self.metrics:
            plt.figure()
            metric.plot(plt, self.results['version'], self.results[metric.getMetricName()])

        plt.show()

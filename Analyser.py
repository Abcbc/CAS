import Graph
import networkx as nx
import numpy as np

class Metric:
    def calculate(self, graph):
        raise NotImplementedError('calculate method must be implemented by concrete metric class')

    def getMetricName(self):
        raise NotImplementedError('getMetricName method must be implemented by concrete metric class')

    def plot(self, plt, x,y, xlabel='version'):
        raise NotImplementedError('plot method must be implemented by concrete metric class')

def plotLinear(plt, x, y, title, xlabel, ylabel):
    plt.plot(x,y)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

class MetricGraphSize(Metric):
    def calculate(self, graph):
        return len(graph.nodes)

    def getMetricName(self):
        return 'GraphSize'

    def plot(self, plt, x,y, xlabel='version'):
        plotLinear(plt, x, y, self.getMetricName(), xlabel, 'Number of nodes')

class MetricAvgClustering(Metric):
    def calculate(self, graph):
        return nx.average_clustering(graph)

    def getMetricName(self):
        return 'AverageClustering'

    def plot(self, plt, x,y, xlabel='version'):
        plotLinear(plt, x, y, self.getMetricName(), xlabel, 'Clustering coefficient')

defaultConfig = {
    'stepSize' : 10
}

availableMetrics = [
    MetricGraphSize(),
    MetricAvgClustering(),
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
        import matplotlib.pyplot as plt
        for metric in self.metrics:
            plt.figure()
            metric.plot(plt, self.results['version'], self.results[metric.getMetricName()])

        plt.show()

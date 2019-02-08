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

    # ToDo works not for all, e.g. not for histogram
    @staticmethod
    def mean_std(runs):
        runs_combined = np.array([run for run in runs]) # each row is a run
        return (np.mean(runs_combined, axis=0), np.std(runs_combined, axis=0))

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

class MetricNumberOfEdges(Metric):
    def calculate(self, graph):
        return len(graph.edges)

    def getMetricName(self):
        return 'NumberOfEdges'

    def plot(self, plt, x,y, xlabel='version', label=''):
        plotLinear(plt, x, y, self.getMetricName(), xlabel, 'Number of edges', label)

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

class MetricGraphProperty(Metric):
    def __init__(self, getter_lambda, name):
        self.getter = getter_lambda
        self.name = name

    def calculate(self, graph):
        return self.getter(graph)

    def getMetricName(self):
        return self.name

    def plot(self, plt, x,y, xlabel='version', label=''):
        plotLinear(plt, x, y, self.getMetricName(), xlabel, self.getMetricName(), label)

class MetricOpinionConsensus(Metric):
    def __init__(self, topicIndex=None):
        self.topicIndex = topicIndex if topicIndex is not None else 'All'

    def _calcForTopic(self, graph, ind):
        opinions = [graph.nodes[nid][Graph.KEY_OPINIONS][ind] for nid in graph.nodes]
        numberPositive = np.sum(np.array(opinions) > 0)
        numberNegative = np.sum(np.array(opinions) < 0)
        if numberPositive == 0 and numberNegative == 0:
            return 0 # no opinion is not really consensus
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
        return 1-numberNeutral/opinions.size

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
        return max(community.best_partition(graph).values())+1

    def getMetricName(self):
        return 'NumberOfClusters'

    def plot(self, plt, x,y, xlabel='version', label=''):
        plotLinear(plt, x,y, self.getMetricName(), xlabel, 'Number', label)

class MetricMeanOrientation(Metric):
    def calculate(self, graph):
        if len(graph.edges) == 0:
            return 0
        return np.mean([graph.edges[eid][Graph.KEY_ORIENTATION] for eid in graph.edges])

    def getMetricName(self):
        return 'MeanOrientation'

    def plot(self, plt, x,y, xlabel='version', label=''):
        plotLinear(plt, x,y, self.getMetricName(), xlabel, 'Mean orientation', label)

class MetricAggregateValues(Metric):
    class Getter:
        def __init__(self, getter_lambda, name):
            self.getter_lambda = getter_lambda
            self.name = name
        def get(self, graph, node_id):
            return self.getter_lambda(graph, node_id)
        def get_name(self):
            return self.name
    class Getter_attribute(Getter):
        def __init__(self, attr_name):
            self.getter_lambda = lambda graph, node_id: graph.nodes[node_id][attr_name]
            self.name = attr_name

    def __init__(self, getter):
        self.getter = getter

# min value is 0!
class MetricHistogram(MetricAggregateValues):
    def __init__(self, getter):
        super().__init__(getter)

    def calculate(self, graph):
        vals = np.array([self.getter.get(graph, nid) for nid in graph.nodes])

        max = np.max(vals)
        nbins = int(np.ceil(max))
        nbins = nbins+1 if nbins == 0 else nbins
        return np.histogram(vals, bins=nbins, range=(0,max))

    def getMetricName(self):
        return 'Histogram'+self.getter.get_name()

    @staticmethod
    def mean_std(runs):
        runs = np.array(runs)
        maxlen = [max([len(run[it][0]) for run in runs]) for it in range(len(runs[0]))]
        bins = np.array([np.array(range(maxlen_+1)) for maxlen_ in maxlen])

        combined_hists = np.array([[(np.pad(hist[0],[0,maxlen_-len(hist[0])],'constant',constant_values=0),bins_) for hist in runs[:,i,:]] for i,maxlen_,bins_ in zip(range(len(runs[0])),maxlen,bins)])

        mean_hist = (np.mean(combined_hists, axis=1))
        iterations = len(mean_hist[0][0])
        fake_std = (np.zeros(iterations), np.zeros(iterations+1))
        fake_std = np.array([fake_std for _ in range(len(mean_hist))])
        return (mean_hist, fake_std) # no std

class MetricMean(MetricAggregateValues):
    def calculate(self, graph):
        return np.mean([self.getter.get(graph, nid) for nid in graph.nodes])

    def getMetricName(self):
        return 'Mean'+self.getter.get_name()

class MetricStd(MetricAggregateValues):
    def calculate(self, graph):
        return np.std([self.getter.get(graph, nid) for nid in graph.nodes])

    def getMetricName(self):
        return 'Std'+self.getter.get_name()


class MetricCommunities(Metric):
    def calculate(self, graph):
        bp = community.best_partition(graph)
        comms = [[nid for nid in community.best_partition(graph) if bp[nid]==i] for i in range(20)]
        comms = [comm for comm in comms if len(comm)>0]
        try:
            return sorted([len(comm) for comm in comms]),community.modularity(bp, graph)
        except ValueError:
            return [0],0

    def getMetricName(self):
        return 'Communities'

    def plot(self, plt, x,y, xlabel='version', label=''):
        raise NotImplementedError

    @staticmethod
    def mean_std(runs):
        # just return the first run. How to average?
        return (runs[0],np.zeros(len(runs[0])))

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
    MetricNumberOfEdges(),
    MetricAvgClustering(),
    MetricDensity(),
    MetricOpinionConsensus(),
    MetricOpinionStrength(),
    MetricTransitivity(),
    MetricNumberOfClusters(),
    MetricMeanOrientation(),
    # MetricHistogram(MetricHistogram.Getter_attribute(Graph.KEY_V), 0, 50,250),
    MetricHistogram(MetricAggregateValues.Getter(lambda graph, nid: nx.degree(graph, nid), 'Degree')),
    # MetricMean(MetricAggregateValues.Getter(lambda graph, nid: nx.degree(graph, nid), 'Degree')), # disabled to save computations, most information is in histogram
    # MetricStd(MetricAggregateValues.Getter(lambda graph, nid: nx.degree(graph, nid), 'Degree')), # disabled to save computations, most information is in histogram
    MetricGraphProperty(lambda graph: nx.is_connected(graph), 'Connectedness'),
    MetricGraphProperty(lambda graph: community.modularity(community.best_partition(graph),graph), 'Modularity'),
    # MetricCommunities(), # disabled, not much to get from this metric, just modularity is measured above

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

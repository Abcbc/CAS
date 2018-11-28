import Graph

class Metric:
    def calculate(self, graph):
        raise NotImplementedError('calculate method must be implemented by concrete metric class')

    @staticmethod
    def getMetricName():
        raise NotImplementedError('getMetricName method must be implemented by concrete metric class')

def plotLinear(plt, x, y, title, xlabel, ylabel):
    plt.plot(x,y)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

class MetricGraphSize(Metric):
    def calculate(self, graph):
        return len(graph.nodes)

    @staticmethod
    def getMetricName():
        return 'GraphSize'

defaultConfig = {
    'stepSize' : 10
}

availableMetrics = [
    MetricGraphSize(),
]

class Analyser:
    def initAnalysis(self, graph, metrics = availableMetrics, config = defaultConfig):
        self.metrics = metrics
        self.config = config
        self.results = {metric.getMetricName():[] for metric in metrics}
        self.results['version'] = []

    def _calcMetrics(self, graph):
        self.results['version'].append(graph.graph[Graph.KEY_VERSION])
        for metric in self.metrics:
            self.results[metric.getMetricName()].append(metric.calculate(graph))

    def onNewVersion(self, graph):
        if graph.graph[Graph.KEY_VERSION] % self.config['stepSize'] < 1e5:
            self._calcMetrics(graph)

    def finishAnalysis(self, graph):
        if self.results['version'][-1] != graph.graph[Graph.KEY_VERSION]:
            self._calcMetrics(graph)

        # ToDo: export this to a viewer module
        import matplotlib.pyplot as plt
        for metric in self.metrics:
            plt.figure()
            plt.plot(self.results['version'], self.results[metric.getMetricName()]) # ToDo configurable plot type
            plt.title(metric.getMetricName())
            plt.xlabel('version')
            plt.ylabel('ToDo: get from metric') # ToDO

        plt.show()



class ConvergensChecker:

    def __init__(self,settings=None ):
       self.number_of_iterations = settings["Convergens_Checker"]["numberOfIterations"]
       self.metrics_with_limits = {}
       self.addLimits(settings["Convergens_Checker"]["Metrics"])
       self.prozentualeAbweichung = float(settings["Convergens_Checker"]["drift"])


    def addLimits(self,limits):
        for metric in limits:
            self.metrics_with_limits[metric] = int(limits[metric])



    def converges(self, metrics_with_values = {} ):

        result = {}
        for metric in metrics_with_values:
            if metric in self.metrics_with_limits:

                if len(metrics_with_values[metric]) >= self.number_of_iterations:
                    last_values = metrics_with_values[metric][-self.number_of_iterations:-1]
                else:
                    return False

                compareValue = self.metrics_with_limits[metric]
                drift = compareValue*self.prozentualeAbweichung
                compareValueMin = compareValue - drift
                compareValueMax = compareValue + drift
                # Von Stackoverflow eine Idee eine Liste auf Sortierung zu prüfen: all(l[i] <= l[i+1] for i in xrange(len(l)-1))
                result[metric] = all((last_values[i])>= compareValueMin and last_values[i]<= compareValueMax for i in range(len(last_values)))
                if not result[metric]: return False

        return True

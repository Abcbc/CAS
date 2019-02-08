'''
Collection of plot routines.
Developed on the way, not consolidated yet.
ToDo: extract common functionality (data reading and structuring)
ToDo: adapt naming and layout in the different functions
'''

import csv
import numpy as np
import matplotlib.pyplot as plt

import utils.ConfigLoader as cnf

def toStr(var):
    if type(var) == float:
        return '{:1.1f}'.format(var)
    else:
        return '{}'.format(var)

def do_matrix_plot(sim_dir, param_name_x, param_name_y, metric_name_z, metric2Scalar, fixedItParamIndices, file_prefix='', add_info=''):
    import os
    contents = os.scandir(sim_dir)
    step_dirs = [entry.name for entry in contents if entry.is_dir()]
    import re
    dir_regex = re.compile('^\d+$')
    step_dirs = [candidate for candidate in step_dirs if dir_regex.fullmatch(candidate)]

    settings = []
    metric_names2ind = {}
    metric_means = []
    metric_stds = []
    for step_dir in step_dirs:
        settings.append(cnf.load_config(sim_dir+step_dir + '/settings.yaml'))
        reader_means = csv.reader(open(sim_dir+step_dir + '/metrics_mean.csv'))
        reader_stds = csv.reader(open(sim_dir+step_dir + '/metrics_std.csv'))
        metric_names = next(reader_means)
        next(reader_stds)
        metric_names2ind = {name:ind for ind, name in enumerate(metric_names)}
        step_means = [[] for _ in metric_names]
        step_stds = [[] for _ in metric_names]
        for row in reader_means:
            for i, name in enumerate(metric_names):
                if not name.startswith('Histogram') and name !='Communities':
                    step_means[i].append(float(row[i]))
        for row in reader_stds:
            for i, name in enumerate(metric_names):
                if not name.startswith('Histogram') and name !='Communities':
                    step_stds[i].append(float(row[i]))
        metric_means.append(step_means)
        metric_stds.append(step_stds)

    step_dirs = [int(step_dir) for step_dir in step_dirs]
    order = np.argsort(step_dirs)

    metric_scalar = []
    for i in range(len(metric_means)):
        metric_scalar.append(metric2Scalar(metric_means[i], metric_stds[i], metric_names2ind))

    sim_conf = cnf.load_config(sim_dir+'settings.yaml')[0]
    it_info = cnf.get_iterators_info(sim_conf)
    xName = param_name_x
    xStep = next(it_inf for it_inf in it_info if it_inf[0]==param_name_x)[1]['step']
    xSteps = next(it_inf for it_inf in it_info if it_inf[0]==param_name_x)[1]['length']
    yName = param_name_y
    yStep = next(it_inf for it_inf in it_info if it_inf[0]==param_name_y)[1]['step']
    ySteps = next(it_inf for it_inf in it_info if it_inf[0]==param_name_y)[1]['length']

    def getInd(xInd,yInd):
        factor = 1
        ind = 0
        indices = fixedItParamIndices.copy()
        indices.update({param_name_x:xInd, param_name_y:yInd})
        for i in range(len(it_info)-1, -1, -1):
            ind += factor * indices[it_info[i][0]]
            factor *= it_info[i][1]['length']
        return ind

    conf = cnf.load_config(sim_dir+str(getInd(0,0))+'/settings.yaml')[0]
    name = '{}{}-vs-{}-{}BA-m-{}'.format(file_prefix,metric_name_z,param_name_x,param_name_y,conf['graph_barabasi_albert_n-conn'])

    x = np.ones((ySteps+1,xSteps+1))
    y = np.ones((ySteps+1,xSteps+1))
    c = np.ones((ySteps,xSteps))

    lines = []
    conf = cnf.load_config(sim_dir+str(getInd(0,0))+'/settings.yaml')[0]
    lines.append('x: {}, y: {}, values: {}; {} {} m {}\n'.format(xName,yName,metric_name_z,conf['graph_type'],conf['graph_num_of_nodes'],conf['graph_barabasi_albert_n-conn']))
    for indY in range(0,ySteps):
        for indX in range(0,xSteps):
            ind = getInd(indX,indY)
            conf = cnf.load_config(sim_dir+str(ind)+'/settings.yaml')[0]
            c[indY,indX] = metric_scalar[order[ind]]
            lines.append('({},{})[{}]\n'.format(conf[xName],conf[yName],c[indY,indX]))
        lines.append('\n')
    with open(name+'.dat','w') as f:
        f.write('For pgf matrix plot. Copy data below into tex file\n')
        f.write(add_info+'\n')
        f.writelines(lines)


    conf = cnf.load_config(sim_dir+str(getInd(0,0))+'/settings.yaml')[0]
    xstart = conf[param_name_x]
    ystart = conf[param_name_y]
    for indY in range(ySteps+1):
        for indX in range(xSteps+1):
            x[indY,indX] = xstart+indX*xStep - xStep/2
            y[indY,indX] = ystart+indY*yStep - yStep/2

    plt.figure()
    plt.pcolormesh(x,y,c)
    plt.colorbar()
    plt.xlabel(xName)
    plt.ylabel(yName)
    plt.title(metric_name_z)
    plt.savefig(name+'.png')

# ToDo: make in_plot_param_name, subplot_param_name optional
def do_time_plot(sim_dir, metric_name_y, fixedItParamIndices, in_plot_param_name, subplot_param_name, file_prefix='', add_info=''):
    import os
    contents = os.scandir(sim_dir)
    step_dirs = [entry.name for entry in contents if entry.is_dir()]
    import re
    dir_regex = re.compile('^\d+$')
    step_dirs = [candidate for candidate in step_dirs if dir_regex.fullmatch(candidate)]

    settings = []
    metric_names2ind = {}
    metric_means = []
    metric_stds = []
    for step_dir in step_dirs:
        settings.append(cnf.load_config(sim_dir+step_dir + '/settings.yaml'))
        reader_means = csv.reader(open(sim_dir+step_dir + '/metrics_mean.csv'))
        reader_stds = csv.reader(open(sim_dir+step_dir + '/metrics_std.csv'))
        metric_names = next(reader_means)
        next(reader_stds)
        metric_names2ind = {name:ind for ind, name in enumerate(metric_names)}
        step_means = [[] for _ in metric_names]
        step_stds = [[] for _ in metric_names]
        for row in reader_means:
            for i, name in enumerate(metric_names):
                if not name.startswith('Histogram') and name !='Communities':
                    step_means[i].append(float(row[i]))
        for row in reader_stds:
            for i, name in enumerate(metric_names):
                if not name.startswith('Histogram') and name !='Communities':
                    step_stds[i].append(float(row[i]))
        metric_means.append(step_means)
        metric_stds.append(step_stds)

    step_dirs = [int(step_dir) for step_dir in step_dirs]
    order = np.argsort(step_dirs)

    sim_conf = cnf.load_config(sim_dir+'settings.yaml')[0]
    it_info = cnf.get_iterators_info(sim_conf)
    def getInd(inPlotInd,subPlotInd):
        factor = 1
        ind = 0
        indices = fixedItParamIndices.copy()
        if in_plot_param_name is not None:
            indices[in_plot_param_name] = inPlotInd
        if subplot_param_name is not None:
            indices[subplot_param_name] = subPlotInd
        for i in range(len(it_info)-1, -1, -1):
            ind += factor * indices[it_info[i][0]]
            factor *= it_info[i][1]['length']
        return ind

    subplot_len = next(it_inf for it_inf in it_info if it_inf[0]==subplot_param_name)[1]['length'] if subplot_param_name is not None else 1
    in_plot_len = next(it_inf for it_inf in it_info if it_inf[0]==in_plot_param_name)[1]['length'] if in_plot_param_name is not None else 1
    for indSubPlot in range(0,subplot_len):
        ind = getInd(0,indSubPlot)
        conf = cnf.load_config(sim_dir+str(ind)+'/settings.yaml')[0]
        fixedItParamDesc = ['-{}-{}'.format(name,conf[name]) for name, ind in fixedItParamIndices.items()]
        fixedItParamDesc = ''.join(fixedItParamDesc)
        name = '{}-{}-vs-Version-{}-{}-BA-m-{}'.format(file_prefix,metric_name_y,subplot_param_name,toStr(conf[subplot_param_name]),conf['graph_barabasi_albert_n-conn']) if subplot_param_name is not None else \
            '{}-{}-vs-Version-BA-m-{}'.format(file_prefix,metric_name_y,conf['graph_barabasi_albert_n-conn'])
        name += fixedItParamDesc

        plt.figure()
        for indInPlot in range(0,in_plot_len):
            ind = getInd(indInPlot,indSubPlot)
            conf = cnf.load_config(sim_dir+str(ind)+'/settings.yaml')[0]

            mean = metric_means[order[ind]]
            std = metric_stds[order[ind]]
            mean_data = mean[metric_names2ind[metric_name_y]]
            error_upper_limit = [_mean + _std for _mean, _std in zip(mean[metric_names2ind[metric_name_y]],std[metric_names2ind[metric_name_y]])]
            error_lower_limit = [_mean - _std for _mean, _std in zip(mean[metric_names2ind[metric_name_y]],std[metric_names2ind[metric_name_y]])]
            version = mean[metric_names2ind['Version']]
            meanPlt = plt.plot(version, mean_data,'-',label='{}={}'.format(in_plot_param_name, toStr(conf[in_plot_param_name]))) if in_plot_param_name is not None else \
                plt.plot(version, mean_data,'-')
            col = meanPlt[0].get_color()
            plt.plot(version, error_upper_limit,'-', color=col, linestyle='--')
            plt.plot(version, error_lower_limit,'-', color=col, linestyle='--')
            fname = (name+'-{}-{}'.format(in_plot_param_name,toStr(conf[in_plot_param_name]))) if in_plot_param_name is not None else name
            fname = fname.replace('.','') # pgfplots requirement no . before .csv
            with open(fname+'.csv','w') as f:
                writer = csv.writer(f)
                writer.writerow(['use with pgfplots: col sep=comma, skip first n=3 (or >3, depending on additional info'])
                writer.writerow(['combined data from {} repetitions. errL and errH are +- 1 sigma.'.format(conf['sim_repetitions'])])
                writer.writerow(['Comment: graph type {}, {} nodes. y axis {}'.format(conf['graph_type'],conf['graph_num_of_nodes'],metric_name_y)+'. This graph shows how '+metric_name_y+' changes.'])
                writer.writerow([add_info])
                writer.writerow(['version','mean','errL','errH'])
                for row in zip(version, mean_data, error_lower_limit, error_upper_limit):
                    writer.writerow(row)
        plt.xlabel('version')
        plt.ylabel(metric_name_y)
        plt.title('{} bei BA m={:1.1f}, {} {}'.format(metric_name_y,conf['graph_barabasi_albert_n-conn'],subplot_param_name,toStr(conf[subplot_param_name])) if subplot_param_name is not None else \
                  '{} bei BA m={:1.1f}'.format(metric_name_y,conf['graph_barabasi_albert_n-conn']))
        plt.legend(loc='upper left')
        plt.savefig(name+'.png')

# version is not version, but version's index. Look at the analyzers setting to relate
def do_histogram_plot(sim_dir, metric_name, version_ind, fixedItParamIndices, subplot_param_name, file_prefix='', add_info=''):
    import os
    contents = os.scandir(sim_dir)
    step_dirs = [entry.name for entry in contents if entry.is_dir()]
    import re
    dir_regex = re.compile('^\d+$')
    step_dirs = [candidate for candidate in step_dirs if dir_regex.fullmatch(candidate)]

    settings = []
    metric_names2ind = {}
    metric_hists = []
    metric_bins = []
    metric_versions = []
    for step_dir in step_dirs:
        settings.append(cnf.load_config(sim_dir+step_dir + '/settings.yaml'))
        reader_means = csv.reader(open(sim_dir+step_dir + '/metrics_mean.csv'))
        reader_stds = csv.reader(open(sim_dir+step_dir + '/metrics_std.csv'))
        metric_names = next(reader_means)
        next(reader_stds)
        metric_names2ind = {name:ind for ind, name in enumerate(metric_names)}
        step_hists = []
        step_bins = []
        step_versions = []
        for row in reader_means:
            for i, name in enumerate(metric_names):
                if name.startswith('Histogram'):
                    from numpy import array # for eval
                    step_hists.append(eval(row[i])[0])
                    step_bins.append(eval(row[i])[1])
                if name == 'Version':
                    step_versions.append(row[i])
        metric_hists.append(step_hists)
        metric_bins.append(step_bins)
        metric_versions.append(step_versions)

    step_dirs = [int(step_dir) for step_dir in step_dirs]
    order = np.argsort(step_dirs)

    sim_conf = cnf.load_config(sim_dir+'settings.yaml')[0]
    it_info = cnf.get_iterators_info(sim_conf)
    def getInd(subPlotInd):
        factor = 1
        ind = 0
        indices = fixedItParamIndices.copy()
        if subplot_param_name is not None:
            indices.update({subplot_param_name:subPlotInd})
        for i in range(len(it_info)-1, -1, -1):
            ind += factor * indices[it_info[i][0]]
            factor *= it_info[i][1]['length']
        return ind

    subplot_len = next(it_inf for it_inf in it_info if it_inf[0]==subplot_param_name)[1]['length'] if subplot_param_name is not None else 1
    for indSubPlot in range(0,subplot_len):
        ind = getInd(indSubPlot)
        conf = cnf.load_config(sim_dir+str(ind)+'/settings.yaml')[0]
        name = '{}-{}-{}-{}-BA-m-{}'.format(file_prefix,metric_name,subplot_param_name,toStr(conf[subplot_param_name]),conf['graph_barabasi_albert_n-conn']) if subplot_param_name is not None else \
            '{}-{}-BA-m-{}'.format(file_prefix,metric_name,conf['graph_barabasi_albert_n-conn'])

        version = metric_versions[metric_names2ind['Version']][version_ind]

        plt.figure()
        ind = getInd(indSubPlot)
        conf = cnf.load_config(sim_dir+str(ind)+'/settings.yaml')[0]

        hist = metric_hists[order[ind]][version_ind]
        bins = metric_bins[order[ind]][version_ind]
        bin_width = bins[1]-bins[0]

        plt.bar(bins[:-1],hist,width=bin_width,align='edge')

        fname = name
        fname = fname.replace('.','') # pgfplots requirement no . before .csv
        with open(fname+'.csv','w') as f:
            writer = csv.writer(f)
            writer.writerow(['use with pgfplots: col sep=comma, skip first n=3 (or >3, depending on additional info, plot with \\addplot[ybar=0pt,fill,bar width=0.2] table [x=xcenter,y=y] {\\table};'])
            writer.writerow(['combined data from {} repetitions'.format(conf['sim_repetitions'])])
            writer.writerow(['Comment: graph type {}, {} nodes. histogram of {}, version {}.'.format(conf['graph_type'],conf['graph_num_of_nodes'],metric_name, version)])
            writer.writerow([add_info])
            writer.writerow(['xmin','xmax','xcenter','xwidth','y'])
            for i in range(len(hist)):
                xmin = bins[i]
                xmax = bins[i+1]
                xcenter = bins[i]+bin_width/2
                y = hist[i]
                writer.writerow([xmin, xmax,xcenter,bin_width,y])
        plt.xlabel(metric_name)
        plt.ylabel('Number of occurrences')
        plt.title('Histogramm {} bei BA m={:1.1f}, v {}, {} {}'.format(metric_name,conf['graph_barabasi_albert_n-conn'],version,subplot_param_name,toStr(conf[subplot_param_name])) if subplot_param_name is not None else \
                  'Histogramm {} bei BA m={:1.1f}, v {}'.format(metric_name,conf['graph_barabasi_albert_n-conn'],version))
        plt.legend(loc='upper left')
        plt.savefig(name+'.png')

def do_histogram_props_plot(sim_dir, metric_name, fixedItParamIndices, subplot_param_name, file_prefix='', add_info=''):
    import os
    contents = os.scandir(sim_dir)
    step_dirs = [entry.name for entry in contents if entry.is_dir()]
    import re
    dir_regex = re.compile('^\d+$')
    step_dirs = [candidate for candidate in step_dirs if dir_regex.fullmatch(candidate)]

    settings = []
    metric_names2ind = {}
    metric_hists = []
    metric_bins = []
    metric_versions = []
    for step_dir in step_dirs:
        settings.append(cnf.load_config(sim_dir+step_dir + '/settings.yaml'))
        reader_means = csv.reader(open(sim_dir+step_dir + '/metrics_mean.csv'))
        reader_stds = csv.reader(open(sim_dir+step_dir + '/metrics_std.csv'))
        metric_names = next(reader_means)
        next(reader_stds)
        metric_names2ind = {name:ind for ind, name in enumerate(metric_names)}
        step_hists = []
        step_bins = []
        step_versions = []
        for row in reader_means:
            for i, name in enumerate(metric_names):
                if name.startswith('Histogram'):
                    from numpy import array # for eval
                    step_hists.append(eval(row[i])[0])
                    step_bins.append(eval(row[i])[1])
                if name == 'Version':
                    step_versions.append(row[i])
        metric_hists.append(step_hists)
        metric_bins.append(step_bins)
        metric_versions.append(step_versions)

    step_dirs = [int(step_dir) for step_dir in step_dirs]
    order = np.argsort(step_dirs)

    sim_conf = cnf.load_config(sim_dir+'settings.yaml')[0]
    it_info = cnf.get_iterators_info(sim_conf)
    def getInd(subPlotInd):
        factor = 1
        ind = 0
        indices = fixedItParamIndices.copy()
        if subplot_param_name is not None:
            indices.update({subplot_param_name:subPlotInd})
        for i in range(len(it_info)-1, -1, -1):
            ind += factor * indices[it_info[i][0]]
            factor *= it_info[i][1]['length']
        return ind

    subplot_len = next(it_inf for it_inf in it_info if it_inf[0]==subplot_param_name)[1]['length'] if subplot_param_name is not None else 1
    for indSubPlot in range(0,subplot_len):
        ind = getInd(indSubPlot)
        conf = cnf.load_config(sim_dir+str(ind)+'/settings.yaml')[0]
        name = '{}-{}-{}-{}'.format(file_prefix,metric_name,subplot_param_name,toStr(conf[subplot_param_name])) if subplot_param_name is not None else \
            '{}-{}'.format(file_prefix,metric_name)
        fixedItParamDesc = ['-{}-{}'.format(name,conf[name]) for name, ind in fixedItParamIndices.items()]
        fixedItParamDesc = ''.join(fixedItParamDesc)
        name += fixedItParamDesc

        plt.figure()
        ind = getInd(indSubPlot)
        conf = cnf.load_config(sim_dir+str(ind)+'/settings.yaml')[0]

        means = []
        stds = []
        version = [int(v_str) for v_str in metric_versions[order[ind]]]
        for v_ind in range(len(metric_hists[order[ind]])):
            hist = metric_hists[order[ind]][v_ind]
            bins = metric_bins[order[ind]][v_ind]
            bin_width = bins[1]-bins[0]
            mean = np.sum([h*(b+bin_width/2) for h,b in zip(hist,bins)])/np.sum(hist)
            std = np.sqrt(np.sum([h*pow(b+bin_width/2-mean,2) for h,b in zip(hist,bins)])/np.sum(hist))
            means.append(mean)
            stds.append(std)

        plt.scatter(means,stds,c=version)
        plt.title('{}-{}-{}'.format(metric_name,subplot_param_name,toStr(conf[subplot_param_name])) if subplot_param_name is not None else \
                  '{}'.format(metric_name))
        plt.xlabel('mean')
        plt.ylabel('std')
        plt.colorbar()

        fname = name
        fname = fname.replace('.','') # pgfplots requirement no . before .csv
        with open(fname+'.csv','w') as f:
            writer = csv.writer(f)
            # writer.writerow(['use with pgfplots: col sep=comma, skip first n=3 (or >3, depending on additional info, plot with \\addplot[ybar=0pt,fill,bar width=0.2] table [x=xcenter,y=y] {\\table};'])
            # writer.writerow(['combined data from {} repetitions'.format(conf['sim_repetitions'])])
            # writer.writerow(['Comment: graph type {}, {} nodes. histogram of {}, version {}.'.format(conf['graph_type'],conf['graph_num_of_nodes'],metric_name, version)])
            # writer.writerow([add_info])
            writer.writerow(['version','mean','std'])
            for i in range(len(version)):
                writer.writerow([version[i], means[i], stds[i]])
        plt.savefig(name+'.png')

def do_communities_plot(sim_dir, fixedItParamIndices, subplot_param_name, file_prefix='', add_info=''):
    import os
    contents = os.scandir(sim_dir)
    step_dirs = [entry.name for entry in contents if entry.is_dir()]
    import re
    dir_regex = re.compile('^\d+$')
    step_dirs = [candidate for candidate in step_dirs if dir_regex.fullmatch(candidate)]

    settings = []
    metric_names2ind = {}
    metric_means = []
    commss = []
    mods = []
    for step_dir in step_dirs:
        settings.append(cnf.load_config(sim_dir+step_dir + '/settings.yaml'))
        reader_means = csv.reader(open(sim_dir+step_dir + '/metrics_mean.csv'))
        reader_stds = csv.reader(open(sim_dir+step_dir + '/metrics_std.csv'))
        metric_names = next(reader_means)
        next(reader_stds)
        metric_names2ind = {name:ind for ind, name in enumerate(metric_names)}
        step_means = [[] for _ in metric_names]
        step_comms = []
        step_mods = []
        for row in reader_means:
            for i, name in enumerate(metric_names):
                if not name.startswith('Histogram') and name !='Communities':
                    step_means[i].append(float(row[i]))
                if name == 'Communities':
                    step_comms.append(eval(row[i])[0])
                    step_mods.append(eval(row[i])[1])
        metric_means.append(step_means)
        commss.append(step_comms)
        mods.append(step_mods)

    step_dirs = [int(step_dir) for step_dir in step_dirs]
    order = np.argsort(step_dirs)

    sim_conf = cnf.load_config(sim_dir+'settings.yaml')[0]
    it_info = cnf.get_iterators_info(sim_conf)
    def getInd(subPlotInd):
        factor = 1
        ind = 0
        indices = fixedItParamIndices.copy()
        if subplot_param_name is not None:
            indices.update({subplot_param_name:subPlotInd})
        for i in range(len(it_info)-1, -1, -1):
            ind += factor * indices[it_info[i][0]]
            factor *= it_info[i][1]['length']
        return ind

    subplot_len = next(it_inf for it_inf in it_info if it_inf[0]==subplot_param_name)[1]['length'] if subplot_param_name is not None else 1
    for indSubPlot in range(0,subplot_len):
        ind = getInd(indSubPlot)
        conf = cnf.load_config(sim_dir+str(ind)+'/settings.yaml')[0]
        fixedItParamDesc = ['-{}-{}'.format(name,conf[name]) for name, ind in fixedItParamIndices.items()]
        fixedItParamDesc = ''.join(fixedItParamDesc)

        plt.figure()
        ind = getInd(indSubPlot)
        conf = cnf.load_config(sim_dir+str(ind)+'/settings.yaml')[0]

        # print(ind)
        # print(order[ind])
        # print(metric_means)
        mean = metric_means[order[ind]]
        comms = commss[order[ind]]
        mods_ = mods[order[ind]]
        version = mean[metric_names2ind['Version']]
        # print(comms)

        base = [0] * len(version)
        maxComms = max([len(comm) for comm in comms])
        for i in range(maxComms):
            for comm in comms:
                while len(comm) < maxComms:
                    comm.append(0)
            c = [comm[i] for comm in comms]
            plt.bar(version,c, bottom=base)
            base = [b+c_ for b,c_ in zip(base,c)]


        name = '{}-{}-vs-Version-{}-{}-BA-m-{}'.format(file_prefix,'Modularity',subplot_param_name,toStr(conf[subplot_param_name]),conf['graph_barabasi_albert_n-conn']) if subplot_param_name is not None else \
            '{}-{}-vs-Version-BA-m-{}'.format(file_prefix,'Modularity',conf['graph_barabasi_albert_n-conn'])
        name += fixedItParamDesc
        fname = name
        fname = fname.replace('.','') # pgfplots requirement no . before .csv
        with open(fname+'.csv','w') as f:
            writer = csv.writer(f)
            writer.writerow(['use with pgfplots: col sep=comma, skip first n=3 (or >3, depending on additional info'])
            writer.writerow(['combined data from {} repetitions. errL and errH are +- 1 sigma.'.format(conf['sim_repetitions'])])
            writer.writerow(['Comment: graph type {}, {} nodes. y axis {}'.format(conf['graph_type'],conf['graph_num_of_nodes'],'Modularity')+'. This graph shows how '+'Modularity'+' changes. The nodes have {} opinions'.format(conf['opinions_number_of_topics'])])
            writer.writerow([add_info])
            writer.writerow(['version','mean','errL','errH'])
            for row in zip(version, mods_):
                writer.writerow(row)
        plt.xlabel('version')
        plt.ylabel('size')
        # plt.title('{} bei BA m={:1.1f}, {} {}'.format(metric_name_y,conf['graph_barabasi_albert_n-conn'],subplot_param_name,toStr(conf[subplot_param_name])))
        # plt.savefig(name+'.png')
        plt.figure()

        plt.plot(version, mods_)
        plt.title('modularity')
        plt.xlabel('Version')

if __name__ == '__main__':
    # def makeSafeForDiv(x):
    #     return x if x != 0 else x+1e-9
    # def getMetricSlope(version, metric_mean, metric_std):
    #     return np.polyfit(x=version,y=metric_mean,deg=1,w=[1/(makeSafeForDiv(sig)) for sig in metric_std])[0]
    # def getLastValue(version, metric_mean, metric_std):
    #     return metric_mean[-1]
    # do_matrix_plot('experiment/BA_diff_rer/', 'opinions_pos_ratio', 'RemoveEdgeRule_absOrientationThreshold', 'NumberOfEdges',
    #                lambda metric_mean, metric_std, metric_names2ind: getLastValue(metric_mean[metric_names2ind['Version']],metric_mean[metric_names2ind['NumberOfEdges']],metric_std[metric_names2ind['NumberOfEdges']]),
    #                {'graph_barabasi_albert_n-conn':3}, file_prefix='Verification-RER-',add_info='BA(50,20), only Remove Edges Rule')

    dir = 'experiment2000/twoCentresPeriph/'


    ##################
    fixed_inds = {
        'graph_barabasi_albert_n-conn':1,
        # 'graph_type':0,
    }
    full_fixed_inds = fixed_inds.copy()
    full_fixed_inds.update({
        # 'opinions_center_choicemode':1,
        # 'graph_inter_cluster_connections':1
    })

    subplot_param_name = None#'graph_inter_cluster_connections'
    in_plot_param_name = None#'opinions_center_choicemode'
    do_communities_plot(dir,full_fixed_inds,subplot_param_name=subplot_param_name,file_prefix='Model',add_info='')
    do_time_plot(dir,'OpinionConsensusAll',fixed_inds, in_plot_param_name=in_plot_param_name,subplot_param_name=subplot_param_name, file_prefix='Model', add_info='')
    do_time_plot(dir,'GraphSize',fixed_inds, in_plot_param_name=in_plot_param_name,subplot_param_name=subplot_param_name, file_prefix='Model', add_info='')
    do_time_plot(dir,'NumberOfEdges',fixed_inds, in_plot_param_name=in_plot_param_name,subplot_param_name=subplot_param_name, file_prefix='Model', add_info='')
    do_time_plot(dir,'OpinionStrengthAll',fixed_inds, in_plot_param_name=in_plot_param_name,subplot_param_name=subplot_param_name, file_prefix='Model', add_info='')
    do_time_plot(dir,'NumberOfClusters',fixed_inds, in_plot_param_name=in_plot_param_name,subplot_param_name=subplot_param_name, file_prefix='Model', add_info='')
    do_time_plot(dir,'Density',fixed_inds, in_plot_param_name=in_plot_param_name,subplot_param_name=subplot_param_name, file_prefix='Model', add_info='')
    do_time_plot(dir,'AverageClustering',fixed_inds, in_plot_param_name=in_plot_param_name,subplot_param_name=subplot_param_name, file_prefix='Model', add_info='')
    do_time_plot(dir,'MeanOrientation',fixed_inds, in_plot_param_name=in_plot_param_name,subplot_param_name=subplot_param_name, file_prefix='Model', add_info='')
    do_time_plot(dir,'Connectedness',fixed_inds, in_plot_param_name=in_plot_param_name,subplot_param_name=subplot_param_name, file_prefix='Model', add_info='')
    do_histogram_plot(dir,'HistogramV',0,full_fixed_inds,subplot_param_name,'Model','')
    # do_histogram_plot(dir,'HistogramV',50,full_fixed_inds,None,'Model','')
    # do_histogram_plot(dir,'HistogramV',100,full_fixed_inds,None,'Model','')
    do_histogram_plot(dir,'HistogramDegree',0,full_fixed_inds,subplot_param_name,'Model','')
    # do_histogram_plot(dir,'HistogramDegree',50,full_fixed_inds,None,'Model','')
    # do_histogram_plot(dir,'HistogramDegree',100,full_fixed_inds,None,'Model','')
    do_histogram_props_plot(dir,'HistogramDegree',full_fixed_inds,subplot_param_name,'Model','')
    do_time_plot(dir,'MeanDegree',fixed_inds, in_plot_param_name=in_plot_param_name,subplot_param_name=subplot_param_name, file_prefix='Model', add_info='')
    do_time_plot(dir,'StdDegree',fixed_inds, in_plot_param_name=in_plot_param_name,subplot_param_name=subplot_param_name, file_prefix='Model', add_info='')
